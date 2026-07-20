"""
MPU6050 accelerometer/gyroscope reader.

What this actually does: it compares each new reading to the previous one and
works out how sharply the acceleration changed (this is called "jerk"). A big,
sudden jerk means something abrupt just happened to the vehicle's motion -
hard braking, or a sharp swerve.
"""
from mpu6050 import mpu6050
import time
import config

sensor = mpu6050(config.MPU6050_I2C_ADDRESS)

_last_accel = None
_last_time = None


def read_raw():
    """Returns the current raw accelerometer (m/s^2) and gyro (deg/s) readings."""
    accel = sensor.get_accel_data()
    gyro = sensor.get_gyro_data()
    return accel, gyro


def get_jerk():
    """
    Reads the sensor and returns a dict describing whether a sudden motion
    spike just happened.
    """
    global _last_accel, _last_time

    accel, gyro = read_raw()
    now = time.time()

    magnitude = (accel["x"] ** 2 + accel["y"] ** 2 + accel["z"] ** 2) ** 0.5

    jerk = 0.0
    if _last_accel is not None and _last_time is not None:
        dt = max(now - _last_time, 0.001)
        prev_magnitude = (
            _last_accel["x"] ** 2 + _last_accel["y"] ** 2 + _last_accel["z"] ** 2
        ) ** 0.5
        jerk = abs(magnitude - prev_magnitude) / dt

    _last_accel = accel
    _last_time = now

    return {
        "accel": accel,
        "gyro": gyro,
        "magnitude": magnitude,
        "jerk": jerk,
        "is_spike": jerk > config.MPU6050_JERK_THRESHOLD,
    }
