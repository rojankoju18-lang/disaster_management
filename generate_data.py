"""
generate_data.py — Run this to generate fresh synthetic data files
Usage: python generate_data.py
Outputs: sensor_data.csv, sensor_history_24hr.json, storm_events.json
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

np.random.seed(42)

N_DAYS = 180
INTERVAL_MINUTES = 5
N_ROWS = N_DAYS * 24 * (60 // INTERVAL_MINUTES)
start_date = datetime(2024, 4, 1)

print(f"Generating {N_ROWS:,} rows ({N_DAYS} days @ {INTERVAL_MINUTES}min intervals)...")

timestamps = [start_date + timedelta(minutes=i*INTERVAL_MINUTES) for i in range(N_ROWS)]
months = np.array([t.month for t in timestamps])
hours  = np.array([t.hour for t in timestamps])

monsoon_intensity = np.where(
    (months >= 6) & (months <= 9),
    0.85 + 0.15 * np.sin((months - 6) / 4 * np.pi),
    np.where(months >= 10, 0.15, 0.25)
)

# Rainfall with storm events
base_rain = monsoon_intensity * 3
rain_event = np.zeros(N_ROWS)
storm_events = []
for _ in range(80):
    idx = np.random.randint(0, N_ROWS - 120)
    duration = np.random.randint(12, 120)
    intensity = np.random.uniform(5, 40) * monsoon_intensity[idx]
    rain_event[idx:idx+duration] += intensity * np.exp(-np.linspace(0, 3, duration))
    storm_events.append({
        "start": str(timestamps[idx]),
        "duration_hrs": round(duration * INTERVAL_MINUTES / 60, 1),
        "peak_intensity_mm_hr": round(float(intensity), 1),
        "month": int(months[idx])
    })

rainfall = np.clip(base_rain + rain_event + np.random.exponential(0.5, N_ROWS), 0, 80)

rain_cumulative = np.convolve(rainfall, np.ones(48)/8, mode='same')
water_level = 0.8 + rain_cumulative * 0.12 + monsoon_intensity * 0.6
water_level += np.random.normal(0, 0.05, N_ROWS)
water_level = np.clip(water_level, 0.2, 9.5)

soil_base = 40 + monsoon_intensity * 30
rain_lag = np.convolve(rainfall, np.ones(144)/144, mode='same')
soil_moisture = soil_base + rain_lag * 0.8 + np.random.normal(0, 2, N_ROWS)
soil_moisture = np.clip(soil_moisture, 20, 100)

temp_base = 22 + 5 * np.sin((months - 3) / 12 * 2 * np.pi)
diurnal = 4 * np.sin((hours - 6) / 24 * 2 * np.pi)
temp = np.clip(temp_base + diurnal - rainfall * 0.05 + np.random.normal(0, 0.8, N_ROWS), 8, 36)
humidity = np.clip(55 + monsoon_intensity * 30 + rainfall * 0.3 - (temp - 22) * 0.8 + np.random.normal(0, 3, N_ROWS), 30, 100)
flow_rate = np.clip(np.power(np.maximum(water_level, 0.1), 1.67) * 3.2 + np.random.normal(0, 0.5, N_ROWS), 0, 120)
turbidity = np.clip(15 + water_level * 8 + rainfall * 0.5 + np.random.normal(0, 3, N_ROWS), 5, 300)
water_rise = np.gradient(water_level) * 6

def label_risk(wl, sm, rf):
    if wl > 4.5 or sm > 88 or rf > 30: return 'CRITICAL'
    if wl > 3.0 or sm > 78 or rf > 15: return 'HIGH'
    if wl > 2.0 or sm > 65 or rf > 5:  return 'ELEVATED'
    return 'NORMAL'

risk_labels = [label_risk(w, s, r) for w, s, r in zip(water_level, soil_moisture, rainfall)]

df = pd.DataFrame({
    'timestamp': timestamps,
    'month': months, 'hour': hours,
    'rainfall_mm_hr':    np.round(rainfall, 2),
    'water_level_m':     np.round(water_level, 3),
    'water_rise_rate':   np.round(water_rise, 4),
    'soil_moisture_pct': np.round(soil_moisture, 1),
    'temperature_c':     np.round(temp, 1),
    'humidity_pct':      np.round(humidity, 1),
    'flow_rate_m3s':     np.round(flow_rate, 2),
    'turbidity_ntu':     np.round(turbidity, 1),
    'risk_level':        risk_labels
})

# ── Save CSV ──────────────────────────────────────────────
df.to_csv('sensor_data.csv', index=False)
print(f"  sensor_data.csv — {len(df):,} rows")

# ── Save last 24hr JSON ───────────────────────────────────
last_day = df.tail(288).copy()
last_day['timestamp'] = last_day['timestamp'].astype(str)
last_day.to_json('sensor_history_24hr.json', orient='records', indent=2)
print(f"  sensor_history_24hr.json — last 288 readings (24hrs)")

# ── Save storm events ─────────────────────────────────────
with open('storm_events.json', 'w') as f:
    json.dump(sorted(storm_events, key=lambda x: x['peak_intensity_mm_hr'], reverse=True), f, indent=2)
print(f"  storm_events.json — {len(storm_events)} storm events catalogued")

print(f"\nRisk distribution:")
for k, v in df['risk_level'].value_counts().items():
    print(f"  {k:10s}: {v:,} ({v/len(df)*100:.1f}%)")
print("\nDone.")
