"""
Simulates a near-miss WITHOUT needing real sensor conditions - this lets you
test that logging + buzzer + motor reverse all work correctly on their own,
before you worry about getting the real sensor thresholds tuned.

Run with: python3 simulate_near_miss.py
"""
import time
from storage import event_logger
from esp32_link import serial_link
import motor_control


def main():
    print("Simulating a near-miss event...\n")
    event_logger.init_db()
    serial_link.connect()

    fake_event = {
        "timestamp": time.time(),
        "severity": 4,
        "object_class": "pedestrian",
        "distance_cm": 18.0,
        "jerk": 22.0,
        "location": None,
    }

    event_logger.save_event(fake_event)
    print("-> Event saved to local database (check data/events.db)")

    serial_link.trigger_buzzer()
    print("-> Buzzer command sent - you should hear a beep now")

    motor_control.auto_reverse()
    print("-> Motor reversed and stopped")

    print("\nSimulation complete. If you heard the buzzer and saw the car reverse, your pipeline works end-to-end.")


if __name__ == "__main__":
    main()
