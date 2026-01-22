import psutil
import time
import json
from pathlib import Path
import pygame as py

py.init()

SKIN_DIR = Path("skins/pet_cat")
VARIANT = "cat_6"

FRAME_SIZE = 50
SCALE = 2.0

SCREEN_WIDTH, SCREEN_HEIGHT = 120, 120
window = py.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
py.display.set_caption("Battery Pet")

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
    battery = psutil.sensors_battery()
    if battery is None:
        return None, None
    return battery.percent, battery.power_plugged

def load_skin():
    with open(SKIN_DIR / "skin.json", "r") as f:
        return json.load(f)

def load_frames(path):
    sheet = py.image.load(path).convert_alpha()
    frame_count = sheet.get_width() // FRAME_SIZE
    scaled_size = int(FRAME_SIZE * SCALE)

    frames = []
    for i in range(frame_count):
        rect = py.Rect(i * FRAME_SIZE, 0, FRAME_SIZE, FRAME_SIZE)
        frame = sheet.subsurface(rect)
        frame = py.transform.smoothscale(frame, (scaled_size, scaled_size))
        frames.append(frame)

    return frames

def main():
    skin = load_skin()
    last_state = None

    frames = []
    frame_index = 0
    current_fps = 0

    clock = py.time.Clock()
    last_battery_check = 0

    running = True
    while running:
        for event in py.event.get():
            if event.type == py.QUIT:
                running = False

        now = time.time()
        if now - last_battery_check >= 60:
            percent, charging = get_battery_info()
            state = "NO_BATTERY" if percent is None else percent_to_state(percent, charging)
            last_battery_check = now

            if state != last_state:
                animation = skin["base"].get(state)
                current_fps = skin["fps"].get(state, 0)

                if animation:
                    path = SKIN_DIR / VARIANT / f"{animation}.png"
                    frames = load_frames(path)
                    frame_index = 0
                    print(f"STATE -> {state} | ANIMATION -> {path} | FPS -> {current_fps}")
                else:
                    frames = []

                last_state = state

        window.fill((0, 0, 0))

        if frames:
            frame = frames[frame_index]
            x = (SCREEN_WIDTH - frame.get_width()) // 2
            y = (SCREEN_HEIGHT - frame.get_height()) // 2
            window.blit(frame, (x, y))

            if current_fps > 0:
                frame_index = (frame_index + 1) % len(frames)

        py.display.flip()

        if current_fps > 0:
            clock.tick(current_fps)
        else:
            clock.tick(2)

    py.quit()

if __name__ == "__main__":
    main()
