#include "system_state.h"

namespace {

// Centralized simulated readings are replaced here as sensor drivers come online.
constexpr float kDemoBattery = 94.0F;
constexpr float kDemoTemperature = 28.6F;
constexpr float kDemoTilt = 2.4F;
constexpr float kDemoWaveLevel = 0.3F;

}  // namespace

void SystemState::begin(uint32_t bootTimeMs) { bootTimeMs_ = bootTimeMs; }

DashboardSnapshot SystemState::snapshot(uint32_t nowMs,
                                        uint8_t clients) const {
  return {"ONLINE",
          clients,
          (nowMs - bootTimeMs_) / 1000UL,
          monitoringEnabled_,
          kDemoBattery,
          kDemoTemperature,
          kDemoTilt,
          kDemoWaveLevel,
          "CALM",
          "WAITING FOR GPS",
          "STANDBY",
          "ARMED"};
}

bool SystemState::toggleMonitoring() {
  monitoringEnabled_ = !monitoringEnabled_;
  return monitoringEnabled_;
}
