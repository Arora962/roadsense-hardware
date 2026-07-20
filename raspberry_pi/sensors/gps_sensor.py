"""
GPS module reader.

Reads NMEA sentences over serial and pulls out latitude, longitude, and speed.

NOTE: GPS modules need a clear view of the sky to get a "fix". Indoors, on a
desk, it is completely normal to get no fix at all - get_location() will just
return None, and the rest of the system keeps working fine without it
(events just get logged with no location attached).
"""
import serial
import pynmea2
import config

try:
    _gps_serial = serial.Serial(config.GPS_SERIAL_PORT, config.GPS_BAUD_RATE, timeout=1)
except Exception as e:
    print(f"[GPS] Could not open {config.GPS_SERIAL_PORT}: {e}")
    print("[GPS] This is fine for desk testing - location will just be None until you fix the port or go outdoors.")
    _gps_serial = None


def get_location():
    """Returns {'lat':..., 'lon':..., 'speed_kmph':...} or None if there's no fix yet."""
    if _gps_serial is None:
        return None
    try:
        line = _gps_serial.readline().decode("ascii", errors="replace").strip()
        if line.startswith("$GPRMC") or line.startswith("$GNRMC"):
            msg = pynmea2.parse(line)
            if msg.status == "A":  # 'A' = valid fix, 'V' = no fix yet
                return {
                    "lat": msg.latitude,
                    "lon": msg.longitude,
                    "speed_kmph": (msg.spd_over_grnd or 0) * 1.852,
                }
    except (pynmea2.ParseError, UnicodeDecodeError):
        pass
    return None
