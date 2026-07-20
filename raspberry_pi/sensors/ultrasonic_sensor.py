"""
HC-SR04 ultrasonic distance sensor.

Tells us whether something is dangerously close in front of the vehicle -
this is our "confirmation" signal alongside the camera.
"""
from gpiozero import DistanceSensor
import config

_sensor = DistanceSensor(
    echo=config.ULTRASONIC_ECHO_PIN,
    trigger=config.ULTRASONIC_TRIGGER_PIN,
    max_distance=3,  # metres
)


def get_distance_cm():
    """Returns distance to the nearest object in front, in centimetres."""
    return _sensor.distance * 100


def is_object_close():
    """Returns (True/False, distance_cm)."""
    distance = get_distance_cm()
    return distance <= config.ULTRASONIC_NEAR_MISS_CM, distance
