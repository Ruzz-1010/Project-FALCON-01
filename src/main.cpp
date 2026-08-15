#include <Arduino.h>

#include "portal_server.h"
#include "sensor_diagnostics.h"

PortalServer portal;
SensorDiagnostics diagnostics;

void setup() {
  Serial.begin(115200);
  delay(500);

  Serial.println();
  Serial.println(F("===================================="));
  Serial.println(F("PROJECT FALCON-01"));
  Serial.println(F("Starting Sensor Node Portal..."));
  Serial.println(F("===================================="));

  if (!portal.begin()) {
    Serial.println(F("FATAL: Portal startup stopped."));
  }
  diagnostics.begin();
}

void loop() {
  portal.handleClient();
  diagnostics.tick(millis());
  delay(2);
}
