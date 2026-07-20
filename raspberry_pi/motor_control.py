"""
Motor control - built directly on your motor_test.py, just wrapped into
reusable functions. Used to automatically reverse the car a short distance
when a near-miss is confirmed.
"""
from gpiozero import OutputDevice
import time
import config

in1 = OutputDevice(config.MOTOR_IN1)
in2 = OutputDevice(config.MOTOR_IN2)
in3 = OutputDevice(config.MOTOR_IN3)
in4 = OutputDevice(config.MOTOR_IN4)


def stop():
    in1.off()
    in2.off()
    in3.off()
    in4.off()


def forward():
    in1.on()
    in2.off()
    in3.on()
    in4.off()


def backward():
    in1.off()
    in2.on()
    in3.off()
    in4.on()


def auto_reverse():
    """The car's automatic reaction to a near-miss: reverse briefly, then stop."""
    print("[Motor] Near-miss confirmed - reversing")
    backward()
    time.sleep(config.AUTO_REVERSE_SECONDS)
    stop()
    print("[Motor] Stopped")
