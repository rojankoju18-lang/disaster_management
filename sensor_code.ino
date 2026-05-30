#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include "DHT.h"

// ═══════════════════════════════════════════════
// WIFI CONFIGURATION
// ═══════════════════════════════════════════════
const char* ssid = "STWCU_LR-11";           // Change to your WiFi name
const char* password = "";   // Change to your WiFi password

// ═══════════════════════════════════════════════
// SENSOR PIN CONFIGURATION
// ═══════════════════════════════════════════════
#define DHT_PIN D4              // DHT11 data pin (GPIO2)
#define DHTTYPE DHT11           // DHT 11 sensor type
#define WATER_LEVEL_PIN A0      // Water level sensor (Analog pin)
#define SOIL_SENSOR_PIN D0      // LM393 soil moisture sensor (Digital pin - GPIO16)

DHT dht(DHT_PIN, DHTTYPE);
ESP8266WebServer server(80);

// ═══════════════════════════════════════════════
// GLOBAL VARIABLES
// ═══════════════════════════════════════════════
float waterLevel = 0.0;
float soilMoisture = 0.0;
float temperature = 0.0;
float humidity = 0.0;
int signalStrength = 0;

// Water level calibration values (adjust based on your sensor)
const int DRY_VALUE = 750;      // ADC value when sensor is dry
const int WET_VALUE = 350;      // ADC value when sensor is fully submerged
const float MAX_WATER_HEIGHT = 8.0;  // Maximum water height in meters

// Soil moisture sensor thresholds
// LM393 digital output: LOW (0) = Soil is WET (moisture > threshold)
//                      HIGH (1) = Soil is DRY (moisture < threshold)
const int SOIL_MOISTURE_THRESHOLD = 50;  // Threshold percentage (0-100%)

// ═══════════════════════════════════════════════
// SETUP
// ═══════════════════════════════════════════════
void setup() {
  Serial.begin(115200);
  delay(100);
  
  Serial.println("\n\n");
  Serial.println("═══════════════════════════════════════════════");
  Serial.println("  NEPAL EWS - SENSOR NODE INITIALIZATION");
  Serial.println("═══════════════════════════════════════════════");
  
  // Initialize DHT sensor
  dht.begin();
  Serial.println("[INIT] DHT11 Sensor initialized");
  
  // Configure analog pin for water level
  pinMode(WATER_LEVEL_PIN, INPUT);
  Serial.println("[INIT] Water Level Sensor initialized");
  
  // Configure digital pin for soil moisture sensor
  pinMode(SOIL_SENSOR_PIN, INPUT);
  Serial.println("[INIT] LM393 Soil Moisture Sensor initialized");
  
  // Connect to WiFi
  connectToWiFi();
  
  // Setup web server endpoints
  setupWebServer();
  
  Serial.println("[SYSTEM] Setup complete - Ready to stream data");
}

// ═══════════════════════════════════════════════
// WIFI CONNECTION
// ═══════════════════════════════════════════════
void connectToWiFi() {
  Serial.print("[WIFI] Connecting to: ");
  Serial.println(ssid);
  
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println(" Connected!");
    Serial.print("[WIFI] IP Address: ");
    Serial.println(WiFi.localIP());
    Serial.print("[WIFI] Signal Strength: ");
    Serial.print(WiFi.RSSI());
    Serial.println(" dBm");
  } else {
    Serial.println(" Failed to connect!");
  }
}

// ═══════════════════════════════════════════════
// WEB SERVER SETUP
// ═══════════════════════════════════════════════
void setupWebServer() {
  // Main data endpoint
  server.on("/data", HTTP_GET, handleDataRequest);
  
  // Status endpoint
  server.on("/status", HTTP_GET, handleStatusRequest);
  
  // Root endpoint
  server.on("/", HTTP_GET, handleRoot);
  
  server.begin();
  Serial.println("[SERVER] Web server started on port 80");
}

// ═══════════════════════════════════════════════
// SENSOR READING FUNCTIONS
// ═══════════════════════════════════════════════

// Read water level sensor (analog)
float readWaterLevel() {
  int rawValue = analogRead(WATER_LEVEL_PIN);
  
  // Convert analog reading to water height (0-8 meters)
  // Calibration: DRY_VALUE = 0m, WET_VALUE = 8m
  float percentage = (float)(DRY_VALUE - rawValue) / (DRY_VALUE - WET_VALUE);
  percentage = constrain(percentage, 0.0, 1.0);  // Limit to 0-100%
  
  float height = percentage * MAX_WATER_HEIGHT;
  
  Serial.print("[WATER] Raw ADC: ");
  Serial.print(rawValue);
  Serial.print(" → Height: ");
  Serial.print(height, 2);
  Serial.println("m");
  
  return height;
}

// Read DHT11 sensor (temperature & humidity)
void readDHTSensor() {
  // DHT11 is slow - add delay between readings
  delay(2000);
  
  temperature = dht.readTemperature();
  humidity = dht.readHumidity();
  
  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("[DHT] Sensor read failed!");
    temperature = 25.0;   // Default values
    humidity = 50.0;
  } else {
    Serial.print("[DHT] Temp: ");
    Serial.print(temperature, 1);
    Serial.print("°C | Humidity: ");
    Serial.print(humidity, 0);
    Serial.println("%");
  }
}

// Read LM393 soil moisture sensor (digital)
float readSoilMoisture() {
  int sensorValue = digitalRead(SOIL_SENSOR_PIN);
  
  // LM393 output:
  // LOW (0) = Moisture detected (wet soil) → High percentage
  // HIGH (1) = No moisture (dry soil) → Low percentage
  
  if (sensorValue == LOW) {
    soilMoisture = 85.0;  // Soil is wet
    Serial.println("[SOIL] Sensor: WET (85%)");
  } else {
    soilMoisture = 25.0;  // Soil is dry
    Serial.println("[SOIL] Sensor: DRY (25%)");
  }
  
  return soilMoisture;
}

// Get WiFi signal strength (RSSI in dBm)
int getSignalStrength() {
  signalStrength = WiFi.RSSI();
  return signalStrength;
}

// ═══════════════════════════════════════════════
// WEB REQUEST HANDLERS
// ═══════════════════════════════════════════════

// Main data endpoint - returns JSON with sensor readings
void handleDataRequest() {
  // Read all sensors
  waterLevel = readWaterLevel();
  readDHTSensor();
  readSoilMoisture();
  signalStrength = getSignalStrength();
  
  // Build JSON response
  String json = "{";
  json += "\"waterLevel\":" + String(waterLevel, 2) + ",";
  json += "\"soilMoisture\":" + String(soilMoisture, 1) + ",";
  json += "\"temperature\":" + String(temperature, 1) + ",";
  json += "\"humidity\":" + String(humidity, 1) + ",";
  json += "\"rssi\":" + String(signalStrength);
  json += "}";
  
  Serial.println("[API] Data request received → Sending JSON");
  
  server.sendHeader("Access-Control-Allow-Origin", "*");
  server.send(200, "application/json", json);
}

// Status endpoint
void handleStatusRequest() {
  String json = "{";
  json += "\"status\":\"online\",";
  json += "\"ip\":\"" + WiFi.localIP().toString() + "\",";
  json += "\"ssid\":\"" + String(ssid) + "\",";
  json += "\"rssi\":" + String(WiFi.RSSI()) + ",";
  json += "\"uptime\":" + String(millis() / 1000);
  json += "}";
  
  server.sendHeader("Access-Control-Allow-Origin", "*");
  server.send(200, "application/json", json);
}

// Root endpoint
void handleRoot() {
  String html = "<html><body>";
  html += "<h1>Nepal EWS Sensor Node</h1>";
  html += "<p>Water Level: " + String(waterLevel, 2) + " m</p>";
  html += "<p>Soil Moisture: " + String(soilMoisture, 1) + " %</p>";
  html += "<p>Temperature: " + String(temperature, 1) + " °C</p>";
  html += "<p>Signal: " + String(signalStrength) + " dBm</p>";
  html += "</body></html>";
  
  server.send(200, "text/html", html);
}

// ═══════════════════════════════════════════════
// MAIN LOOP
// ═══════════════════════════════════════════════
void loop() {
  // Handle incoming web requests
  server.handleClient();
  
  // Keep WiFi connected
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("[WIFI] Connection lost - Reconnecting...");
    connectToWiFi();
  }
  
  delay(100);
}
