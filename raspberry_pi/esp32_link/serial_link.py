"""
Sends commands to the ESP32 over the USB serial cable.

Right now the only command is "BUZZ", which tells the ESP32 to sound the
buzzer. The 8x8 matrix heartbeat animation runs entirely on the ESP32 itself
and doesn't need any commands from the Pi.
"""
import serial
import time
import config

_esp32 = None


def connect():
    global _esp32
    try:
        _esp32 = serial.Serial(config.ESP32_SERIAL_PORT, config.ESP32_BAUD_RATE, timeout=1)
        time.sleep(2)  # give the ESP32 a moment to reset after the port opens
        print(f"[ESP32] Connected on {config.ESP32_SERIAL_PORT}")
        return True
    except Exception as e:
        print(f"[ESP32] Could not connect on {config.ESP32_SERIAL_PORT}: {e}")
        print("[ESP32] Run `ls /dev/tty*` with it plugged/unplugged to find the right port, then update config.py")
        _esp32 = None
        return False


def trigger_buzzer():
    if _esp32 is None:
        print("[ESP32] Not connected - skipping buzzer trigger (fine for testing without it plugged in)")
        return
    _esp32.write(b"BUZZ\n")
