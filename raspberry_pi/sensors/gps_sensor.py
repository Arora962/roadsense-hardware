"""
GPS reader - now via the ESP8266 link, not a Pi serial port.

The GPS module (NEO-6M) is wired directly to the ESP8266 (TX -> D2), not
the Pi. The ESP8266 forwards the raw NMEA sentences it receives over the
same USB serial cable it already uses for buzzer commands. So this file no
longer opens its own serial port - it asks esp32_link.serial_link for
whatever lines have come in since last time, and picks out the GPS ones.

NOTE: GPS modules need a clear view of the sky to get a "fix". Indoors, on
a desk, it is completely normal to get no fix at all - get_location() will
just return None (or the last known fix) and the rest of the system keeps
working fine without it (events just get logged with no location attached).
"""
import pynmea2
from esp32_link import serial_link

_last_location = None


def get_location():
    """Returns {'lat':..., 'lon':..., 'speed_kmph':...} from the most recent
    valid GPS fix seen so far, or None if there hasn't been one yet."""
    global _last_location

    for line in serial_link.read_lines():
        if line.startswith("$GPRMC") or line.startswith("$GNRMC"):
            try:
                msg = pynmea2.parse(line)
                if msg.status == "A":  # 'A' = valid fix, 'V' = no fix yet
                    _last_location = {
                        "lat": msg.latitude,
                        "lon": msg.longitude,
                        "speed_kmph": (msg.spd_over_grnd or 0) * 1.852,
                    }
            except (pynmea2.ParseError, AttributeError):
                pass  # partial/garbled sentence - skip it, next one will come

    return _last_location
