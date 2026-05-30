# NEPAL EWS - COMPLETE EXECUTION GUIDE

## PHASE 1: VERIFY YOUR CURRENT CONNECTIONS

Based on your breadboard images, let me help you verify and complete the wiring.

### ✅ What I see in your setup:
- ESP8266 LoLin board connected via USB
- Breadboard with some components arranged
- Power distribution rails (red/black lines visible)
- Component placement area

### 🔴 Complete Wiring Checklist

#### **Step 1: Power Distribution Setup**
```
ESP8266 to Breadboard:
┌─────────────────────────────────────────┐
│ ESP8266 Pinout (Your LoLin Board)      │
│ Top Rail:                               │
│ • 3V3 (3.3V) → Red Power Rail on Board │
│ • GND → Black Ground Rail on Board      │
│ • VIN (5V) → Optional extra power       │
└─────────────────────────────────────────┘

Your Board has USB power, so connect:
- 3V3 pin → Positive power rail (red)
- GND pin → Ground rail (black)
- This powers both sensors from ESP8266
```

#### **Step 2: DHT11 Connection (Temperature & Humidity)**
```
DHT11 Sensor (usually 4 pins: VCC, DATA, GND, NC)

Connection:
┌─────────────────────────────────────────┐
│ DHT11 Pin 1 (VCC) → Red Power Rail (3.3V)
│ DHT11 Pin 2 (DATA) → ESP8266 D4 (GPIO2)
│ DHT11 Pin 3 (GND) → Black Ground Rail
│ DHT11 Pin 4 (NC) → Leave unconnected
└─────────────────────────────────────────┘

OPTIONAL but RECOMMENDED:
- Add 10kΩ resistor between Pin 2 (DATA) and VCC
- This stabilizes the signal (pull-up resistor)
```

#### **Step 3: Water Level Sensor Connection**
```
Water Level Sensor (usually 3 pins: VCC, GND, Signal)

Connection:
┌─────────────────────────────────────────┐
│ Water Sensor VCC (Red) → Red Power Rail (3.3V)
│ Water Sensor GND (Black) → Black Ground Rail
│ Water Sensor Signal (Green/Yellow) → ESP8266 A0
└─────────────────────────────────────────┘

The A0 pin on ESP8266 reads analog voltage (0-1023)
```

### 📐 Your Breadboard Layout
```
BREADBOARD VISUAL LAYOUT:

        Col 1   Col 2   Col 3   Col 4   Col 5
Row 1 [ + ] ─ [ + ] ─ [ + ] ─ [ + ] ─ [ + ]  ← RED POWER RAIL (3.3V)
Row 2 [ - ] ─ [ - ] ─ [ - ] ─ [ - ] ─ [ - ]  ← BLACK GROUND RAIL

Row 3 [VCC]   [DHT]   [WATER] [GND]   [ESP]
      ├─ DHT11 Pin 1
      ├─ Water Sensor VCC
      └─ connects to power rail above

Row 4 [GND]   [DATA]  [SIG]   [GND]   [ESP]
      ├─ DHT11 Pin 3
      ├─ Water Sensor GND
      └─ connects to ground rail above

Row 5 [D4]    [D4]    [A0]    [GND]   [ESP]
      ├─ DHT11 Pin 2 → D4
      └─ Water Sensor Signal → A0

Connect to ESP8266:
D4 pin (GPIO2) for DHT11 data
A0 pin for Water Sensor analog
GND and 3V3 for power
```

---

## PHASE 2: SOFTWARE SETUP (Windows)

### Step 2.1: Download Arduino IDE
1. Go to: https://www.arduino.cc/en/software
2. Download "Arduino IDE" (not Arduino Create)
3. Run installer (accept all defaults)
4. Launch Arduino IDE

### Step 2.2: Add ESP8266 Board Support
```
In Arduino IDE:
1. Click: File → Preferences
2. Scroll to "Additional Boards Manager URLs"
3. Paste this URL:
   http://arduino.esp8266.com/stable/package_esp8266com_index.json
4. Click OK
5. Go to: Tools → Board → Boards Manager
6. Search: "esp8266"
7. Click "esp8266 by ESP8266 Community" → Install
8. Wait for installation (may take 1-2 minutes)
9. Close Boards Manager
```

### Step 2.3: Install Required Libraries
```
In Arduino IDE:
1. Go to: Sketch → Include Library → Manage Libraries
2. Search: "DHT" → Install "DHT sensor library" by Adafruit
3. When prompted, click "Install all" for dependencies
4. Search: "Adafruit Unified Sensor" → Install by Adafruit
5. Close Library Manager
```

### Step 2.4: Configure Your WiFi in Code
```
Open: sensor_code.ino

Find these lines (around line 10):
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

Replace with YOUR actual WiFi credentials:
Example:
const char* ssid = "MyHomeWiFi";
const char* password = "MyPassword123";

⚠️ IMPORTANT:
- WiFi must be 2.4GHz (ESP8266 doesn't support 5GHz)
- Use exact capitalization
- No spaces at the end
```

---

## PHASE 3: UPLOAD CODE TO ESP8266

### Step 3.1: Prepare ESP8266
1. Connect ESP8266 to computer via USB cable
2. Wait 3-5 seconds for driver installation
3. Open Device Manager (Windows+X → Device Manager)
4. Look for "USB-to-Serial" or "CH340" port
5. Note the COM port (e.g., COM3, COM5)

### Step 3.2: Configure Arduino IDE
```
In Arduino IDE:
1. Go to: Tools → Board → select "NodeMCU 1.0 (ESP8266)"
   (Your LoLin board is compatible)
2. Go to: Tools → Port → select your COM port (e.g., COM3)
3. Go to: Tools → Upload Speed → select 115200
4. Go to: Tools → CPU Frequency → 80 MHz
```

### Step 3.3: Upload Code
```
1. Open sensor_code.ino in Arduino IDE
2. Click the Upload button (→ arrow at top left)
3. You should see:
   - "Compiling sketch..."
   - "Uploading..."
   - Then progress bar fills up
4. FINAL MESSAGE: "Wrote 262144 bytes to file system"
   ✅ SUCCESS! Code is uploaded

If you get an error:
- Reconnect ESP8266 USB cable
- Try again
- Check COM port is correct
```

---

## PHASE 4: VERIFY SENSOR READINGS

### Step 4.1: Open Serial Monitor
```
In Arduino IDE:
1. Click: Tools → Serial Monitor
   (Or press Ctrl+Shift+M)
2. Set baud rate to 115200 (bottom right)
3. You should see output like:

═══════════════════════════════════════════════
  NEPAL EWS - SENSOR NODE INITIALIZATION
═══════════════════════════════════════════════
[INIT] DHT11 Sensor initialized
[INIT] Water Level Sensor initialized
[WIFI] Connecting to: MyHomeWiFi
.......... Connected!
[WIFI] IP Address: 192.168.X.XXX
[WIFI] Signal Strength: -65 dBm
[SERVER] Web server started on port 80

[WATER] Raw ADC: 650 → Height: 1.45m
[DHT] Temp: 28.5°C | Humidity: 65.2%
[API] Data request received → Sending JSON
```

### Step 4.2: Note Your ESP8266 IP Address
```
From Serial Monitor, find the line:
[WIFI] IP Address: 192.168.X.XXX

Example output:
[WIFI] IP Address: 192.168.1.105

WRITE THIS DOWN! You'll need it for the dashboard.
```

### Step 4.3: Test API Endpoint
```
1. Open your browser
2. Go to: http://192.168.X.XXX/data
   (Replace X.XXX with your actual IP)
3. You should see JSON like:
   {
     "waterLevel": 1.45,
     "soilMoisture": 65.2,
     "temperature": 28.5,
     "humidity": 65.2,
     "rssi": -65
   }

If you see this: ✅ ESP8266 is working!
If not: Check WiFi connection, reload page
```

---

## PHASE 5: CONNECT DASHBOARD TO ESP8266

### Step 5.1: Update Dashboard IP
```
1. Open: nepal_ews_dashboard (1).html in your browser
2. Wait for page to fully load
3. Scroll down to the IP Configuration panel
   (Bottom left corner)
4. Find the input field showing "192.168.1.100"
5. Replace it with YOUR ESP8266 IP (from Phase 4.2)
   Example: 192.168.1.105
6. Click "UPDATE IP" button
```

### Step 5.2: Verify Dashboard Connection
```
Look at the dashboard:
- "NETWORK STATUS" should show: ● ONLINE (green dot)
- Live gauge at top should show:
  * Water Level: (your sensor value) meters
  * Soil Moisture: (humidity) %
  * Signal: (RSSI) dBm

If OFFLINE:
1. Check IP address is correct
2. Reload the page (Ctrl+R or F5)
3. Check ESP8266 is connected to WiFi
4. Look at Serial Monitor for errors
```

---

## PHASE 6: CALIBRATE SENSORS (Optional but Recommended)

### Water Level Sensor Calibration
```
1. Keep sensor in dry air:
   - Look at Serial Monitor
   - Note the ADC value (e.g., 750)
   
2. Place sensor in water (shallow):
   - Look at Serial Monitor
   - Note the ADC value (e.g., 350)
   
3. Edit sensor_code.ino:
   - Find lines ~31-32:
     const int DRY_VALUE = 750;    // Change this
     const int WET_VALUE = 350;    // Change this
   - Replace with YOUR measured values
   
4. Re-upload the code
5. Test in water again - readings should be accurate
```

### Test Flood Alert
```
1. Place water sensor in shallow water (2 cm)
2. Dashboard should show water level around 0.5-1.0m
3. If > 4.0m threshold:
   - Alert banner appears
   - Siren sound plays
   - Cards turn red
   - Terminal shows "[CRITICAL]" message
```

---

## PHASE 7: TEST ALL FEATURES

### ✅ Checklist Before Submission
```
□ ESP8266 powers up (blue LED on)
□ WiFi connects (Serial Monitor shows IP)
□ Dashboard loads without errors
□ Network Status shows ONLINE
□ Water level updates in real-time
□ Soil moisture updates in real-time
□ Temperature shows reasonable value
□ Signal strength (RSSI) shows correctly
□ Graphs/sparklines animate
□ Alert triggers when threshold exceeded
□ Siren sound plays on alert
□ Modal popup shows hazard details
□ Terminal logs appear for each action
□ Can dismiss alert and return to normal
□ IP configuration panel works
```

---

## PHASE 8: TROUBLESHOOTING

### Problem: ESP8266 won't connect to WiFi
**Solution:**
- Check WiFi name (SSID) and password are EXACT
- Verify WiFi is 2.4GHz (not 5GHz)
- Try moving ESP8266 closer to router
- Restart ESP8266 (press RST button)
- Restart router
- Check Serial Monitor for error: [WIFI] Connection lost

### Problem: Sensor readings are stuck at same value
**Solution:**
- Check DHT11 wiring (especially DATA pin to D4)
- Check water sensor signal wire to A0
- Try waiting 10 seconds (DHT is slow)
- Restart ESP8266
- Check all jumper wires are fully inserted

### Problem: Dashboard shows OFFLINE but ESP8266 is online
**Solution:**
- Check IP address is CORRECT (copy-paste from Serial Monitor)
- Try accessing: http://192.168.X.XXX/ directly in browser
- If that works, update dashboard IP again
- Reload dashboard page (Ctrl+F5 hard refresh)
- Check firewall isn't blocking

### Problem: Water sensor shows 0 or 1023 constantly
**Solution:**
- Check signal wire connection to A0
- Verify sensor VCC is connected to 3.3V
- Try different jumper wire
- Calibrate sensor (Phase 6)
- Test with multimeter if available

### Problem: DHT11 not reading (shows default values)
**Solution:**
- Verify DATA pin connection to D4
- Add 10kΩ pull-up resistor (between DATA and VCC)
- Check VCC is 3.3V (not 5V!)
- Restart ESP8266
- Verify DHT sensor not defective

---

## PHASE 9: OPTIMIZE FOR HACKATHON DEMO

### Recommendations
```
1. Pre-program your WiFi credentials
2. Calibrate sensors before demo
3. Test on mobile hotspot as backup WiFi
4. Have Serial Monitor ready to show data
5. Prepare demo narrative:
   - "Water level monitored by analog sensor"
   - "Temperature/humidity via DHT11"
   - "Real-time alert system for floods/landslides"
   - "Multi-hazard detection for Nepal"

6. Optional enhancements for judges:
   - Add GPS coordinates (optional GPS module)
   - Add push notifications to Telegram/Email
   - Create mobile app connection
   - Historical data storage
```

---

## QUICK START REFERENCE

```
🔗 URL to test sensor: http://192.168.X.XXX/data
🔗 URL to dashboard: file:///C:/Users/rojan/OneDrive/Desktop/New%20folder/nepal_ews_dashboard%20(1).html

📝 Files you need:
   1. sensor_code.ino → Upload to ESP8266
   2. nepal_ews_dashboard.html → Open in browser
   3. SENSOR_SETUP_GUIDE.md → Reference

⚙️ Serial Monitor:
   - Baud: 115200
   - Shows: WiFi status, sensor readings, errors

🔌 USB cable:
   - Provides power to ESP8266
   - Enables code upload
   - Shows debug messages in Serial Monitor
```

---

## NEXT STEPS (Do in order)

1. ✅ **RIGHT NOW**: Verify physical connections match Phase 1
2. ✅ **INSTALL**: Arduino IDE (Phase 2)
3. ✅ **CONFIGURE**: WiFi credentials in code
4. ✅ **UPLOAD**: Code to ESP8266 (Phase 3)
5. ✅ **TEST**: Serial Monitor output (Phase 4)
6. ✅ **UPDATE**: Dashboard IP (Phase 5)
7. ✅ **VERIFY**: All features working (Phase 7)
8. ✅ **OPTIMIZE**: For hackathon presentation

---

## SUPPORT REFERENCE

**Arduino IDE Download:** https://www.arduino.cc/en/software
**ESP8266 Docs:** https://arduino-esp8266.readthedocs.io/
**DHT Library:** https://github.com/adafruit/DHT-sensor-library

**Common Errors:**
- "Board at 192.168.X.X is not available" → Check IP in dashboard config
- "Failed to connect" → Check WiFi credentials
- "DHT read failed" → Check wiring, add pull-up resistor
- "Port COM3 not found" → Check USB cable, reinstall drivers

Good luck with your hackathon! 🚀
