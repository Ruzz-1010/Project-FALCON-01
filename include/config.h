#pragma once

#include <Arduino.h>

namespace FalconConfig {

constexpr char kApSsid[] = "FALCON-01";
constexpr char kApPassword[] = "falcon123";
constexpr uint16_t kHttpPort = 80;
constexpr uint16_t kDnsPort = 53;
constexpr uint8_t kApChannel = 6;
constexpr uint8_t kMaxConnections = 4;

constexpr char kIndexPath[] = "/index.html";
constexpr char kStylePath[] = "/style.css";
constexpr char kScriptPath[] = "/app.js";
constexpr char kLogoPath[] = "/falcon-logo.jpg";

constexpr char kStatusApiPath[] = "/api/status";
constexpr char kMonitoringApiPath[] = "/api/monitoring/toggle";
constexpr char kRestartApiPath[] = "/api/restart";
constexpr uint32_t kRestartDelayMs = 700;

// Phase 1 prototype pin allocation. Keep synchronized with docs/PINOUT.md.
constexpr uint8_t kI2cSdaPin = 21;
constexpr uint8_t kI2cSclPin = 22;
constexpr uint8_t kBnoSckPin = 18;
constexpr uint8_t kBnoMisoPin = 19;
constexpr uint8_t kBnoMosiPin = 23;
constexpr uint8_t kBnoCsPin = 13;
constexpr uint8_t kBnoIntPin = 27;
constexpr uint8_t kBnoResetPin = 14;
constexpr uint8_t kGpsRxPin = 16;
constexpr uint8_t kGpsTxPin = 17;
constexpr uint8_t kAnemometerPin = 25;
constexpr uint8_t kWaterTemperaturePin = 26;
constexpr uint8_t kLeakPin = 32;
constexpr uint8_t kFanPwmPin = 33;
constexpr uint8_t kFan1TachPin = 34;
constexpr uint8_t kFan2TachPin = 35;
constexpr uint32_t kFanPwmFrequencyHz = 25000;
constexpr uint8_t kBar02Address = 0x76;
constexpr uint8_t kBatteryMonitorAddress = 0x40;
constexpr uint8_t kSolarMonitorAddress = 0x41;
constexpr uint8_t kEnclosureTemperatureAddress = 0x18;
constexpr uint8_t kWindAdcAddress = 0x48;
constexpr uint32_t kTelemetryIntervalMs = 2000;

}  // namespace FalconConfig
