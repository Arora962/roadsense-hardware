"""
RoadSense - central configuration.

Everything you might need to tune or change lives here, in one place,
so you never have to go hunting through multiple files.
"""

# ---------------------------------------------------------------------------
# Serial link to the ESP32 (connected via USB to the Pi)
# ---------------------------------------------------------------------------
# Run `ls /dev/tty*` with the ESP32 UNPLUGGED, then again with it PLUGGED IN.
# The new entry that appears (usually /dev/ttyUSB0 or /dev/ttyACM0) is your port.
ESP32_SERIAL_PORT = "/dev/ttyUSB0"
ESP32_BAUD_RATE = 115200

# ---------------------------------------------------------------------------
# GPS module
# ---------------------------------------------------------------------------
# If it's a USB GPS dongle: usually /dev/ttyUSB1 (check with `ls /dev/tty*` the
# same way as above, since the ESP32 will likely grab ttyUSB0 first).
# If it's wired directly to the Pi's GPIO UART pins: use "/dev/serial0" instead.
GPS_SERIAL_PORT = "/dev/serial0"
GPS_BAUD_RATE = 9600

# ---------------------------------------------------------------------------
# Ultrasonic sensor (HC-SR04) - BCM pin numbers
# ---------------------------------------------------------------------------
ULTRASONIC_TRIGGER_PIN = 24
ULTRASONIC_ECHO_PIN = 23
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
DETECTION_CONFIDENCE = 0.5

# ---------------------------------------------------------------------------
# Local storage
# ---------------------------------------------------------------------------
DB_PATH = "data/events.db"

# ---------------------------------------------------------------------------
# Backend server (not needed yet - flip SEND_TO_BACKEND on once your
# Node/Express server is running)
# ---------------------------------------------------------------------------
BACKEND_URL = "http://localhost:5000/api/events"
SEND_TO_BACKEND = False
