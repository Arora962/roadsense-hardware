"""
Quick way to see what's been logged so far, without needing the website yet.

Run with: python3 view_events.py
"""
from storage import event_logger

events = event_logger.get_all_events()

if not events:
    print("No events logged yet. Run simulate_near_miss.py or main.py first.")
else:
    print(f"{len(events)} event(s) logged:\n")
    for e in events:
        gps = f"GPS: {e['lat']}, {e['lon']}" if e["lat"] else "no GPS fix"
        print(
            f"#{e['id']} | severity {e['severity']}/5 | {e['object_class']} | "
            f"{e['distance_cm']:.0f}cm | jerk {e['jerk']:.1f} | {gps}"
        )
