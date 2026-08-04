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

}  // namespace FalconConfig
