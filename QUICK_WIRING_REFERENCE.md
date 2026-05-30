# QUICK WIRING REFERENCE CARD

## 🔌 PIN CONNECTIONS AT A GLANCE

```
╔═══════════════════════════════════════════════════════════════════╗
║                    ESP8266 LOLIN BOARD PINOUT                     ║
║                                                                    ║
║  USB Power → ESP8266                                              ║
║     ↓                                                              ║
║   [USB] ────────────────────────────────────────────────────────  ║
║     │                                                              ║
║     ├─→ 3V3 (3.3V) ─────────→ RED POWER RAIL                     ║
║     │                                                              ║
║     └─→ GND ────────────────→ BLACK GROUND RAIL                  ║
║                                                                    ║
║  LEFT SIDE PINS (GPIO):                                           ║
║  ┌─────────────────┐                                              ║
║  │ D0  (GPIO16)    │                                              ║
║  │ D1  (GPIO5)     │                                              ║
║  │ D2  (GPIO4)     │                                              ║
║  │ D3  (GPIO0)     │                                              ║
║  │ D4  (GPIO2)  ◄─────────── DHT11 DATA PIN                     ║
║  │ D5  (GPIO14)    │                                              ║
║  │ D6  (GPIO12)    │                                              ║
║  │ D7  (GPIO13)    │                                              ║
║  │ D8  (GPIO15)    │                                              ║
║  └─────────────────┘                                              ║
║                                                                    ║
║  ANALOG INPUT:                                                    ║
║  ┌─────────────────┐                                              ║
║  │ A0 (ADC)   ◄────────────── WATER SENSOR SIGNAL               ║
║  └─────────────────┘                                              ║
║                                                                    ║
║  POWER & GROUND:                                                  ║
║  ┌─────────────────┐                                              ║
║  │ 3V3 (3.3V)      │ ──────→ Sensors VCC                         ║
║  │ GND             │ ──────→ Sensors GND                         ║
║  │ VIN (5V)        │ (optional backup power)                     ║
║  └─────────────────┘                                              ║
╚═══════════════════════════════════════════════════════════════════╝
```

## 🔋 POWER DISTRIBUTION

```
ESP8266 3V3 Pin (3.3V)
    ↓
    └─→ BREADBOARD RED RAIL (Positive Power Rail)
         ├─→ DHT11 Pin 1 (VCC)
         ├─→ Water Sensor VCC
         └─→ [Optional: Resistors, LEDs, etc.]

ESP8266 GND Pin
    ↓
    └─→ BREADBOARD BLACK RAIL (Ground Rail)
         ├─→ DHT11 Pin 3 (GND)
         ├─→ Water Sensor GND
         └─→ [All Ground connections]
```

## 📍 SENSOR CONNECTIONS

### DHT11 (Temperature & Humidity)
```
┌────────────────────────┐
│   DHT11 SENSOR         │
│ (View from front)      │
│                        │
│  Pin 1 (VCC)  ────────→ 3.3V POWER RAIL
│  Pin 2 (DATA) ────────→ ESP8266 D4
│  Pin 3 (GND)  ────────→ GROUND RAIL
│  Pin 4 (NC)   ────────→ NOT CONNECTED
│                        │
└────────────────────────┘

📌 RECOMMENDED:
Add 10kΩ resistor:
  From: DHT11 Pin 2 (DATA)
  To:   3.3V POWER RAIL
  (This is a pull-up resistor for stable signal)
```

### WATER LEVEL SENSOR
```
┌────────────────────────┐
│  WATER LEVEL SENSOR    │
│   (3-pin analog)       │
│                        │
│  VCC (Red)    ────────→ 3.3V POWER RAIL
│  GND (Black)  ────────→ GROUND RAIL
│  Signal (Green/Yellow) → ESP8266 A0
│                        │
└────────────────────────┘

⚠️ CRITICAL:
- DO NOT connect Signal to 5V
- Must use A0 (analog input) on ESP8266
- Sensor reads 0-1023 (0V to 3.3V)
```

## 🧩 BREADBOARD LAYOUT

```
Row numbers (vertical on left side)

      1      2      3      4      5     (Column markers)
      ▼      ▼      ▼      ▼      ▼
   ┌──────┬──────┬──────┬──────┬──────┐
   │ + + + │ + + + │ + + + │ + + + │ + + + │  ← RED RAIL (3.3V)
   │ - - - │ - - - │ - - - │ - - - │ - - - │  ← BLACK RAIL (GND)
   ├──────┼──────┼──────┼──────┼──────┤
   │      │      │      │      │      │  
   │[DHT] │[DHT] │[WATER]│[R]   │[ESP8]│  <- Row 3
   │ VCC  │ DATA │ VCC   │ 10k  │ 3V3 │
   ├──────┼──────┼──────┼──────┼──────┤
   │      │      │      │      │      │
   │[JUMP]│[D4]  │[A0]  │[GND] │[ESP8]│  <- Row 4
   │ GND  │      │      │      │ GND  │
   ├──────┼──────┼──────┼──────┼──────┤
   │      │      │      │      │      │
   │[DHT] │[R]   │[WATE]│      │      │  <- Row 5
   │ GND  │ to   │ GND  │      │      │
   │      │ VCC  │      │      │      │
   └──────┴──────┴──────┴──────┴──────┘

Legend:
[DHT]  = DHT11 Sensor legs
[WATE] = Water Sensor legs
[R]    = Resistor
[ESP8] = Connections going to ESP8266
```

## 📊 SIGNAL FLOW

```
SENSORS → ESP8266 → WiFi → DASHBOARD
  ↓         ↓        ↓        ↓
Water   Reads     Sends     Shows
Level   Analog    JSON      Gauges
        Value     Data
  
DHT11 → D4 (GPIO2) → Reads temperature/humidity every 2 sec
Water  → A0 (ADC)  → Reads water level constantly
  ↓        ↓          ↓
3.3V   Processes    Creates
Supply Combined     JSON
       Data
```

## ⚡ VOLTAGE LEVELS

```
Sensor Power Supply:
├─ 3.3V (from ESP8266) ─→ Safe for DHT11 & Water Sensor
├─ 5V ─────────────────→ ⚠️ DO NOT USE (damages DHT11)
└─ 1.5V (batteries) ───→ TOO LOW (won't work)

Signal Levels:
├─ D4 (Digital GPIO) ──→ 0V or 3.3V (HIGH/LOW)
├─ A0 (Analog ADC) ────→ 0V to 3.3V (0 to 1023)
└─ Serial Comm ────────→ 3.3V logic level
```

## 🔌 JUMPER WIRE TYPES

```
Your Components:
├─ 15x Jumper Wires (typical bundle)
│  ├─ Male-to-Male (M-M) ─→ For breadboard connections
│  └─ Female-to-Female (F-F) ─→ For sensor header pins
│
├─ 5x Female Wires
│  ├─ Female-to-Male (F-M) ─→ For direct sensor connections
│  └─ Female-to-Female (F-F) ─→ For breadboard extensions
│
└─ Total: Enough for all connections + extras
```

## 🎯 CONNECTION SUMMARY

| Component | From Pin | To ESP8266 | Wire Color |
|-----------|----------|------------|-----------|
| DHT11 VCC | Pin 1 | 3V3 | RED |
| DHT11 DATA | Pin 2 | D4 (GPIO2) | YELLOW |
| DHT11 GND | Pin 3 | GND | BLACK |
| Water VCC | VCC | 3V3 | RED |
| Water GND | GND | GND | BLACK |
| Water Signal | SIG | A0 | GREEN |
| Pull-up R | 10kΩ | Between D4 & 3V3 | Any |

## ✅ PRE-UPLOAD CHECKLIST

- [ ] All jumper wires fully inserted (not loose)
- [ ] DHT11 has 4 pins connected (no loose pins)
- [ ] Water sensor has 3 pins connected
- [ ] Pull-up resistor installed (DHT DATA to VCC)
- [ ] ESP8266 powered via USB (blue LED on)
- [ ] No visible wire shorts or bridges
- [ ] All connections match table above
- [ ] Breadboard rails show no corrosion
- [ ] Sensors not damaged or wet

## 🚀 NEXT: PROCEED TO PHASE 2 (SOFTWARE SETUP)

See: EXECUTION_GUIDE.md → PHASE 2
```

---

## 🎓 UNDERSTANDING THE CIRCUIT

```
Power Supply:
USB 5V → ESP8266 Voltage Regulator → 3.3V
           (onboard regulator)

Data Reading Loop:
1. ESP8266 reads DHT11 on D4 pin
   └─ Temperature: 0-50°C
   └─ Humidity: 0-100%

2. ESP8266 reads Water on A0 pin (analog 0-1023 → 0-3.3V)
   └─ Converts to water height (0-8 meters)

3. ESP8266 combines both readings into JSON

4. Browser requests /data endpoint

5. ESP8266 sends JSON to dashboard

6. Dashboard displays real-time gauges

7. If thresholds exceeded → ALERT!
```

---

## 📱 FILE LOCATIONS

```
Your Project Directory:
C:\Users\rojan\OneDrive\Desktop\New folder\
  ├─ nepal_ews_dashboard (1).html ............ Open in browser
  ├─ sensor_code.ino ........................ Upload to ESP8266
  ├─ SENSOR_SETUP_GUIDE.md .................. Reference
  ├─ EXECUTION_GUIDE.md ..................... Step-by-step guide
  └─ QUICK_WIRING_REFERENCE.md ............. (This file)
```
