/*
  RoadSense - ESP32 Companion Sketch
  ------------------------------------
  Two jobs, nothing else:
    1) Plays a continuous "heartbeat" pulse animation on an 8x8 MAX7219
       dot-matrix - purely decorative, always running.
    2) Listens on USB Serial for a "BUZZ" command from the Raspberry Pi
       and sounds the buzzer for a short moment when a near-miss is detected.

  Library required (install via Arduino IDE: Sketch > Include Library > Manage Libraries):
    "LedControl" by Eberhard Fahle

  Wiring (change the pin numbers below if you wired it differently):
    MAX7219 matrix:  DIN -> GPIO23, CLK -> GPIO18, CS -> GPIO5, VCC -> 5V, GND -> GND
    Buzzer:          + -> GPIO4, - -> GND
    Serial link:     just the USB cable to the Raspberry Pi - no extra wiring needed
*/

#include "LedControl.h"

// ---- Pins (change these if your wiring is different) ----
const int MATRIX_DIN = D7;
const int MATRIX_CLK = D5;
const int MATRIX_CS  = D8;
const int BUZZER_PIN = D6;

LedControl lc = LedControl(MATRIX_DIN, MATRIX_CLK, MATRIX_CS, 1);

// A simple 8x8 heart shape
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

// ---- Heartbeat pulse animation (non-blocking, uses millis()) ----
unsigned long lastPulseTime = 0;
int pulseBrightness = 1;
bool pulseGoingUp = true;
const int PULSE_INTERVAL_MS = 60;  // how fast the pulse fades in/out
const int PULSE_MIN = 1;
const int PULSE_MAX = 12;

// ---- Buzzer state (non-blocking) ----
bool buzzerActive = false;
unsigned long buzzerStartTime = 0;
const int BUZZER_DURATION_MS = 800;

String serialBuffer = "";

void setup() {
  Serial.begin(115200);

  lc.shutdown(0, false);        // wake the display up
  lc.setIntensity(0, PULSE_MIN);
  lc.clearDisplay(0);
  drawHeart();

  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);

  Serial.println("ESP32_READY");
}

void loop() {
  handleHeartbeat();
  handleSerialCommands();
  handleBuzzer();
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
