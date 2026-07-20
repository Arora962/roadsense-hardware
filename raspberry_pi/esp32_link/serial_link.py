"""
Serial link to the ESP8266, over the USB cable.

This is now a two-way, shared link:
  - OUT: the only command sent to the ESP8266 is "BUZZ", which tells it to
    sound the buzzer. The 8x8 matrix heartbeat animation runs entirely on
    the ESP8266 itself and doesn't need any commands from the Pi.
  - IN: the GPS module is wired to the ESP8266 (not the Pi), so raw NMEA
    sentences arrive on this same serial stream, mixed in with the
    occasional "ACK_BUZZ" / "ESP8266_READY" line. gps_sensor.py calls
    read_lines() below to pick its GPS lines out of that stream - it does
    NOT open its own serial port any more.

Only one thing in the whole project is allowed to open this serial port,
and it's this file. Everything else goes through connect() / trigger_buzzer()
/ read_lines().
"""
import serial
import time
import config

_esp32 = None
_read_buffer = ""


def connect():
    global _esp32
    try:
        # timeout=0 -> non-blocking reads, so read_lines() never stalls the
        # main loop waiting for bytes that may not be coming this instant.
        _esp32 = serial.Serial(config.ESP32_SERIAL_PORT, config.ESP32_BAUD_RATE, timeout=0)
        time.sleep(2)  # give the ESP8266 a moment to reset after the port opens
        print(f"[ESP8266] Connected on {config.ESP32_SERIAL_PORT}")
        return True
    except Exception as e:
        print(f"[ESP8266] Could not connect on {config.ESP32_SERIAL_PORT}: {e}")
        print("[ESP8266] Run `ls /dev/tty*` with it plugged/unplugged to find the right port, then update config.py")
        print("[ESP8266] Note: GPS now rides on this same link, so no GPS fix either until this connects.")
        _esp32 = None
        return False


def is_connected():
    return _esp32 is not None


def trigger_buzzer():
    if _esp32 is None:
        print("[ESP8266] Not connected - skipping buzzer trigger (fine for testing without it plugged in)")
        return
    _esp32.write(b"BUZZ\n")


def read_lines():
    """Non-blocking. Returns a list of whatever complete lines have arrived
    on the ESP8266 link since the last call (could be empty, could be
    several - GPS lines, ACK_BUZZ, ESP8266_READY, all mixed together).
    Callers just check the prefix of each line for what they care about.
    """
    global _read_buffer

    if _esp32 is None:
        return []

    try:
        waiting = _esp32.in_waiting
        if waiting:
            _read_buffer += _esp32.read(waiting).decode("ascii", errors="replace")
    except Exception as e:
        print(f"[ESP8266] Read error, will retry next loop: {e}")
        return []

    lines = []
    while "\n" in _read_buffer:
        line, _read_buffer = _read_buffer.split("\n", 1)
        stripped = line.strip()
        if stripped:
            lines.append(stripped)
    return lines
