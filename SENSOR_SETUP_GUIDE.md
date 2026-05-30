# NEPAL EWS - SENSOR SETUP GUIDE

## Components
- ESP8266MOD (WiFi Microcontroller)
- DHT11 (Temperature & Humidity Sensor)
- Water Level Sensor (Analog)
- Breadboard
- Jumper Wires (15x)
- Female Wires (5x)

---

## WIRING DIAGRAM

### ESP8266 Pinout
```
ESP8266MOD Pin Mapping:
- D0 = GPIO16
- D1 = GPIO5
- D2 = GPIO4
- D3 = GPIO0
- D4 = GPIO2  ← DHT11 DATA PIN (use this)
- D5 = GPIO14
- D6 = GPIO12
- D7 = GPIO13
- D8 = GPIO15
- RX = GPIO3
- TX = GPIO1
- A0 = Analog Input (Water Level Sensor)
- GND = Ground
- 3.3V = Power
- VIN = 5V Input (if using external power)
```

---

## CONNECTIONS

### 1. DHT11 Sensor Connection
```
DHT11 Pin 1 (VCC)     → ESP8266 3.3V
DHT11 Pin 2 (DATA)    → ESP8266 D4 (GPIO2)
DHT11 Pin 3 (GND)     → ESP8266 GND
DHT11 Pin 4 (NC)      → Not connected

Note: Place a 10kΩ pull-up resistor between Pin 2 (DATA) and VCC (optional but recommended)
```

### 2. Water Level Sensor Connection
```
Water Level Sensor:
- VCC (Red)           → ESP8266 3.3V
- GND (Black/Brown)   → ESP8266 GND
- Signal (Green/Blue) → ESP8266 A0 (Analog Input)

The analog output reads 0-1023 where:
- ~750 = Dry (no water)
- ~350 = Fully submerged
Adjust DRY_VALUE and WET_VALUE in code based on your sensor
```

### 3. Power Supply
```
USB Cable Method (Simple):
- Connect ESP8266 to computer via USB cable
- Powers from USB 5V
- Ground is shared

External Power Supply (Recommended):
- 5V Power Supply → ESP8266 VIN + GND
- Or 3.3V for lower power consumption
```

### 4. Breadboard Layout
```
Row 1:   ESP8266 3.3V → DHT11 VCC + Water Sensor VCC
Row 2:   ESP8266 GND  → DHT11 GND + Water Sensor GND
Row 3:   ESP8266 D4   → DHT11 DATA (with 10kΩ resistor to VCC)
Row 4:   ESP8266 A0   → Water Level Sensor Signal
```

---

## SETUP INSTRUCTIONS

### Step 1: Install Arduino IDE
1. Download Arduino IDE from https://www.arduino.cc/
2. Install it on your computer

### Step 2: Install ESP8266 Board Support
1. Open Arduino IDE
2. Go to File → Preferences
3. Add to "Additional Boards Manager URLs":
   `http://arduino.esp8266.com/stable/package_esp8266com_index.json`
4. Go to Tools → Board → Boards Manager
5. Search "ESP8266" and install "esp8266 by ESP8266 Community"

### Step 3: Install Required Libraries
1. Go to Sketch → Include Library → Manage Libraries
2. Install:
   - "DHT sensor library" by Adafruit
   - "Adafruit Unified Sensor" by Adafruit

### Step 4: Configure the Code
1. Open `sensor_code.ino` in Arduino IDE
2. Update WiFi credentials (Line ~10):
   ```cpp
   const char* ssid = "YOUR_WIFI_SSID";
   const char* password = "YOUR_WIFI_PASSWORD";
   ```
3. Adjust water level calibration if needed (Lines ~30-31):
   ```cpp
   const int DRY_VALUE = 750;    // Adjust based on sensor readings
   const int WET_VALUE = 350;    // Adjust based on sensor readings
   ```

### Step 5: Upload Code
1. Connect ESP8266 to computer via USB
2. Go to Tools → Board → select "NodeMCU 1.0" or "Generic ESP8266"
3. Go to Tools → Port → select the COM port
4. Click Upload (→ arrow button)
5. Wait for "Wrote X bytes" message

### Step 6: Verify Connection
1. Open Tools → Serial Monitor (Ctrl+Shift+M)
2. Set baud rate to 115200
3. You should see initialization messages and sensor readings
4. Note the IP address displayed

### Step 7: Connect Dashboard
1. Open the HTML dashboard file in your browser
2. Scroll to bottom left - find the IP Configuration panel
3. Replace "192.168.1.100" with the IP address from Step 6
4. Click "UPDATE IP"
5. Dashboard should now display live sensor data!

---

## SENSOR CALIBRATION

### Water Level Sensor
To calibrate for accurate readings:
1. Place sensor in air (dry): Note ADC value from Serial Monitor
2. Place sensor fully submerged: Note ADC value
3. Update these lines in code:
   ```cpp
   const int DRY_VALUE = YOUR_DRY_VALUE;     // e.g., 750
   const int WET_VALUE = YOUR_WET_VALUE;     // e.g., 350
   ```

### DHT11 Sensor
- Ensure 2 second delay between reads (already in code)
- Place in shaded area away from direct heat sources
- Humidity reading is used as soil moisture approximation

---

## API ENDPOINTS

The sensor provides these endpoints:

### 1. `/data` - Main Sensor Data (JSON)
```
Request:  GET http://192.168.X.X/data
Response: {
  "waterLevel": 2.45,
  "soilMoisture": 72.5,
  "temperature": 28.5,
  "humidity": 65.2,
  "rssi": -65
}
```

### 2. `/status` - System Status (JSON)
```
Request:  GET http://192.168.X.X/status
Response: {
  "status": "online",
  "ip": "192.168.X.X",
  "ssid": "WiFi_Network",
  "rssi": -65,
  "uptime": 3600
}
```

### 3. `/` - Web Interface
```
Request:  GET http://192.168.X.X/
Response: HTML page with current sensor values
```

---

## TROUBLESHOOTING

### Issue: ESP8266 won't connect to WiFi
- Verify SSID and password are correct
- Check if WiFi is 2.4GHz (ESP8266 only supports 2.4GHz, not 5GHz)
- Look at Serial Monitor for error messages
- Try moving closer to WiFi router

### Issue: DHT11 not reading
- Check data line has 10kΩ pull-up resistor
- Ensure DHT11 has 2-3 second delay between reads
- Verify power supply (must be 3.3V)
- Check wiring on breadboard

### Issue: Water sensor reading 0 or 1023
- Check analog signal wire connection to A0
- Calibrate DRY_VALUE and WET_VALUE
- Test with known water levels
- Verify sensor power supply

### Issue: Dashboard shows "Network Status: OFFLINE"
- Check IP address is correct
- Verify ESP8266 is connected to WiFi
- Check firewall isn't blocking connection
- Try accessing http://192.168.X.X in browser directly

### Issue: Frequent WiFi disconnections
- Check WiFi signal strength (RSSI should be > -70)
- Move ESP8266 closer to router
- Check for WiFi interference
- Reduce polling frequency in dashboard code

---

## MONITORING THRESHOLDS (in Dashboard)

Current settings:
- **Flood Threshold**: 4.0 meters (water level)
- **Landslide Threshold**: 50% (soil moisture - below triggers alert)

Adjust in HTML dashboard code (search for "FLOOD_THRESHOLD_DEFAULT" and "LANDSLIDE_THRESHOLD_DEFAULT")

---

## NEXT STEPS

1. Test water sensor with different water levels
2. Test DHT11 readings against a known thermometer
3. Verify all four tower cards populate with data in dashboard
4. Set appropriate alert thresholds for your specific location
5. Consider adding SD card logging for data persistence

---

## PINOUT REFERENCE

```
ESP8266 Pins Used:
D4 (GPIO2)   ← DHT11 Data Input
A0 (ADC0)    ← Water Level Sensor Analog Input
3.3V         ← Power for sensors
GND          ← Ground reference

Note: Some ESP8266 boards use slightly different pin numbering
Always refer to your specific board's pinout diagram
```
