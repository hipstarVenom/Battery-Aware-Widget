import psutil
import time
import json
import random
from pathlib import Path
import pygame as py

py.init()

# ---------------- PATHS ---------------- #

BASE_DIR = Path(__file__).parent
SKIN_DIR = BASE_DIR / "skins" / "pet_cat"
CONFIG_PATH = BASE_DIR / "config.json"

# ---------------- CONSTANTS ---------------- #

FRAME_SIZE = 50
SCALE = 2.0

MENU_SIZE = (360, 260)
PET_SIZE = (140, 140)

TRANSPARENT_COLOR = (255, 0, 255)  # magic pink
FPS_IDLE = 2

FONT = py.font.SysFont(None, 16)
HIGHLIGHT_COLOR = (255, 255, 0)

# ---------------- WINDOW POSITION HELPERS ---------------- #

def get_window_pos():
    try:
        return py.display.get_window_position()
    except:
        return None

def set_window_pos(pos):
    if pos:
        try:
            py.display.set_window_position(pos[0], pos[1])
        except:
            pass

# ---------------- CONFIG ---------------- #

def load_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    return {
        "selected_cat": "cat_1",
        "first_run": True
    }

def save_config(cat):
    with open(CONFIG_PATH, "w") as f:
        json.dump(
            {
                "selected_cat": cat,
                "first_run": False
            },
            f
        )

# ---------------- BATTERY ---------------- #

def percent_to_state(percent, charging):
    if charging:
        return "CHARGING"
    if percent >= 70:
        return "HIGH"
    if percent >= 40:
        return "MEDIUM"
    if percent >= 15:
        return "LOW"
    return "CRITICAL"

def get_battery_info():
    b = psutil.sensors_battery()
    if not b:
        return None, None
    return b.percent, b.power_plugged

# ---------------- ASSETS ---------------- #

def load_skin():
    with open(SKIN_DIR / "skin.json", "r") as f:
        return json.load(f)

def load_frames(path):
    sheet = py.image.load(path).convert_alpha()
    count = sheet.get_width() // FRAME_SIZE
    size = int(FRAME_SIZE * SCALE)

    frames = []
    for i in range(count):
        rect = py.Rect(i * FRAME_SIZE, 0, FRAME_SIZE, FRAME_SIZE)
        frame = sheet.subsurface(rect)
        frame = py.transform.smoothscale(frame, (size, size))
        frames.append(frame)
    return frames

def load_idle_frame(path):
    sheet = py.image.load(path).convert_alpha()
    rect = py.Rect(0, 0, FRAME_SIZE, FRAME_SIZE)
    frame = sheet.subsurface(rect)
    size = int(FRAME_SIZE * SCALE)
    return py.transform.smoothscale(frame, (size, size))

# ---------------- MENU ---------------- #

def select_cat_menu(window, initial_cat):
    clock = py.time.Clock()

    selected = int(initial_cat.split("_")[1])
    preview_frames = load_frames(SKIN_DIR / initial_cat / "run.png")
    preview_index = 0

    idle_frames = {
        i: load_idle_frame(SKIN_DIR / f"cat_{i}" / "idle.png")
        for i in range(1, 7)
    }

    positions = {
        1: py.Rect(30, 50, 100, 100),
        2: py.Rect(140, 50, 100, 100),
        3: py.Rect(250, 50, 100, 100),
        4: py.Rect(30, 150, 100, 100),
        5: py.Rect(140, 150, 100, 100),
        6: py.Rect(250, 150, 100, 100),
    }

    while True:
        for event in py.event.get():
            if event.type == py.QUIT:
                return None

            if event.type == py.MOUSEBUTTONDOWN:
                for i, rect in positions.items():
                    if rect.collidepoint(event.pos):
                        selected = i
                        preview_frames = load_frames(
                            SKIN_DIR / f"cat_{selected}" / "run.png"
                        )
                        preview_index = 0

            if event.type == py.KEYDOWN:
                if event.key == py.K_RETURN:
                    return f"cat_{selected}"
                if event.key == py.K_ESCAPE:
                    return None

        window.fill((70, 100, 130))
        title = FONT.render("Click Cat | ENTER Start | ESC Quit", True, (255, 255, 255))
        window.blit(title, (20, 15))

        for i, rect in positions.items():
            if i == selected:
                frame = preview_frames[preview_index]
                py.draw.rect(window, HIGHLIGHT_COLOR, rect.inflate(6, 6), 3)
            else:
                frame = idle_frames[i]

            x = rect.x + (rect.width - frame.get_width()) // 2
            y = rect.y + (rect.height - frame.get_height()) // 2
            window.blit(frame, (x, y))

        preview_index = (preview_index + 1) % len(preview_frames)
        py.display.flip()
        clock.tick(10)

# ---------------- PET MODE (WITH INTERACTION) ---------------- #

def run_pet(window, skin, variant):
    clock = py.time.Clock()

    last_state = None
    frames = []
    base_index = 0

    interaction_frames = None
    interaction_index = 0

    fps = FPS_IDLE
    last_battery_check = 0

    while True:
        for event in py.event.get():
            if event.type == py.QUIT:
                return "QUIT"

            if event.type == py.KEYDOWN and event.key == py.K_ESCAPE:
                return "MENU"

            if event.type == py.MOUSEBUTTONDOWN:
                if interaction_frames is None:
                    percent, charging = get_battery_info()
                    state = "LOW" if percent is None else percent_to_state(percent, charging)
                    tap_list = skin["tap"].get(state, [])
                    if tap_list:
                        anim = random.choice(tap_list)
                        interaction_frames = load_frames(
                            SKIN_DIR / variant / f"{anim}.png"
                        )
                        interaction_index = 0
                        fps = skin["fps"].get(state, 6)

        now = time.time()
        if now - last_battery_check >= 60 and interaction_frames is None:
            percent, charging = get_battery_info()
            state = "LOW" if percent is None else percent_to_state(percent, charging)
            last_battery_check = now

            if state != last_state:
                anim = skin["base"].get(state)
                fps = skin["fps"].get(state, FPS_IDLE)
                frames = load_frames(SKIN_DIR / variant / f"{anim}.png")
                base_index = 0
                last_state = state

        window.fill(TRANSPARENT_COLOR)

        if interaction_frames:
            if interaction_index >= len(interaction_frames):
                interaction_frames = None
                interaction_index = 0
            else:
                frame = interaction_frames[interaction_index]
                interaction_index += 1
        elif frames:
            if base_index >= len(frames):
                base_index = 0
            frame = frames[base_index]
            base_index += 1
        else:
            frame = None

        if frame:
            x = (PET_SIZE[0] - frame.get_width()) // 2
            y = (PET_SIZE[1] - frame.get_height()) // 2
            window.blit(frame, (x, y))

        py.display.update()
        clock.tick(fps if fps > 0 else FPS_IDLE)

# ---------------- APP ---------------- #

def main():
    skin = load_skin()
    config = load_config()
    current_cat = config["selected_cat"]

    if config["first_run"]:
        window = py.display.set_mode(MENU_SIZE)
        new_cat = select_cat_menu(window, current_cat)
        if not new_cat:
            py.quit()
            return
        current_cat = new_cat
        save_config(current_cat)

    window = py.display.set_mode(PET_SIZE, py.NOFRAME)
    window.set_colorkey(TRANSPARENT_COLOR)

    while True:
        result = run_pet(window, skin, current_cat)

        if result == "QUIT":
            break

        if result == "MENU":
            pos = get_window_pos()
            window = py.display.set_mode(MENU_SIZE)
            set_window_pos(pos)

            new_cat = select_cat_menu(window, current_cat)
            if not new_cat:
                break

            current_cat = new_cat
            save_config(current_cat)

            pos = get_window_pos()
            window = py.display.set_mode(PET_SIZE, py.NOFRAME)
            window.set_colorkey(TRANSPARENT_COLOR)
            set_window_pos(pos)

    py.quit()

if __name__ == "__main__":
    main()
