#!/usr/bin/env python3
"""Nepal EWS backend service.

This script polls the ESP8266 sensor node at /data, saves readings to SQLite,
and exposes a simple HTTP API for status and history.
"""

import argparse
import json
import sqlite3
import threading
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

DB_PATH = "nepal_backend.sqlite"
DEFAULT_SENSOR_HOST = "192.168.1.100"
DEFAULT_POLL_INTERVAL = 10
DEFAULT_API_PORT = 5000

CREATE_READINGS_TABLE = """
CREATE TABLE IF NOT EXISTS sensor_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp INTEGER NOT NULL,
    water_level REAL,
    soil_moisture REAL,
    temperature REAL,
    humidity REAL,
    rssi INTEGER,
    status TEXT
)
"""

CREATE_STATUS_TABLE = """
CREATE TABLE IF NOT EXISTS sensor_status (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    last_check INTEGER,
    connected INTEGER,
    last_error TEXT,
    sensor_url TEXT
)
"""

INSERT_STATUS_ROW = "INSERT OR IGNORE INTO sensor_status (id, connected, sensor_url) VALUES (1, 0, ?)"

lock = threading.Lock()

class BackendState:
    def __init__(self, sensor_host, poll_interval, api_port):
        self.sensor_host = sensor_host
        self.poll_interval = poll_interval
        self.api_port = api_port
        self.sensor_url = f"http://{sensor_host}/data"
        self.last_reading = None
        self.last_status = {
            "connected": False,
            "last_check": None,
            "last_error": None,
            "sensor_url": self.sensor_url,
        }

    def update_last_reading(self, reading):
        with lock:
            self.last_reading = reading

    def update_status(self, connected, last_error=None):
        with lock:
            self.last_status.update({
                "connected": connected,
                "last_check": int(time.time()),
                "last_error": last_error,
                "sensor_url": self.sensor_url,
            })

state = None


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(CREATE_READINGS_TABLE)
    conn.execute(CREATE_STATUS_TABLE)
    conn.execute(INSERT_STATUS_ROW, (state.sensor_url,))
    conn.commit()
    conn.close()


def fetch_sensor_data():
    request = urllib.request.Request(state.sensor_url, headers={"User-Agent": "NepalEWSBackend/1.0"})
    with urllib.request.urlopen(request, timeout=8) as response:
        if response.status != 200:
            raise ValueError(f"Unexpected HTTP status {response.status}")
        payload = response.read().decode("utf-8")
        data = json.loads(payload)
        return data


def save_reading(reading, status_text="ok"):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO sensor_readings (timestamp, water_level, soil_moisture, temperature, humidity, rssi, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            int(time.time()),
            reading.get("waterLevel"),
            reading.get("soilMoisture"),
            reading.get("temperature"),
            reading.get("humidity"),
            reading.get("rssi"),
            status_text,
        ),
    )
    conn.execute(
        "UPDATE sensor_status SET last_check = ?, connected = ?, last_error = ?, sensor_url = ? WHERE id = 1",
        (int(time.time()), 1, None, state.sensor_url),
    )
    conn.commit()
    conn.close()


def save_status(connected, last_error=None):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "UPDATE sensor_status SET last_check = ?, connected = ?, last_error = ?, sensor_url = ? WHERE id = 1",
        (int(time.time()), int(bool(connected)), last_error, state.sensor_url),
    )
    conn.commit()
    conn.close()


def poll_loop():
    while True:
        try:
            reading = fetch_sensor_data()
            print(f"[POLL] Connected to sensor node at {state.sensor_url}")
            print(f"[POLL] Received: {reading}")
            save_reading(reading)
            state.update_last_reading(reading)
            state.update_status(True, None)
        except (urllib.error.URLError, urllib.error.HTTPError, ValueError, json.JSONDecodeError) as exc:
            error_msg = str(exc)
            print(f"[ERROR] Sensor node unreachable or invalid response: {error_msg}")
            state.update_status(False, error_msg)
            save_status(False, error_msg)
        time.sleep(state.poll_interval)


def query_latest_reading():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute(
        "SELECT timestamp, water_level, soil_moisture, temperature, humidity, rssi, status FROM sensor_readings ORDER BY timestamp DESC LIMIT 1"
    )
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return {
        "timestamp": row[0],
        "waterLevel": row[1],
        "soilMoisture": row[2],
        "temperature": row[3],
        "humidity": row[4],
        "rssi": row[5],
        "status": row[6],
    }


def query_history(limit=100):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute(
        "SELECT timestamp, water_level, soil_moisture, temperature, humidity, rssi, status FROM sensor_readings ORDER BY timestamp DESC LIMIT ?",
        (limit,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "timestamp": row[0],
            "waterLevel": row[1],
            "soilMoisture": row[2],
            "temperature": row[3],
            "humidity": row[4],
            "rssi": row[5],
            "status": row[6],
        }
        for row in rows
    ]


def query_status():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute("SELECT last_check, connected, last_error, sensor_url FROM sensor_status WHERE id = 1")
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return {
        "last_check": row[0],
        "connected": bool(row[1]),
        "last_error": row[2],
        "sensor_url": row[3],
    }


class NepalRequestHandler(BaseHTTPRequestHandler):
    def _send_json(self, body, status=200):
        payload = json.dumps(body, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path == "/latest":
            latest = query_latest_reading()
            if latest is None:
                self._send_json({"error": "No sensor data available yet."}, status=404)
                return
            self._send_json(latest)
            return

        if path == "/history":
            limit = int(query.get("limit", [100])[0])
            history = query_history(limit)
            self._send_json({"count": len(history), "history": history})
            return

        if path == "/status":
            status = query_status()
            self._send_json(status or {"error": "Status unavailable."})
            return

        if path == "/":
            self._send_json(
                {
                    "service": "Nepal EWS Backend",
                    "sensor_url": state.sensor_url,
                    "poll_interval": state.poll_interval,
                    "api_endpoints": ["/latest", "/history?limit=100", "/status"],
                }
            )
            return

        self._send_json({"error": "Endpoint not found."}, status=404)

    def log_message(self, format, *args):
        return


def run_server():
    address = ("", state.api_port)
    server = HTTPServer(address, NepalRequestHandler)
    print(f"[API] Nepal backend listening on http://0.0.0.0:{state.api_port}")
    server.serve_forever()


def parse_args():
    parser = argparse.ArgumentParser(description="Nepal EWS Python backend for sensor polling and SQLite storage.")
    parser.add_argument("--sensor-host", default=DEFAULT_SENSOR_HOST, help="ESP8266 sensor node IP or hostname")
    parser.add_argument("--poll-interval", type=int, default=DEFAULT_POLL_INTERVAL, help="Polling interval in seconds")
    parser.add_argument("--api-port", type=int, default=DEFAULT_API_PORT, help="HTTP API port")
    return parser.parse_args()


def main():
    global state
    args = parse_args()
    state = BackendState(args.sensor_host, args.poll_interval, args.api_port)
    init_db()

    poll_thread = threading.Thread(target=poll_loop, daemon=True)
    poll_thread.start()
    run_server()


if __name__ == "__main__":
    main()
