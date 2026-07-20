"""
The rulebook - decides whether what the sensors are seeing right now counts
as a real near-miss.

RULE: A near-miss is only logged if BOTH of these are true -
  1) The IMU sees a sudden jerk (something abrupt happened to the vehicle's motion)
  2) That's confirmed by EITHER the ultrasonic sensor (something is close)
     OR the camera (it can see what caused it)

This two-part rule is what stops the system from logging every little bump
or hard brake as a "near-miss" - it needs BOTH the sudden motion AND
evidence of an actual hazard causing it.
"""
import time


def evaluate(imu_reading, ultrasonic_close, distance_cm, object_class, object_confidence, location):
    if not imu_reading["is_spike"]:
        return None  # nothing sudden happened - not a near-miss

    confirmed_by_ultrasonic = ultrasonic_close
    confirmed_by_camera = object_class not in ("none", "unknown")

    if not (confirmed_by_ultrasonic or confirmed_by_camera):
        return None  # sudden motion but nothing around to explain it - probably just a bump

    severity = score_severity(imu_reading["jerk"], distance_cm, object_class, location)

    return {
        "timestamp": time.time(),
        "severity": severity,
        "object_class": object_class,
        "distance_cm": distance_cm,
        "jerk": round(imu_reading["jerk"], 2),
        "location": location,
    }


def score_severity(jerk, distance_cm, object_class, location):
    """Returns a severity score from 0 (mild) to 5 (severe)."""
    score = 0

    # how hard was the jerk
    if jerk > 20:
        score += 3
    elif jerk > 12:
        score += 2
    else:
        score += 1

    # how close was the object
    if distance_cm and distance_cm < 20:
        score += 2
    elif distance_cm and distance_cm < 40:
        score += 1

    # what caused it
    risk_weight = {"pedestrian": 2, "two-wheeler": 1.5, "vehicle": 1, "unknown": 0.5, "none": 0}
    score += risk_weight.get(object_class, 0)

    # faster = more dangerous, if we have a GPS fix
    if location and location.get("speed_kmph", 0) > 20:
        score += 1

    return min(round(score), 5)
