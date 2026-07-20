/*
  RoadSense - ESP8266 Companion + GPS Test
  -----------------------------------------
  - Heartbeat pulse animation on 8x8 MAX7219
  - Buzzer on "BUZZ" command from Raspberry Pi
  - GPS (NEO-6M) on D2 – NMEA sentences printed to Serial
    (just for testing; remove when you know it works)

  Wiring:
    MAX7219:  DIN -> D7, CLK -> D5, CS -> D8, VCC -> 5V, GND -> GND
    Buzzer:   + -> D6, - -> GND
    GPS:      VCC -> 3V3, GND -> GND, TX -> D2 (RX left unconnected)

  Serial link: USB cable to the Pi (115200 baud)
*/

#include "LedControl.h"
#include <SoftwareSerial.h>

// ---- Pins ----
const int MATRIX_DIN = D7;
const int MATRIX_CLK = D5;
const int MATRIX_CS  = D8;
const int BUZZER_PIN = D6;
const int GPS_RX     = D2;   // GPS TX connected here
const int GPS_TX     = D1;   // not used, but SoftwareSerial needs a TX pin

// GPS software serial (D2 = RX, D1 = TX)
SoftwareSerial gpsSerial(GPS_RX, GPS_TX);

LedControl lc = LedControl(MATRIX_DIN, MATRIX_CLK, MATRIX_CS, 1);

// Heart shape
byte heart[8] = {
  0b01100110,
  0b11111111,
  0b11111111,
  0b11111111,
  0b01111110,
  0b00111100,
  0b00011000,
  0b00000000
};

// ---- Heartbeat pulse ----
unsigned long lastPulseTime = 0;
int pulseBrightness = 1;
bool pulseGoingUp = true;
const int PULSE_INTERVAL_MS = 60;
const int PULSE_MIN = 1;
const int PULSE_MAX = 12;

// ---- Buzzer state ----
bool buzzerActive = false;
unsigned long buzzerStartTime = 0;
const int BUZZER_DURATION_MS = 800;

String serialBuffer = "";

void setup() {
  Serial.begin(115200);        // main Serial to Pi
  gpsSerial.begin(9600);       // GPS at 9600 baud

  lc.shutdown(0, false);
  lc.setIntensity(0, PULSE_MIN);
  lc.clearDisplay(0);
  drawHeart();

  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);

  Serial.println("ESP8266_READY");
}

void loop() {
  handleHeartbeat();
  handleSerialCommands();
  handleBuzzer();
  handleGPS();                  // forward GPS data to Serial
}

void drawHeart() {
  for (int row = 0; row < 8; row++) {
    for (int col = 0; col < 8; col++) {
      bool on = bitRead(heart[row], 7 - col);
      lc.setLed(0, row, col, on);
    }
  }
}

void handleHeartbeat() {
  unsigned long now = millis();
  if (now - lastPulseTime >= PULSE_INTERVAL_MS) {
    lastPulseTime = now;
    if (pulseGoingUp) {
      pulseBrightness++;
      if (pulseBrightness >= PULSE_MAX) pulseGoingUp = false;
    } else {
      pulseBrightness--;
      if (pulseBrightness <= PULSE_MIN) pulseGoingUp = true;
    }
    lc.setIntensity(0, pulseBrightness);
  }
}

void handleSerialCommands() {
  while (Serial.available() > 0) {
    char c = Serial.read();
    if (c == '\n') {
      serialBuffer.trim();
      if (serialBuffer == "BUZZ") {
        buzzerActive = true;
        buzzerStartTime = millis();
        digitalWrite(BUZZER_PIN, HIGH);
        Serial.println("ACK_BUZZ");
      }
      serialBuffer = "";
    } else {
      serialBuffer += c;
    }
  }
}

void handleBuzzer() {
  if (buzzerActive && (millis() - buzzerStartTime >= BUZZER_DURATION_MS)) {
    digitalWrite(BUZZER_PIN, LOW);
    buzzerActive = false;
  }
}

// ---- GPS passthrough for testing ----
void handleGPS() {
  while (gpsSerial.available()) {
    Serial.write(gpsSerial.read());
  }
}