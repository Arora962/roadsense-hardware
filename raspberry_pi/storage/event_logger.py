"""
Local SQLite storage for near-miss events, so nothing is ever lost even
without internet. Also (optionally) forwards each event to your backend
server once you flip SEND_TO_BACKEND on in config.py.
"""
import sqlite3
import os
import config

os.makedirs(os.path.dirname(config.DB_PATH) or ".", exist_ok=True)


def init_db():
    conn = sqlite3.connect(config.DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL,
            severity INTEGER,
            object_class TEXT,
            distance_cm REAL,
            jerk REAL,
            lat REAL,
            lon REAL,
            speed_kmph REAL
        )
        """
    )
    conn.commit()
    conn.close()


def save_event(event):
    conn = sqlite3.connect(config.DB_PATH)
    location = event.get("location") or {}
    conn.execute(
        """
        INSERT INTO events (timestamp, severity, object_class, distance_cm, jerk, lat, lon, speed_kmph)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            event["timestamp"],
            event["severity"],
            event["object_class"],
            event["distance_cm"],
            event["jerk"],
            location.get("lat"),
            location.get("lon"),
            location.get("speed_kmph"),
        ),
    )
    conn.commit()
    conn.close()
    print(f"[Storage] Event saved locally to {config.DB_PATH}")

    if config.SEND_TO_BACKEND:
        try:
            import requests

            requests.post(config.BACKEND_URL, json=event, timeout=3)
            print("[Storage] Event also sent to backend")
        except Exception as e:
            print(f"[Storage] Could not reach backend right now ({e}) - event is safely stored locally, nothing lost")


def get_all_events():
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM events ORDER BY timestamp DESC").fetchall()
    conn.close()
    return [dict(row) for row in rows]
