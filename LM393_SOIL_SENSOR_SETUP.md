# UPDATED SENSOR SETUP GUIDE - LM393 Soil Moisture Module

## ✨ NEW ADDITION: LM393 Soil Moisture Sensor Module

We've now added the **LM393 Soil Moisture Sensor Module** to detect landslide risk through soil moisture levels.

---

## 📦 LM393 MODULE OVERVIEW

### What is it?
The **LM393 Soil Moisture Sensor Module** is a comparator-based circuit that measures soil moisture and detects when soil reaches a critical threshold (indicating potential landslide risk).

### Key Features:
- **Dual Output**: Digital threshold (DO) + Analog level (AO)
- **Adjustable Sensitivity**: Potentiometer dial for threshold calibration
- **Low Power**: Only ~10mA consumption
- **3.3V Compatible**: Works directly with ESP8266
- **Cost**: ~$1-2 USD

---

## 🔌 PIN CONNECTIONS (LM393 Module)

```
LM393 Module (4-pin):

┌──────────────┐
│ LM393 Module │
├──────────────┤
│ Pin 1 (VCC)  │ ──→ 3.3V Power Rail
│ Pin 2 (GND)  │ ──→ Ground Rail (BLACK)
│ Pin 3 (DO)   │ ──→ ESP8266 D0 (GPIO16)  [Digital Output]
│ Pin 4 (AO)   │ ──→ ESP8266 D1 (GPIO5)   [Analog Output]
└──────────────┘

SOIL PROBE (2 metal pins):
  ├─→ Inserted into soil/water
  └─→ Connected to module's sensor input (internal)
```

---

## ⚙️ CALIBRATION PROCEDURE (CRITICAL!)

**IMPORTANT**: The LM393 module MUST be calibrated to work correctly!

### Step 1: Prepare Two Test Samples

```
DRY SAMPLE:           WET SAMPLE:
Completely dry soil   Saturated wet soil
or sand              (or pure water)

Keep both ready during calibration!
```

### Step 2: Dry Calibration

```
1. Remove soil probe from everything
2. Let probe air-dry (5 minutes)
3. Power on the module
4. Observe LED next to potentiometer:
   - LED should be ON (Red)
   - This means threshold is not met

5. If LED is OFF:
   - Slowly turn potentiometer CLOCKWISE
   - Until LED turns ON
   - Stop here
```

### Step 3: Wet Calibration

```
1. Insert soil probe into WET SOIL or WATER
2. Immediately observe LED:
   - LED should turn OFF (Go dark)
   - This means moisture detected below threshold
   
3. If LED stays ON:
   - Slowly turn potentiometer COUNTER-CLOCKWISE
   - Until LED turns OFF
   - Stop here
```

### Step 4: Fine-Tune Sensitivity

```
Repeat with DRY and WET samples until:
✓ DRY soil  → LED ON  (threshold NOT met)
✓ WET soil  → LED OFF (threshold MET - ALERT!)

If you want to detect moisture EARLIER:
  ↻ Turn potentiometer slightly counter-clockwise

If you want to detect moisture LATER:
  ↻ Turn potentiometer slightly clockwise
```

### Step 5: Field Verification

```
NORMAL CONDITIONS:
  • Soil probe in dry/normal soil → DO = HIGH (1)
  • Serial monitor shows low moisture %
  • Dashboard: Soil status = STABLE

RAIN/WET CONDITIONS:
  • Soil probe in wet soil → DO = LOW (0)
  • Serial monitor shows high moisture %
  • Dashboard: Soil status = WARNING → CRITICAL
```

---

## 📊 Output Behavior After Calibration

### Digital Output (DO) - Pin 3

```
DO Behavior (connected to ESP8266 D0):
┌─────────────────────────────────────────┐
│ DRY SOIL:                               │
│ digitalRead(D0) = HIGH (1)              │
│ Status: "STABLE"                        │
│ LED: ON                                 │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ WET SOIL / LANDSLIDE RISK:              │
│ digitalRead(D0) = LOW (0)               │
│ Status: "CRITICAL" / "UNSTABLE"         │
│ LED: OFF                                │
│ 🚨 ALARM TRIGGERS                       │
└─────────────────────────────────────────┘
```

### Analog Output (AO) - Pin 4

```
AO Behavior (connected to ESP8266 D1):

100% DRY:        50% MOIST:      100% WET:
0V (0 ADC)       ~1.65V          3.3V (1023 ADC)
│                │               │
└─────────────────┴───────────────┘
    Moisture Level Increases →

NOTE: D1 on ESP8266 reads digital values.
      For true analog, you'd need an external ADC.
      Currently we estimate analog level from DO + hysteresis.
```

---

## 🧪 TESTING THE SENSOR IN CODE

### In Arduino Serial Monitor (115200 baud):

```
✓ Expected output when DRY:
  [INIT] LM393 Soil Moisture Sensor initialized
  [SOIL] DO: HIGH (DRY) → Moisture: 25.3%
  [SOIL] DO: HIGH (DRY) → Moisture: 26.1%

✓ Expected output when WET:
  [SOIL] DO: LOW  (WET) → Moisture: 72.4%
  [SOIL] DO: LOW  (WET) → Moisture: 74.1%
  [ALERT] Soil moisture CRITICAL - Below threshold (50%)

✗ Error output (recalibrate):
  [SOIL] DO: HIGH (DRY) → Moisture: 75.0%  ← Should be low!
  [SOIL] DO: LOW  (WET) → Moisture: 20.1%  ← Should be high!
```

---

## 🌧️ LANDSLIDE THRESHOLD CONFIGURATION

### Default Settings in Code:

```cpp
const int SOIL_MOISTURE_THRESHOLD = 50;  // 50% = Landslide alert threshold
```

### Threshold Meanings:

```
THRESHOLDS FOR NEPAL CONTEXT:
  0-30%:   Very Dry    - Safe (green zone)
  30-50%:  Normal      - Caution (amber zone)
  50-100%: Wet/Satured - CRITICAL (red zone) 🚨
```

### To Change Threshold:

```cpp
// In sensor_code.ino, find this line:
const int SOIL_MOISTURE_THRESHOLD = 50;

// Change the number (0-100) based on your region:
const int SOIL_MOISTURE_THRESHOLD = 40;  // More sensitive
const int SOIL_MOISTURE_THRESHOLD = 60;  // Less sensitive

// Re-upload to ESP8266
```

---

## 🔧 TROUBLESHOOTING LM393

| Problem | Cause | Solution |
|---------|-------|----------|
| DO never changes | Not calibrated | Perform full calibration procedure |
| DO inverted (HIGH when wet) | Sensor installed backwards | Reverse the two probe pins |
| Erratic readings | Loose probe connection | Ensure probe firmly inserted in soil |
| Module not powering on | No power | Check VCC connected to 3.3V rail |
| LED always ON | Threshold set too high | Turn potentiometer counter-clockwise |
| LED always OFF | Threshold set too low | Turn potentiometer clockwise |

---

## 🔍 WHAT DO SOIL MOISTURE LEVELS MEAN?

### In Nepal's Monsoon Context:

```
┌─────────────────────────────────────────────────────────────┐
│ SOIL MOISTURE LEVEL          CONDITION           RISK        │
├─────────────────────────────────────────────────────────────┤
│ 0-20%:  Completely Dry       No recent rain      NONE        │
│                                                               │
│ 20-40%: Slightly Moist       Recent drizzle      LOW         │
│                              or mountain mist               │
│                                                               │
│ 40-60%: Moderate Moisture    Light rain          MEDIUM      │
│                              ongoing (6-12 hrs)  ⚠️          │
│                                                               │
│ 60-80%: Very Wet             Heavy rainfall      HIGH        │
│                              (12+ hrs)           🔴          │
│                                                               │
│ 80-100%:Saturated/Waterlogged Extreme monsoon    CRITICAL    │
│         (may trigger sensor during flash floods)  🚨🚨🚨    │
└─────────────────────────────────────────────────────────────┘
```

---

## 📱 DASHBOARD INTERPRETATION

### When Viewing Nepal EWS Dashboard:

```
Tower T-04 (Landslide Risk Monitoring):

❌ CRITICAL (RED):
   Soil: <50%
   Slope: "UNSTABLE"
   → ALERT: Landslide risk detected
   → Action: Evacuate vulnerable areas

⚠️ WARNING (AMBER):
   Soil: 50-60%
   Slope: "UNSTABLE"
   → CAUTION: Monitor closely during heavy rain

✅ SAFE (GREEN):
   Soil: >60%
   Slope: "STABLE"
   → No immediate risk
```

---

## 💡 TIPS FOR BEST RESULTS

1. **Sensor Placement**: Install probe at 10-20cm depth in soil (not surface)
2. **Multiple Sensors**: Consider deploying multiple nodes in high-risk slopes
3. **Calibration Season**: Re-calibrate after long dry season changes
4. **Maintenance**: Check probe for corrosion quarterly
5. **WiFi Range**: Keep within 50m of router for reliable data

---

## 📚 ADDITIONAL RESOURCES

- LM393 Datasheet: Google "LM393 comparator IC"
- Soil Moisture Sensor: https://www.electronics-lab.com/soil-moisture-sensor/
- Landslide Prediction: https://www.usgs.gov/natural-hazards/landslide-hazards

---

**Questions? Check QUICK_START.txt or EXECUTION_GUIDE.md**
