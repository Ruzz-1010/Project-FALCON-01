// Project FALCON GPS diagnostic sketch
// NEO-6M / GY-GPS6MV2: VCC=5V/VIN, GND=GND, TX=GPIO16 (ESP32 RX2),
// RX=GPIO17 (ESP32 TX2, optional).

#include <Arduino.h>

HardwareSerial gps(2);
static constexpr int GPS_RX = 16;
static constexpr int GPS_TX = 17;

void setup() {
  Serial.begin(115200);
  delay(500);
  Serial.println();
  Serial.println("FALCON GPS diagnostic");
  Serial.println("GPS UART: RX16 / TX17 at 9600 baud");
  gps.begin(9600, SERIAL_8N1, GPS_RX, GPS_TX);
}

void loop() {
  while (gps.available()) {
    Serial.write(gps.read());
  }
}
