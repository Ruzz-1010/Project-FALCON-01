#include "sensor_diagnostics.h"

#include <SPI.h>
#include <Wire.h>

#include "config.h"

namespace {

const char* state(bool present) {
  return present ? "DETECTED" : "NOT_DETECTED";
}

}  // namespace

void SensorDiagnostics::begin() {
  Wire.begin(FalconConfig::kI2cSdaPin, FalconConfig::kI2cSclPin);
  SPI.begin(FalconConfig::kBnoSckPin, FalconConfig::kBnoMisoPin,
            FalconConfig::kBnoMosiPin, FalconConfig::kBnoCsPin);
  pinMode(FalconConfig::kBnoCsPin, OUTPUT);
  digitalWrite(FalconConfig::kBnoCsPin, HIGH);
  pinMode(FalconConfig::kBnoResetPin, OUTPUT);
  digitalWrite(FalconConfig::kBnoResetPin, HIGH);
  pinMode(FalconConfig::kBnoIntPin, INPUT_PULLUP);
  pinMode(FalconConfig::kAnemometerPin, INPUT_PULLUP);
  pinMode(FalconConfig::kLeakPin, INPUT_PULLUP);
  pinMode(FalconConfig::kFanPwmPin, OUTPUT);
  digitalWrite(FalconConfig::kFanPwmPin, LOW);
  gps_.begin(9600, SERIAL_8N1, FalconConfig::kGpsRxPin,
             FalconConfig::kGpsTxPin);
  printInventory();
}

bool SensorDiagnostics::addressPresent(uint8_t address) {
  Wire.beginTransmission(address);
  return Wire.endTransmission() == 0;
}

void SensorDiagnostics::printInventory() {
  Serial.println(F("[DIAG] FALCON Phase 1 hardware probe"));
  const struct { uint8_t address; const char* name; } devices[] = {
      {FalconConfig::kBar02Address, "Bar02"},
      {FalconConfig::kBatteryMonitorAddress, "INA260 battery"},
      {FalconConfig::kSolarMonitorAddress, "INA260 solar"},
      {FalconConfig::kEnclosureTemperatureAddress, "MCP9808"},
      {FalconConfig::kWindAdcAddress, "ADS1115"},
  };
  for (const auto& device : devices) {
    Serial.printf("[DIAG] I2C 0x%02X %-16s %s\n", device.address,
                  device.name, state(addressPresent(device.address)));
  }
  Serial.println(F("[DIAG] BNO085 SPI: wiring initialized; driver self-test pending"));
  Serial.println(F("[DIAG] GPS UART2: waiting for receiver bytes"));
}

void SensorDiagnostics::tick(uint32_t nowMs) {
  while (gps_.available()) {
    // Diagnostic mode confirms receiver activity without claiming a valid fix.
    gps_.read();
    lastGpsByteMs_ = nowMs;
  }
  if (nowMs - lastTelemetryMs_ >= FalconConfig::kTelemetryIntervalMs) {
    lastTelemetryMs_ = nowMs;
    emitTelemetry(nowMs);
  }
}

void SensorDiagnostics::emitTelemetry(uint32_t nowMs) {
  const bool bar02 = addressPresent(FalconConfig::kBar02Address);
  const bool battery = addressPresent(FalconConfig::kBatteryMonitorAddress);
  const bool solar = addressPresent(FalconConfig::kSolarMonitorAddress);
  const bool enclosure = addressPresent(FalconConfig::kEnclosureTemperatureAddress);
  const bool windAdc = addressPresent(FalconConfig::kWindAdcAddress);
  Serial.printf(
      "{\"protocol\":\"falcon.telemetry\",\"version\":1,\"sequence\":%lu,"
      "\"uptimeMs\":%lu,\"source\":\"hardware-diagnostic\","
      "\"monitoring\":true,\"sensors\":{\"bar02\":\"%s\","
      "\"bno085\":\"UNTESTED\",\"gps\":\"%s\",\"batteryIna260\":\"%s\","
      "\"solarIna260\":\"%s\",\"mcp9808\":\"%s\",\"ads1115\":\"%s\"},"
      "\"measurements\":{}}\n",
      static_cast<unsigned long>(sequence_++), static_cast<unsigned long>(nowMs),
      bar02 ? "DETECTED" : "NOT_DETECTED",
      nowMs - lastGpsByteMs_ < 5000 && lastGpsByteMs_ > 0 ? "BYTES" : "WAITING",
      battery ? "DETECTED" : "NOT_DETECTED", solar ? "DETECTED" : "NOT_DETECTED",
      enclosure ? "DETECTED" : "NOT_DETECTED", windAdc ? "DETECTED" : "NOT_DETECTED");
}
