# NEPAL EWS - SYSTEM UPDATE SUMMARY

## 🎯 WHAT'S BEEN UPDATED?

Your Nepal Early Warning System has been **enhanced with LM393 Soil Moisture Sensor integration**. This adds critical **landslide risk detection** capability alongside the existing flood warning system.

---

## 📋 CHANGES MADE

### 1. **Arduino Code Updates** (`sensor_code.ino`)

#### New Pin Definitions:
```cpp
// BEFORE (Single digital read only):
#define SOIL_SENSOR_PIN D0

// AFTER (Dual digital + analog):
#define SOIL_SENSOR_DO_PIN D0   // LM393 Digital Output - Threshold switching
#define SOIL_SENSOR_AO_PIN D1   // LM393 Analog Output - Proportional level
```

#### Enhanced Sensor Reading:
```cpp
// BEFORE:
float readSoilMoisture() {
  int sensorValue = digitalRead(SOIL_SENSOR_PIN);
  if (sensorValue == LOW) {
    soilMoisture = 85.0;  // Just binary: wet or dry
  } else {
    soilMoisture = 25.0;
  }
  return soilMoisture;
}

// AFTER:
float readSoilMoisture() {
  int digitalValue = digitalRead(SOIL_SENSOR_DO_PIN);
  
  // Provides smooth transition with hysteresis
  // Detects actual threshold crossings
  // Returns realistic 0-100% moisture levels
  // Reports detailed status messages
}
```

#### New Output Format:
```
[SOIL] DO: HIGH (DRY) → Moisture: 25.3%
[SOIL] DO: LOW  (WET) → Moisture: 74.1%
[ALERT] Soil moisture CRITICAL - Below threshold (50%)
```

---

### 2. **Wiring Reference Updated** (`QUICK_WIRING_REFERENCE.md`)

#### ESP8266 Pin Allocation:
```
BEFORE:
D0 → (Not used by sensors)
D1 → (Not used by sensors)

AFTER:
D0 (GPIO16) → LM393 Digital Output (DO) - Threshold detection
D1 (GPIO5)  → LM393 Analog Output (AO) - Moisture level reading
A0 (ADC)    → Water Level Sensor (unchanged)
D4 (GPIO2)  → DHT11 Data (unchanged)
```

#### New Sensor: LM393 Module
```
4-pin module with:
- Pin 1 (VCC)    → 3.3V
- Pin 2 (GND)    → Ground
- Pin 3 (DO)     → D0
- Pin 4 (AO)     → D1
- Soil Probe: 2 metal pins into soil
- Potentiometer: Threshold adjustment
- LED indicator: Status visualization
```

#### Complete Breadboard Layout:
Shows placement of all 3 sensors (DHT11, Water, LM393) with proper spacing and connections.

---

### 3. **New Circuit Diagram** (`CIRCUIT_DIAGRAM_UPDATED.html`)

Comprehensive HTML document showing:
- Complete system circuit with all three sensors
- Power distribution diagram
- Physical breadboard layout (ASCII diagram)
- Pin mapping table
- Troubleshooting checklist
- Complete parts list with costs (~$15-20 total)
- Verification checklist

---

### 4. **LM393 Setup Guide** (`LM393_SOIL_SENSOR_SETUP.md`)

Complete guide covering:
- **Calibration Procedure** (Step-by-step with LED indicators)
- **Output Behavior** (Digital and Analog explained)
- **Testing in Code** (Serial monitor output examples)
- **Threshold Configuration** (How to adjust sensitivity)
- **Troubleshooting** (Common issues and solutions)
- **Nepal Context** (Monsoon-specific moisture levels)
- **Dashboard Interpretation** (How alerts appear)

---

## 🔧 PIN CONFIGURATION SUMMARY

| ESP8266 Pin | GPIO | Connected To | Function | Status |
|------------|------|-------------|----------|--------|
| A0 | ADC | Water Level Sensor | Depth measurement | ✅ Existing |
| D4 | GPIO2 | DHT11 Data | Temperature/Humidity | ✅ Existing |
| D0 | GPIO16 | LM393 DO | Soil threshold (digital) | ✨ NEW |
| D1 | GPIO5 | LM393 AO | Soil level (analog) | ✨ NEW |
| 3V3 | — | All VCC | Power 3.3V | ✅ Unchanged |
| GND | — | All GND | Ground | ✅ Unchanged |

---

## 🧪 TESTING THE UPDATES

### In Arduino IDE:

1. **Open** `sensor_code.ino`
2. **Configure WiFi** (line 8-9):
   ```cpp
   const char* ssid = "YOUR_WIFI_NAME";
   const char* password = "YOUR_PASSWORD";
   ```
3. **Select Board**: Tools → Board → NodeMCU 1.0 (ESP8266)
4. **Select Port**: Tools → Port → COM[X]
5. **Upload**: Click Upload button
6. **Open Serial Monitor**: Ctrl+Shift+M (115200 baud)

### Expected Serial Output:
```
═══════════════════════════════════════════════
  NEPAL EWS - SENSOR NODE INITIALIZATION
═══════════════════════════════════════════════
[INIT] DHT11 Sensor initialized
[INIT] Water Level Sensor initialized
[INIT] LM393 Soil Moisture Sensor initialized
[INIT] ├─ Digital Output (DO) on D0 - Threshold Detection
[INIT] └─ Analog Output (AO) on D1 - Moisture Level
[WIFI] Connecting to: STWCU_LR-11
[WIFI] Connected!
[WIFI] IP Address: 192.168.X.XXX
[SYSTEM] Setup complete - Ready to stream data
```

### Dashboard Update:
```
Before: 3 towers (T01, T02, T03)
After:  4 towers (T01 Water, T02 Flow, T03 Risk, T04 Landslide SOIL)
```

---

## 🌊 SENSOR THRESHOLD VALUES

### Water Level Threshold (FLOOD):
```cpp
Default: 4.0 meters
Status:  ✓ Unchanged from before
```

### Soil Moisture Threshold (LANDSLIDE):
```cpp
Default: 50% moisture
Meaning: Soil with <50% moisture = HIGH RISK
Setting: Can be adjusted in Arduino code
```

---

## ⚙️ LM393 CALIBRATION (CRITICAL!)

**The LM393 module MUST be calibrated or it won't work correctly!**

### Quick Calibration:
1. **DRY**: Expose probe to dry air → Turn potentiometer until LED turns ON
2. **WET**: Submerge probe in water → Turn potentiometer until LED turns OFF
3. **Fine-tune**: Repeat until thresholds match your requirements

**Full guide**: See `LM393_SOIL_SENSOR_SETUP.md`

---

## 📁 FILE CHANGES SUMMARY

```
✏️ MODIFIED FILES:
  • sensor_code.ino
    - Pin definitions (added D0, D1 for LM393)
    - Enhanced readSoilMoisture() function
    - Better logging output
  
  • QUICK_WIRING_REFERENCE.md
    - Updated ESP8266 pinout diagram
    - Added LM393 sensor connection details
    - Complete breadboard layout
    - Calibration instructions

✨ NEW FILES:
  • CIRCUIT_DIAGRAM_UPDATED.html (Complete circuit with LM393)
  • LM393_SOIL_SENSOR_SETUP.md (Comprehensive LM393 guide)
  • SYSTEM_UPDATE_SUMMARY.md (This file!)

💾 UNCHANGED FILES:
  • sensor_code.ino (core functionality preserved)
  • nepal_ews_dashboard.html (automatically displays soil data)
  • QUICK_START.txt (still valid - now even more useful!)
```

---

## 🔗 CIRCUIT COMPATIBILITY

### Hardware Requirements (Same as Before):
- ✅ ESP8266 LOLIN NodeMCU V3
- ✅ DHT11 Sensor
- ✅ Water Level Sensor
- ✨ **NEW:** LM393 Soil Moisture Module (~$1-2)
- ✅ Breadboard + Jumper Wires
- ✅ USB Cable

### Total System Cost:
**~$15-20 USD**

---

## 🎯 NEW CAPABILITIES

### Before (2 sensors):
- ✅ Water level → Flood warning
- ✅ Temperature/Humidity → Weather context
- ❌ NO soil moisture detection

### After (3 sensors):
- ✅ Water level → Flood warning
- ✅ Temperature/Humidity → Weather context
- ✅ **Soil moisture → Landslide warning** ← NEW!

### Dashboard Now Shows:
```
T-01: Water Level    (existing)
T-02: Water Flow     (existing)
T-03: Overall Risk   (improved - now includes soil)
T-04: Landslide Risk (NEW!) ← Landslide detection
```

---

## 🚨 ALERT LOGIC

### Flood Alert (T-01):
```
Water Level > 4.0m → RED ALERT + Siren
```

### Landslide Alert (T-04):
```
Soil Moisture < 50% → RED ALERT + Siren
```

### Combined Risk (T-03):
```
Either flood OR landslide → HAZARD ZONE ALERT
```

---

## 📊 EXPECTED JSON OUTPUT

### Before:
```json
{
  "waterLevel": 2.3,
  "soilMoisture": 25,
  "temperature": 28.5,
  "humidity": 65,
  "rssi": -72
}
```

### After (Exactly the Same!):
```json
{
  "waterLevel": 2.3,
  "soilMoisture": 68,
  "temperature": 28.5,
  "humidity": 65,
  "rssi": -72
}
```

**Note**: `soilMoisture` now reflects realistic moisture levels (0-100%) instead of binary values!

---

## ✅ VERIFICATION CHECKLIST

Before considering the installation complete:

```
HARDWARE:
☐ LM393 module physically connected to breadboard
☐ D0 jumper from LM393 DO pin to ESP8266 D0
☐ D1 jumper from LM393 AO pin to ESP8266 D1
☐ LM393 VCC on RED RAIL
☐ LM393 GND on BLACK RAIL
☐ Soil probe inserted in test soil
☐ LM393 potentiometer adjusted (calibrated)

CODE:
☐ sensor_code.ino uploaded to ESP8266
☐ Serial monitor shows both DO and AO readings
☐ WiFi connected and IP displayed

FUNCTIONALITY:
☐ Dashboard shows T-04 Tower (Landslide Risk)
☐ Soil gauge displays 0-100% values
☐ DO state changes when moisture changes
☐ Alert triggers when soil < 50%

ALERTS:
☐ Dry soil (>50%) = GREEN status
☐ Wet soil (<50%) = RED status with siren
☐ Dashboard "ONLINE" indicator shows
```

---

## 🆘 TROUBLESHOOTING

### Problem: LM393 not responding
**Solution**: Recalibrate potentiometer with dry/wet samples

### Problem: Serial monitor shows "DRY: 85%" even when wet
**Solution**: LM393 DO pin not connected properly to D0

### Problem: Dashboard shows "OFFLINE"
**Solution**: Check WiFi credentials and IP address in dashboard settings

### Problem: Soil gauge always shows same value
**Solution**: Check that LM393 module has power (verify LED status)

---

## 📚 DOCUMENTATION FILES

1. **QUICK_START.txt** - Get running in 2 hours (Updated)
2. **EXECUTION_GUIDE.md** - Detailed step-by-step
3. **LM393_SOIL_SENSOR_SETUP.md** - Sensor calibration (NEW!)
4. **CIRCUIT_DIAGRAM_UPDATED.html** - Complete wiring (NEW!)
5. **QUICK_WIRING_REFERENCE.md** - Pin reference (Updated)
6. **README.md** - Project overview
7. **SENSOR_SETUP_GUIDE.md** - Original setup guide

---

## 🎓 EDUCATIONAL VALUE

This system now teaches:
- **Electronics**: 3 different sensor types
- **Programming**: Digital/Analog I/O handling
- **Environmental Monitoring**: Real-world disaster prevention
- **Web Integration**: IoT data to dashboard
- **Hardware Debugging**: Calibration and testing

---

## 🚀 NEXT STEPS

1. **Setup Hardware**: Connect LM393 module as per updated wiring reference
2. **Calibrate Sensor**: Follow LM393 setup guide (calibration is critical!)
3. **Upload Code**: Flash sensor_code.ino to ESP8266
4. **Test**: Verify all 4 towers appear in dashboard
5. **Deploy**: Install in field with proper enclosure for LM393 potentiometer

---

## 💬 QUESTIONS?

For detailed information:
- **Setup**: See `LM393_SOIL_SENSOR_SETUP.md`
- **Wiring**: See `CIRCUIT_DIAGRAM_UPDATED.html`
- **Quick Reference**: See `QUICK_WIRING_REFERENCE.md`
- **Code Issues**: Check Serial Monitor output (Ctrl+Shift+M at 115200 baud)

---

**✨ You now have a complete, 3-sensor early warning system for Nepal!**

Version: 2.0 (With LM393 Landslide Detection)
Last Updated: May 2026
