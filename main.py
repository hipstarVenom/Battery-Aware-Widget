import psutil
import time

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

def main():
    last_state = None

    while True:
        percent, charging = get_battery_info()

        state = "NO_BATTERY" if percent is None else percent_to_state(percent, charging)

        if state != last_state:
            print(f"STATE -> {state} ({percent}%)")
            last_state = state

        time.sleep(60)

if __name__ == "__main__":
    main()
