#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
#include <DHT.h>

// ── WiFi credentials ──────────────────────────────────────
const char* WIFI_SSID     = "OnePlus Nord";   // <-- change this
const char* WIFI_PASSWORD = "howareuman";   // <-- change this

// ── Backend URL (your laptop IP) ──────────────────────────
const char* SERVER_URL = "http://10.12.4.32:5000/post-data";

// ── Pin definitions ───────────────────────────────────────
#define DHT_PIN        D4   // DHT11 data pin
#define DHT_TYPE       DHT11
#define SOIL_SELECT    D5   // Digital pin to switch A0 between sensors
                            // HIGH = read soil, LOW = read water level
// Both soil moisture signal and water level share A0 via a toggle pin
// If you only have one analog sensor at a time, just comment out the toggle logic

// ── Sensor read interval ──────────────────────────────────
const unsigned long INTERVAL_MS = 5000; // 5 seconds

DHT dht(DHT_PIN, DHT_TYPE);
WiFiClient wifiClient;

// ─────────────────────────────────────────────────────────

void setup() {
  Serial.begin(115200);
  delay(100);

  pinMode(SOIL_SELECT, OUTPUT);
  dht.begin();

  Serial.println("\n\n== Nepal EWS Sensor Node ==");
  Serial.print("Connecting to WiFi: ");
  Serial.println(WIFI_SSID);

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi connected!");
  Serial.print("ESP8266 IP: ");
  Serial.println(WiFi.localIP());
  Serial.print("Sending data to: ");
  Serial.println(SERVER_URL);
  Serial.println("=========================\n");
}

// ─────────────────────────────────────────────────────────

int readSoilMoisture() {
  digitalWrite(SOIL_SELECT, HIGH); // route A0 to soil sensor
  delay(100);                      // settle time
  return analogRead(A0);
}

int readWaterLevel() {
  digitalWrite(SOIL_SELECT, LOW);  // route A0 to water level sensor
  delay(100);
  return analogRead(A0);
}

void sendData(int soil, int water, float temp, float hum) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("[ERROR] WiFi disconnected, skipping send");
    return;
  }

  HTTPClient http;
  http.begin(wifiClient, SERVER_URL);
  http.addHeader("Content-Type", "application/json");

  // Build JSON string manually (no ArduinoJson needed)
  String payload = "{";
  payload += "\"soil_moisture\":"  + String(soil)         + ",";
  payload += "\"water_level\":"    + String(water)        + ",";
  payload += "\"temperature\":"    + String(temp, 1)      + ",";
  payload += "\"humidity\":"       + String(hum, 1);
  payload += "}";

  Serial.print("[POST] ");
  Serial.println(payload);

  int httpCode = http.POST(payload);

  if (httpCode == 200) {
    String response = http.getString();
    Serial.print("[OK] Server: ");
    Serial.println(response);
  } else {
    Serial.print("[ERROR] HTTP code: ");
    Serial.println(httpCode);
  }

  http.end();
}

// ─────────────────────────────────────────────────────────

void loop() {
  static unsigned long lastSend = 0;

  if (millis() - lastSend >= INTERVAL_MS) {
    lastSend = millis();

    // Read DHT11
    float temperature = dht.readTemperature();
    float humidity    = dht.readHumidity();

    if (isnan(temperature) || isnan(humidity)) {
      Serial.println("[WARN] DHT11 read failed, using 0");
      temperature = 0;
      humidity    = 0;
    }

    // Read analog sensors (toggle between the two)
    int soilRaw  = readSoilMoisture();
    int waterRaw = readWaterLevel();

    Serial.printf("[READ] soil=%d  water=%d  temp=%.1f°C  hum=%.1f%%\n",
                  soilRaw, waterRaw, temperature, humidity);

    sendData(soilRaw, waterRaw, temperature, humidity);
  }
}
