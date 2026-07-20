"""
RoadSense - main loop.

Reads all sensors continuously, checks each reading against the near-miss
rulebook, and when a real near-miss is confirmed: logs it, sounds the
buzzer (via the ESP32), and reverses the car.

Run with:  python3 main.py
Stop with: Ctrl+C
"""
import time
import config
from sensors import imu_sensor, ultrasonic_sensor, gps_sensor, camera_sensor
from detection import near_miss_detector
from esp32_link import serial_link
from storage import event_logger
import motor_control

LOOP_DELAY_SECONDS = 0.2
COOLDOWN_AFTER_EVENT_SECONDS = 2  # stops one event from re-triggering repeatedly


def handle_near_miss(event):
    print("\n" + "=" * 50)
    print(f"NEAR-MISS DETECTED - severity {event['severity']}/5, cause: {event['object_class']}")
    print("=" * 50)
    event_logger.save_event(event)
    serial_link.trigger_buzzer()
    motor_control.auto_reverse()


def main():
    print("Starting RoadSense main loop... (Ctrl+C to stop)\n")
    event_logger.init_db()
    serial_link.connect()

    while True:
        try:
            imu_reading = imu_sensor.get_jerk()
            ultrasonic_close, distance_cm = ultrasonic_sensor.is_object_close()
            object_class, object_confidence = camera_sensor.classify_frame()
            location = gps_sensor.get_location()

            event = near_miss_detector.evaluate(
                imu_reading, ultrasonic_close, distance_cm,
                object_class, object_confidence, location,
            )

            if event:
                handle_near_miss(event)
                time.sleep(COOLDOWN_AFTER_EVENT_SECONDS)

            time.sleep(LOOP_DELAY_SECONDS)

        except KeyboardInterrupt:
            print("\nStopping RoadSense.")
            motor_control.stop()
            break
        except Exception as e:
            print(f"[Main] Unexpected error, continuing loop: {e}")
            time.sleep(1)


if __name__ == "__main__":
    main()
