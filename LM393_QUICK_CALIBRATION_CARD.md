# LM393 CALIBRATION QUICK CARD

## 🎯 CALIBRATION IN 5 MINUTES

```
╔════════════════════════════════════════════════════════════════════╗
║           LM393 SOIL MOISTURE SENSOR CALIBRATION GUIDE             ║
║                       QUICK REFERENCE CARD                         ║
╚════════════════════════════════════════════════════════════════════╝
```

---

## 🔧 WHAT YOU NEED

- ✅ LM393 Module (powered, connected to D0 & D1)
- ✅ Soil probe (2 metal pins from module)
- ✅ DRY sample (completely dry soil or sand)
- ✅ WET sample (saturated soil or pure water)
- ✅ Potentiometer (adjustment dial on module)
- ✅ LED on module (for visual feedback)

---

## ⚡ QUICK CALIBRATION STEPS

### STEP 1: PREPARE (30 seconds)
```
☐ Have DRY and WET samples ready
☐ Power on LM393 module
☐ Observe LED status:
  • ON (Red) = OK (threshold NOT met)
  • OFF (Dark) = needs adjustment
```

### STEP 2: DRY CALIBRATION (1 minute)
```
☐ Keep soil probe in AIR (not touching anything)
☐ Look at LED:
  
  IF LED is ON (Red):
    → DO NOT CHANGE POTENTIOMETER
    → Go to Step 3
  
  IF LED is OFF (Dark):
    → Slowly turn potentiometer CLOCKWISE ↻
    → Until LED turns ON
    → Stop here
```

### STEP 3: WET CALIBRATION (2 minutes)
```
☐ Insert soil probe into WET SOIL or WATER
☐ Immediately look at LED:
  
  IF LED turns OFF (Dark):
    → PERFECT! Calibration done ✓
    → Go to Step 4
  
  IF LED stays ON (Red):
    → Slowly turn potentiometer COUNTER-CLOCKWISE ↺
    → Until LED turns OFF
    → Stop here
    → Go back to Step 2 (verify dry still works)
```

### STEP 4: FINE-TUNE (1 minute)
```
Optional: Adjust sensitivity for your region

DRY soil test:
  ☐ Probe in normal/dry soil
  ☐ LED should be ON

WET soil test:
  ☐ Probe in heavily watered soil
  ☐ LED should be OFF

If you want EARLIER detection (more sensitive):
  ↺ Turn potentiometer COUNTER-CLOCKWISE slightly

If you want LATER detection (less sensitive):
  ↻ Turn potentiometer CLOCKWISE slightly
```

---

## ✅ VERIFICATION TEST

After calibration, test with 3 samples:

```
TEST 1: Dry Soil (Normal Conditions)
  Insert probe → Should NOT trigger alarm
  DO pin → HIGH (1) 
  Serial → "[SOIL] DO: HIGH (DRY)"
  LED → ON (Red)

TEST 2: Slightly Moist Soil (Light Rain)
  Insert probe → Should NOT trigger alarm
  DO pin → HIGH (1)
  Serial → "[SOIL] DO: HIGH (DRY)"
  LED → ON (Red)

TEST 3: Wet Soil (Heavy Rain/Waterlogged)
  Insert probe → SHOULD trigger alarm
  DO pin → LOW (0)
  Serial → "[SOIL] DO: LOW (WET)"
  LED → OFF (Dark)
  🚨 ALERT!
```

---

## 🔴 TROUBLESHOOTING DURING CALIBRATION

| Symptom | Cause | Fix |
|---------|-------|-----|
| LED won't turn ON | Potentiometer all the way wrong | Try turning clockwise fully, then counter-clockwise gradually |
| LED won't turn OFF | Same as above | Try turning counter-clockwise fully, then clockwise gradually |
| LED flickering | Moisture on sensor | Let probe dry, try again |
| No change at all | Module not powered | Check VCC and GND connections to 3.3V rail |
| Inverted behavior (ON when wet) | Sensor pins reversed | Try swapping the two probe pins |

---

## 📊 CALIBRATION CHECKLIST

```
Before Starting:
☐ LM393 module powered and mounted on breadboard
☐ D0 wire connected to ESP8266 D0
☐ D1 wire connected to ESP8266 D1
☐ Soil probe connected to module (internal)
☐ Potentiometer not stuck or damaged

During Calibration:
☐ DRY air test: LED ON
☐ WET water test: LED OFF
☐ Repeated tests: Consistent results
☐ No loose connections: All wires secured
☐ Probe pins: Clean, no corrosion

After Calibration:
☐ Arduino sketch uploaded with new pins
☐ Serial monitor shows [SOIL] readings
☐ Dashboard displays soil gauge
☐ Alarm test: Verify siren plays when triggered
☐ Documentation: Note your potentiometer position
```

---

## 🎯 EXPECTED BEHAVIOR AFTER CALIBRATION

### In Arduino Serial Monitor:

```
✓ NORMAL STATE (Dry Soil):
  [WATER] Raw ADC: 850 → Height: 0.00m
  [DHT] Temp: 28.5°C | Humidity: 65%
  [SOIL] DO: HIGH (DRY) → Moisture: 25.3%
  [SOIL] DO: HIGH (DRY) → Moisture: 26.1%
  [SOIL] DO: HIGH (DRY) → Moisture: 25.8%

✓ ALERT STATE (Wet Soil):
  [WATER] Raw ADC: 850 → Height: 0.00m
  [DHT] Temp: 28.5°C | Humidity: 65%
  [SOIL] DO: LOW  (WET) → Moisture: 72.4%
  [ALERT] Soil moisture CRITICAL - Below threshold (50%)
  [SOIL] DO: LOW  (WET) → Moisture: 73.1%
  [SOIL] DO: LOW  (WET) → Moisture: 72.8%
```

---

## 📱 DASHBOARD AFTER CALIBRATION

### T-04 Tower (Landslide Risk):

```
NORMAL CONDITIONS:
┌──────────────────┐
│ ✓ T-04 STABLE    │
│                  │
│ Soil: 28%        │
│ ████░░░░░░░░░░░░ │
│                  │
│ Slope: STABLE    │
│ ████████░░░░░░░░ │
│                  │
│ Status: OK       │
└──────────────────┘

ALERT CONDITIONS:
┌──────────────────┐
│ ⚠️ T-04 CRITICAL │
│                  │
│ Soil: 74%        │
│ ████████████████ │
│                  │
│ Slope: CRITICAL  │
│ ░░░░░░░░░░░░░░░░ │
│                  │
│ Status: DANGER   │
│ 🚨 Siren Active  │
└──────────────────┘
```

---

## 💡 PRO TIPS

1. **Document Your Calibration**: 
   - Write down potentiometer position
   - Helps recalibration if it shifts

2. **Seasonal Recalibration**:
   - Dry season: May need to recalibrate
   - After monsoon: Sensors may drift

3. **Field Testing**:
   - Carry wet/dry samples for quick verification
   - Test periodically (monthly if possible)

4. **Maintenance**:
   - Inspect probe for corrosion quarterly
   - Clean with soft brush if dirty
   - Replace if bent or damaged

5. **Backup Sensor**:
   - Consider deploying 2+ nodes in steep areas
   - Redundancy = better early warning

---

## 📞 STILL STUCK?

Check these files for more info:
- **Full Guide**: `LM393_SOIL_SENSOR_SETUP.md`
- **Circuit Diagram**: `CIRCUIT_DIAGRAM_UPDATED.html`
- **Wiring Reference**: `QUICK_WIRING_REFERENCE.md`
- **System Overview**: `SYSTEM_UPDATE_SUMMARY.md`

---

## ✨ ONCE CALIBRATED

Your system can now detect:
- 🌊 **Floods** → Water sensor → Alert at 4.0m
- 🏔️ **Landslides** → Soil sensor → Alert when <50% moisture
- 🌡️ **Weather** → DHT11 → Temperature & humidity context

**You're helping save lives in Nepal!** 🇳🇵
