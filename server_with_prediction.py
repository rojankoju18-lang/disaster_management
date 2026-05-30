from flask import Flask, request, jsonify
from collections import deque
from datetime import datetime
import numpy as np
import joblib
import json
import time

app = Flask(__name__)

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
    return response

# ── Load ML model ─────────────────────────────────────────
try:
    model   = joblib.load('ews_model.pkl')
    le      = joblib.load('label_encoder.pkl')
    with open('model_metadata.json') as f:
        meta = json.load(f)
    FEATURES = meta['features']
    print("[ML] Model loaded — 45-min ahead predictor active")
    ML_READY = True
except Exception as e:
    print(f"[ML] Model not found, running rule-based only: {e}")
    ML_READY = False

# ── In-memory ring buffer (last 36 readings = 3 hrs) ─────
HISTORY_SIZE = 50
history = deque(maxlen=HISTORY_SIZE)

latest_data = {
    "soil_moisture": 0, "water_level": 0,
    "temperature": 0, "humidity": 0,
    "rainfall_mm_hr": 0, "flow_rate": 0, "turbidity": 0,
    "timestamp": None, "alert": False, "alert_reason": "",
    "prediction": {"risk_45min": "UNKNOWN", "confidence": 0, "probabilities": {}}
}

# ── Thresholds (rule-based fallback) ─────────────────────
T = {"CRITICAL": (4.5, 88, 30), "HIGH": (3.0, 78, 15), "ELEVATED": (2.0, 65, 5)}

# ─────────────────────────────────────────────────────────

def rolling(field, n, fn='mean'):
    vals = [h[field] for h in list(history)[-n:] if field in h]
    if not vals:
        return 0
    return np.mean(vals) if fn == 'mean' else np.sum(vals)

def delta(field, n):
    arr = [h[field] for h in list(history)[-n:] if field in h]
    if len(arr) < 2:
        return 0
    return arr[-1] - arr[0]

def get_month_hour():
    now = datetime.now()
    return now.month, now.hour

def rule_based_risk(wl, sm, rf):
    if wl > T['CRITICAL'][0] or sm > T['CRITICAL'][1] or rf > T['CRITICAL'][2]:
        return 'CRITICAL'
    if wl > T['HIGH'][0]     or sm > T['HIGH'][1]     or rf > T['HIGH'][2]:
        return 'HIGH'
    if wl > T['ELEVATED'][0] or sm > T['ELEVATED'][1] or rf > T['ELEVATED'][2]:
        return 'ELEVATED'
    return 'NORMAL'

def ml_predict(reading):
    """Build feature vector and predict 45-min risk"""
    if not ML_READY:
        return {"risk_45min": rule_based_risk(
            reading['water_level'], reading['soil_moisture'], reading['rainfall_mm_hr']
        ), "confidence": None, "probabilities": {}, "method": "rule-based"}

    month, hour = get_month_hour()
    wl   = reading['water_level']
    sm   = reading['soil_moisture']
    rf   = reading['rainfall_mm_hr']
    flow = reading.get('flow_rate', wl ** 1.67 * 3.2)
    turb = reading.get('turbidity', 15 + wl * 8)

    feat = [
        rf,                        # rainfall_mm_hr
        rolling('rainfall_mm_hr', 6),   # rain_30min_avg
        rolling('rainfall_mm_hr', 12),  # rain_1hr_avg
        rolling('rainfall_mm_hr', 36, 'sum'),  # rain_3hr_sum
        wl,                        # water_level_m
        rolling('water_level', 12),     # water_1hr_avg
        delta('water_level', 12),       # water_rise_1hr
        delta('water_level', 6),        # water_rise_30min
        delta('water_level', 1),        # water_rise_rate (per step)
        sm,                        # soil_moisture_pct
        delta('soil_moisture', 12),     # soil_trend
        reading.get('temperature', 25), # temperature_c
        reading.get('humidity', 70),    # humidity_pct
        flow,                      # flow_rate_m3s
        turb,                      # turbidity_ntu
        month, hour
    ]

    X = np.array(feat).reshape(1, -1)
    pred_enc  = model.predict(X)[0]
    proba     = model.predict_proba(X)[0]
    risk      = le.inverse_transform([pred_enc])[0]
    confidence = float(np.max(proba))

    prob_dict = {cls: round(float(p), 3) for cls, p in zip(le.classes_, proba)}
    return {
        "risk_45min": risk,
        "confidence": round(confidence, 3),
        "probabilities": prob_dict,
        "method": "ml-random-forest"
    }

def check_immediate_alert(wl, sm, rf):
    reasons = []
    if wl >= T['HIGH'][0]:    reasons.append(f"Water level HIGH: {wl:.2f}m")
    if sm >= T['HIGH'][1]:    reasons.append(f"Soil saturation HIGH: {sm:.1f}%")
    if rf >= T['HIGH'][2]:    reasons.append(f"Rainfall HIGH: {rf:.1f}mm/hr")
    wr = delta('water_level', 6)
    if wr >= 0.5:             reasons.append(f"Rapid rise: +{wr:.2f}m in 30min")
    return bool(reasons), " | ".join(reasons)

# ── ROUTES ────────────────────────────────────────────────

@app.route("/post-data", methods=["POST"])
def receive_data():
    body = request.get_json(silent=True)
    if not body:
        return jsonify({"error": "No JSON"}), 400

    # Normalize analog 0-1023 → percentages if raw values given
    soil_raw  = int(body.get("soil_moisture", 0))
    water_raw = int(body.get("water_level", 0))
    soil_pct  = round((1023 - soil_raw) / 1023 * 100, 1) if soil_raw > 100 else float(soil_raw)
    water_m   = round(water_raw / 1023 * 9.5, 3)         if water_raw > 10  else float(water_raw)

    # Derived
    rainfall  = float(body.get("rainfall_mm_hr", 0))
    flow      = round(max(water_m, 0.1) ** 1.67 * 3.2, 2)
    turb      = round(15 + water_m * 8 + rainfall * 0.5, 1)

    reading = {
        "soil_moisture":   soil_pct,
        "water_level":     water_m,
        "temperature":     float(body.get("temperature", 0)),
        "humidity":        float(body.get("humidity", 0)),
        "rainfall_mm_hr":  rainfall,
        "flow_rate":       flow,
        "turbidity":       turb,
        "timestamp":       datetime.now().isoformat(),
        "unix_ts":         time.time()
    }

    history.append(reading)

    # Predict 45 min ahead
    prediction = ml_predict(reading)

    # Immediate threshold alert
    alert, reason = check_immediate_alert(water_m, soil_pct, rainfall)

    # Also alert if ML predicts CRITICAL in 45 min
    if prediction['risk_45min'] == 'CRITICAL' and prediction.get('confidence', 0) > 0.8:
        alert = True
        reason = (reason + " | " if reason else "") + f"ML predicts CRITICAL in 45min (conf={prediction['confidence']:.0%})"

    reading.update({"alert": alert, "alert_reason": reason, "prediction": prediction})
    latest_data.update(reading)

    level = "CRITICAL" if alert else prediction['risk_45min']
    print(f"[{reading['timestamp'][:19]}] {level} | water={water_m:.2f}m soil={soil_pct:.1f}% rf={rainfall:.1f}mm | pred_45min={prediction['risk_45min']} ({prediction.get('confidence', '?'):.0%})")

    return jsonify({
        "status": "OK",
        "alert": alert,
        "reason": reason,
        "prediction": prediction
    }), 200


@app.route("/latest", methods=["GET"])
def get_latest():
    return jsonify(latest_data), 200


@app.route("/history", methods=["GET"])
def get_history():
    return jsonify(list(history)), 200


@app.route("/predict", methods=["POST"])
def predict_only():
    """Standalone prediction — POST any sensor reading, get 45-min forecast"""
    body = request.get_json(silent=True) or {}
    reading = {
        "water_level":    float(body.get("water_level", 2.0)),
        "soil_moisture":  float(body.get("soil_moisture", 60)),
        "rainfall_mm_hr": float(body.get("rainfall_mm_hr", 0)),
        "temperature":    float(body.get("temperature", 25)),
        "humidity":       float(body.get("humidity", 70)),
    }
    prediction = ml_predict(reading)
    return jsonify(prediction), 200


@app.route("/alert", methods=["GET"])
def get_alert():
    return jsonify({
        "alert":      latest_data["alert"],
        "reason":     latest_data["alert_reason"],
        "prediction": latest_data.get("prediction", {}),
        "timestamp":  latest_data["timestamp"]
    }), 200


@app.route("/", methods=["GET"])
def health():
    return jsonify({
        "status": "Nepal EWS running",
        "ml_ready": ML_READY,
        "readings_buffered": len(history),
        "model_accuracy": meta.get('accuracy') if ML_READY else None
    }), 200


if __name__ == "__main__":
    print("=" * 55)
    print("  Nepal EWS + ML Prediction Server — port 5000")
    print(f"  ML model: {'ACTIVE (97.6% accuracy)' if ML_READY else 'NOT LOADED'}")
    print("  Endpoints:")
    print("    POST /post-data  — ESP8266 sensor push")
    print("    GET  /latest     — current readings + prediction")
    print("    GET  /history    — last 50 readings")
    print("    GET  /alert      — alert + 45-min forecast")
    print("    POST /predict    — standalone ML prediction")
    print("=" * 55)
    app.run(host="0.0.0.0", port=5000, debug=True)
