#include <WiFi.h>
#include <WebServer.h>
#include <WiFiManager.h>
#include <FirebaseESP32.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include "DHT.h"

// ---------------------------------------------------------
// FIREBASE DETAILS
// ---------------------------------------------------------
#define FIREBASE_HOST "smartagri-iot-d40cc-default-rtdb.firebaseio.com"
#define FIREBASE_AUTH "6My9kgn52mIw8YtAe25UOsk9zgBCXxBNZsP8QeMz"

// ---------------------------------------------------------
// EXACT PIN DEFINITIONS (Updated based on your wiring)
// ---------------------------------------------------------
#define DHTPIN 4           // DHT Sensor (D4)
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);

#define PH_PIN 32          // pH Sensor (D32)
#define LDR_PIN 35         // Light Sensor (D35)

// Soil Moisture Sensors
#define SOIL_RESISTIVE 33  // Fork wala (D33)
#define SOIL_CAPACITIVE 34 // Black wala (D34) -> Used for main reading

#define RAIN_PIN 39        // Rain Sensor (VN pin = GPIO 39)

// Ultrasonic Sensor
#define TRIG_PIN 13        // (D13)
#define ECHO_PIN 12        // (D12)

// RGB LED Pins
#define RGB_RED 25         // (D25)
#define RGB_GREEN 26       // (D26)
#define RGB_BLUE 27        // (D27)

// ---------------------------------------------------------
// OLED & GLOBAL OBJECTS
// ---------------------------------------------------------
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

FirebaseData fbdo;
FirebaseAuth auth;
FirebaseConfig config;
WebServer server(80);

// Global Variables
float t=0, h=0, phVal=0, distance=0;
int soilVal=0, ldrVal=0, rainVal=0;

// ---------------------------------------------------------
// LOCAL WEB SERVER DASHBOARD HTML (192.168.4.1)
// ---------------------------------------------------------
void handleRoot() {
  String html = "<html><head><meta http-equiv='refresh' content='3'>";
  html += "<style>body{font-family: Arial; background-color: #f4f4f9; text-align: center;}";
  html += "h1{color: #2c3e50;} .card{background: white; padding: 20px; margin: 10px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.2); display: inline-block; width: 200px;}</style></head><body>";
  html += "<h1>🌾 SmartAgri Local Dashboard</h1>";
  html += "<div class='card'><h2>Temp</h2><p style='font-size: 24px; color: red;'>" + String(t) + " &deg;C</p></div>";
  html += "<div class='card'><h2>Humidity</h2><p style='font-size: 24px; color: blue;'>" + String(h) + " %</p></div>";
  html += "<div class='card'><h2>pH Level</h2><p style='font-size: 24px; color: green;'>" + String(phVal) + "</p></div>";
  html += "<div class='card'><h2>Moisture</h2><p style='font-size: 24px; color: brown;'>" + String(soilVal) + " %</p></div>";
  html += "<div class='card'><h2>Light</h2><p style='font-size: 24px; color: orange;'>" + String(ldrVal) + " %</p></div>";
  html += "<div class='card'><h2>Rain</h2><p style='font-size: 24px; color: teal;'>" + String(rainVal) + " %</p></div>";
  html += "<div class='card'><h2>Water Lvl</h2><p style='font-size: 24px; color: navy;'>" + String(distance) + " cm</p></div>";
  html += "</body></html>";
  server.send(200, "text/html", html);
}

// ---------------------------------------------------------
// SETUP
// ---------------------------------------------------------
void setup() {
  Serial.begin(115200);
  
  // Initialize output pins
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(RGB_RED, OUTPUT);
  pinMode(RGB_GREEN, OUTPUT);
  pinMode(RGB_BLUE, OUTPUT);

  // Default RGB to OFF (Assuming Common Cathode, if Common Anode use HIGH)
  digitalWrite(RGB_RED, LOW);
  digitalWrite(RGB_GREEN, LOW);
  digitalWrite(RGB_BLUE, LOW);

  // OLED Setup
  Wire.begin();
  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println(F("SSD1306 allocation failed"));
  }
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(WHITE);
  display.setCursor(0, 10);
  display.println("Connect to Wi-Fi:");
  display.println("SmartAgri_Setup");
  display.display();

  dht.begin();

  // 1. DYNAMIC WI-FI MANAGER 
  WiFiManager wm;
  // wm.resetSettings(); // <-- Agar purana network bhulana ho toh isko uncomment karke upload karna ek baar
  
  bool res = wm.autoConnect("SmartAgri_Setup", "12345678"); 

  if(!res) {
    Serial.println("Failed to connect");
  } else {
    Serial.println("Connected to Internet!");
  }

  // 2. START LOCAL HOTSPOT
  WiFi.mode(WIFI_AP_STA);
  WiFi.softAP("SmartAgri_Local", "12345678");
  Serial.println("Local Hotspot Started! IP: 192.168.4.1");

  // 3. START WEB SERVER
  server.on("/", handleRoot);
  server.begin();

  // 4. FIREBASE SETUP
  config.host = FIREBASE_HOST;
  config.signer.tokens.legacy_token = FIREBASE_AUTH;
  Firebase.begin(&config, &auth);
  Firebase.reconnectWiFi(true);
}

// ---------------------------------------------------------
// MAIN LOOP
// ---------------------------------------------------------
void loop() {
  // Handle local dashboard requests
  server.handleClient();

  // --- SENSOR READINGS WITH ERROR CHECKING ---
  float tempRead = dht.readTemperature();
  float humRead = dht.readHumidity();

  // DHT22 Error Fix: Sirf tabhi update karo jab reading valid ho
  if (!isnan(tempRead)) {
    t = tempRead;
  } 
  if (!isnan(humRead)) {
    h = humRead;
  }

  // Raw Values Read
  int soilRaw = analogRead(SOIL_CAPACITIVE); 
  int ldrRaw = analogRead(LDR_PIN);
  int rainRaw = analogRead(RAIN_PIN);

  // Map 0-4095 raw data to 0-100% Percentage
  soilVal = map(soilRaw, 4095, 1000, 0, 100); 
  ldrVal  = map(ldrRaw, 4095, 0, 0, 100);      
  rainVal = map(rainRaw, 4095, 0, 0, 100);    

  // Constrain values exactly between 0 and 100
  soilVal = constrain(soilVal, 0, 100);
  ldrVal  = constrain(ldrVal, 0, 100);
  rainVal = constrain(rainVal, 0, 100);

  // pH Sensor Calculation
  int phRaw = analogRead(PH_PIN);
  float voltage = phRaw * (3.3 / 4095.0);
  phVal = 7.0 + ((2.5 - voltage) / 0.18);

  // Ultrasonic Sensor Calculation
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  long duration = pulseIn(ECHO_PIN, HIGH, 30000); 
  if(duration == 0) {
    distance = 0.0; 
  } else {
    distance = duration * 0.034 / 2;
  }

  // --- FIREBASE UPLOAD ---
  if (Firebase.ready()) {
    Firebase.setFloat(fbdo, "/SmartAgri/Temperature", t);
    Firebase.setFloat(fbdo, "/SmartAgri/Humidity", h);
    Firebase.setFloat(fbdo, "/SmartAgri/pH_Value", phVal);
    Firebase.setInt(fbdo, "/SmartAgri/SoilMoisture", soilVal);
    Firebase.setInt(fbdo, "/SmartAgri/LightLevel", ldrVal);
    Firebase.setInt(fbdo, "/SmartAgri/RainLevel", rainVal);
    Firebase.setFloat(fbdo, "/SmartAgri/WaterLevel", distance);
  }

// --- OLED DISPLAY ---
  display.clearDisplay();
  display.setCursor(0, 0);


  // --- MASTER RGB LOGIC (All Sensors Combined) ---
  
  // Condition 1: DANGER / CRITICAL (Red)
  if (soilVal < 30 || phVal < 5.0 || phVal > 8.5 || distance > 150) {
    digitalWrite(RGB_RED, HIGH);
    digitalWrite(RGB_GREEN, LOW);
    digitalWrite(RGB_BLUE, LOW);
  } 
  // Condition 2: WEATHER ALERT / OVER-WATERED (Blue)
  else if (rainVal > 60 || soilVal > 80 || ldrVal < 30) {
    digitalWrite(RGB_RED, LOW);
    digitalWrite(RGB_GREEN, LOW);
    digitalWrite(RGB_BLUE, HIGH);
  } 
  // Condition 3: OPTIMAL / ALL GOOD (Green)
  else {
    digitalWrite(RGB_RED, LOW);
    digitalWrite(RGB_GREEN, HIGH);
    digitalWrite(RGB_BLUE, LOW);
  }

  // Line 1: Temp & Humidity (Ek decimal place ke sath)
  display.print("T: "); display.print(t, 1); display.print("C | H: "); display.print(h, 0); display.println("%");
  
  // Line 2: pH & Moisture
  display.print("pH: "); display.print(phVal, 1); display.print(" | M: "); display.print(soilVal); display.println("%");
  
  // Line 3: Light & Rain
  display.print("Lgt: "); display.print(ldrVal); display.print("% | Rn: "); display.print(rainVal); display.println("%");
  
  // Line 4: Water Level
  display.print("Water: "); display.print(distance, 1); display.println(" cm");
  
  // Empty space ke liye
  display.println();
  
  // Line 6: Wi-Fi IP
  display.println("IP: 192.168.4.1"); 
  
  display.display();

  delay(2000); 
}