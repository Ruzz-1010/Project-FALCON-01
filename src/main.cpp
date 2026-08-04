#include <Arduino.h>

#include "portal_server.h"

PortalServer portal;

void setup() {
  Serial.begin(115200);
  delay(500);

  Serial.println();
  Serial.println(F("===================================="));
  Serial.println(F("PROJECT FALCON-01"));
  Serial.println(F("Starting Local Dashboard v2..."));
  Serial.println(F("===================================="));

  if (!portal.begin()) {
    Serial.println(F("FATAL: Portal startup stopped."));
  }
}

void loop() {
  portal.handleClient();
  delay(2);
}
