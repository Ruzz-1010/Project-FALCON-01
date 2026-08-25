#pragma once

#include <Arduino.h>

struct DashboardSnapshot {
  const char* system;
  uint8_t clients;
  uint32_t uptimeSeconds;
  bool monitoring;
  float battery;
  float temperature;
  float waveLevel;
  float waterPressure;
  const char* seaCondition;
  const char* gps;
  const char* solar;
  const char* security;
};

class SystemState {
 public:
  void begin(uint32_t bootTimeMs);
  DashboardSnapshot snapshot(uint32_t nowMs, uint8_t clients) const;
  bool toggleMonitoring();

 private:
  uint32_t bootTimeMs_ = 0;
  bool monitoringEnabled_ = true;
};
