#pragma once

#include <Arduino.h>

class SensorDiagnostics {
 public:
  void begin();
  void tick(uint32_t nowMs);

 private:
  bool addressPresent(uint8_t address);
  void printInventory();
  void emitTelemetry(uint32_t nowMs);

  HardwareSerial gps_{2};
  uint32_t lastTelemetryMs_ = 0;
  uint32_t lastGpsByteMs_ = 0;
  uint32_t sequence_ = 0;
};
