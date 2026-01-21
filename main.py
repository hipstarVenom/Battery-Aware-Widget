import psutil
import time
import json
from pathlib import Path

SKIN_DIR = Path("skins/pet_cat")
VARIANT = "cat_6"

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

def main():
    skin = load_skin()
    last_state = None

    while True:
        percent, charging = get_battery_info()
        state = "NO_BATTERY" if percent is None else percent_to_state(percent, charging)

        if state != last_state:
            animation = skin["base"].get(state)
            if animation:
                path = SKIN_DIR / VARIANT / f"{animation}.png"
                print(f"STATE -> {state} ({percent}%)")
                print(f"ANIMATION -> {path}")
            else:
                print(f"STATE -> {state} ({percent}%) (no animation)")

            last_state = state

        time.sleep(60)

if __name__ == "__main__":
    main()
