"""
RoadSense - central configuration.

Everything you might need to tune or change lives here, in one place,
so you never have to go hunting through multiple files.
"""

# ---------------------------------------------------------------------------
# Serial link to the ESP8266 (connected via USB to the Pi)
# ---------------------------------------------------------------------------
# Run `ls /dev/tty*` with the ESP8266 UNPLUGGED, then again with it PLUGGED IN.
# The new entry that appears (usually /dev/ttyUSB0 or /dev/ttyACM0) is your port.
#
# This ONE serial link now carries everything: buzzer commands going out,
# and GPS NMEA sentences coming in - the GPS module is wired to the ESP8266
# (D2), not the Pi anymore, and the ESP8266 forwards raw GPS bytes over this
# same USB cable. There is no separate GPS_SERIAL_PORT any more - gps_sensor.py
# reads GPS lines through esp32_link/serial_link.py instead of opening its
# own port. Don't wire a GPS module directly to the Pi while this is active.
ESP8266_PORT = "/dev/ttyUSB0"
ESP32_BAUD_RATE = 115200

# ---------------------------------------------------------------------------
# Ultrasonic sensor (HC-SR04) - BCM pin numbers
# ---------------------------------------------------------------------------
ULTRASONIC_TRIGGER_PIN = 23
ULTRASONIC_ECHO_PIN = 24
ULTRASONIC_NEAR_MISS_CM = 60   # distance below this counts as "something close"

# ---------------------------------------------------------------------------
# MPU6050 (accelerometer + gyroscope)
# ---------------------------------------------------------------------------
MPU6050_I2C_ADDRESS = 0x68
MPU6050_JERK_THRESHOLD = 5.0   # tune this by watching printed jerk values while testing

# ---------------------------------------------------------------------------
# Motor pins - same as your motor_test.py
# ---------------------------------------------------------------------------
MOTOR_IN1 = 17
MOTOR_IN2 = 27
MOTOR_IN3 = 22
MOTOR_IN4 = 25
AUTO_REVERSE_SECONDS = 2   # how long the car reverses for when a near-miss is confirmed

# ---------------------------------------------------------------------------
# Camera / object classification
# ---------------------------------------------------------------------------
# This is OPTIONAL. If the model files below aren't present, the camera will
# simply report "unknown" and the rest of the system still works fine using
# just the IMU + ultrasonic sensors. See README.md if you want to add this later.
USE_OBJECT_DETECTION_MODEL = True
MODEL_PROTOTXT = "models/MobileNetSSD_deploy.prototxt"
MODEL_WEIGHTS = "models/MobileNetSSD_deploy.caffemodel"
DETECTION_CONFIDENCE = 0.2

# ---------------------------------------------------------------------------
# Local storage
# ---------------------------------------------------------------------------
DB_PATH = "data/events.db"

# ---------------------------------------------------------------------------
# Backend server (not needed yet - flip SEND_TO_BACKEND on once your
# Node/Express server is running)
# ---------------------------------------------------------------------------
BACKEND_URL = "http://13.203.205.175:5000/api/events"
SEND_TO_BACKEND = True
