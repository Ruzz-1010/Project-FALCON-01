#include "portal_server.h"

#include <LittleFS.h>
#include <WiFi.h>

#include "config.h"

namespace {

constexpr char kNoCache[] = "no-store";
constexpr char kStaticCache[] = "public, max-age=3600";

}  // namespace

PortalServer::PortalServer() : webServer_(FalconConfig::kHttpPort) {}

bool PortalServer::begin() {
  bootTime_ = millis();

  if (!LittleFS.begin(true)) {
    Serial.println(F("ERROR: LittleFS mount failed."));
    return false;
  }

  webAssetsReady_ = validateWebAssets();
  if (webAssetsReady_) {
    Serial.println(F("LittleFS web assets verified."));
  } else {
    Serial.println(F("ERROR: One or more LittleFS web assets are missing."));
    Serial.println(F("Run PlatformIO: Upload Filesystem Image."));
  }

  WiFi.mode(WIFI_OFF);
  delay(100);
  WiFi.mode(WIFI_AP);

  const IPAddress localIp(192, 168, 4, 1);
  const IPAddress gateway(192, 168, 4, 1);
  const IPAddress subnet(255, 255, 255, 0);
  if (!WiFi.softAPConfig(localIp, gateway, subnet)) {
    Serial.println(F("ERROR: Wi-Fi access point network configuration failed."));
    return false;
  }

  if (!WiFi.softAP(FalconConfig::kApSsid, FalconConfig::kApPassword,
                   FalconConfig::kApChannel, false,
                   FalconConfig::kMaxConnections)) {
    Serial.println(F("ERROR: Wi-Fi access point failed."));
    return false;
  }

  if (!dnsServer_.start(FalconConfig::kDnsPort, "*", localIp)) {
    Serial.println(F("ERROR: Captive portal DNS server failed."));
    WiFi.softAPdisconnect(true);
    return false;
  }

  configureRoutes();
  webServer_.begin();
  running_ = true;

  Serial.print(F("Wi-Fi name : "));
  Serial.println(FalconConfig::kApSsid);
  Serial.print(F("Password   : "));
  Serial.println(FalconConfig::kApPassword);
  Serial.print(F("Dashboard  : http://"));
  Serial.println(localIp);
  Serial.println(F("FALCON captive portal ready."));
  return true;
}

void PortalServer::handleClient() {
  if (!running_) {
    return;
  }
  dnsServer_.processNextRequest();
  webServer_.handleClient();
}

void PortalServer::configureRoutes() {
  webServer_.on("/", HTTP_GET, [this]() { sendDashboard(); });
  webServer_.on("/index.html", HTTP_GET, [this]() { sendDashboard(); });
  webServer_.on("/style.css", HTTP_GET, [this]() {
    sendFile(FalconConfig::kStylePath, "text/css", kStaticCache);
  });
  webServer_.on("/app.js", HTTP_GET, [this]() {
    sendFile(FalconConfig::kScriptPath, "application/javascript", kStaticCache);
  });
  webServer_.on("/falcon-logo.jpg", HTTP_GET, [this]() {
    sendFile(FalconConfig::kLogoPath, "image/jpeg", kStaticCache);
  });

  webServer_.on("/api/status", HTTP_GET, [this]() { handleStatus(); });
  webServer_.on("/api/monitoring/toggle", HTTP_POST,
                [this]() { handleMonitoringToggle(); });
  webServer_.on("/api/restart", HTTP_POST, [this]() { handleRestart(); });

  const char* captivePaths[] = {
      "/generate_204",          "/gen_204",
      "/connecttest.txt",       "/redirect",
      "/ncsi.txt",              "/hotspot-detect.html",
      "/library/test/success.html", "/canonical.html",
      "/success.txt"};

  for (const char* path : captivePaths) {
    webServer_.on(path, HTTP_GET, [this]() { sendDashboard(); });
  }

  webServer_.onNotFound([this]() { handleNotFound(); });
}

void PortalServer::handleStatus() {
  const unsigned long uptimeSeconds = (millis() - bootTime_) / 1000UL;

  // Simulated values remain in one place until physical sensors are connected.
  constexpr float kDemoBattery = 94.0F;
  constexpr float kDemoTemperature = 28.6F;
  constexpr float kDemoTilt = 2.4F;
  constexpr float kDemoWaveLevel = 0.3F;

  String json;
  json.reserve(256);
  json += F("{\"system\":\"ONLINE\",\"clients\":");
  json += WiFi.softAPgetStationNum();
  json += F(",\"uptime\":");
  json += uptimeSeconds;
  json += F(",\"monitoring\":");
  json += monitoringEnabled_ ? F("true") : F("false");
  json += F(",\"battery\":");
  json += String(kDemoBattery, 0);
  json += F(",\"temperature\":");
  json += String(kDemoTemperature, 1);
  json += F(",\"tilt\":");
  json += String(kDemoTilt, 1);
  json += F(",\"waveLevel\":");
  json += String(kDemoWaveLevel, 1);
  json += F(",\"seaCondition\":\"");
  json += escapeJson("CALM");
  json += F("\",\"gps\":\"");
  json += escapeJson("WAITING FOR GPS");
  json += F("\",\"solar\":\"");
  json += escapeJson("STANDBY");
  json += F("\",\"security\":\"");
  json += escapeJson("ARMED");
  json += F("\"}");

  webServer_.sendHeader("Cache-Control", kNoCache);
  webServer_.send(200, "application/json", json);
}

void PortalServer::handleMonitoringToggle() {
  monitoringEnabled_ = !monitoringEnabled_;
  const String json = monitoringEnabled_
                          ? F("{\"monitoring\":true}")
                          : F("{\"monitoring\":false}");
  webServer_.sendHeader("Cache-Control", kNoCache);
  webServer_.send(200, "application/json", json);
}

void PortalServer::handleRestart() {
  webServer_.sendHeader("Cache-Control", kNoCache);
  webServer_.send(200, "application/json", F("{\"restarting\":true}"));
  delay(700);
  ESP.restart();
}

void PortalServer::handleNotFound() {
  String host = webServer_.hostHeader();
  const int portSeparator = host.indexOf(':');
  if (portSeparator >= 0) {
    host.remove(portSeparator);
  }

  if (host != WiFi.softAPIP().toString()) {
    redirectToDashboard();
    return;
  }

  sendDashboard();
}

void PortalServer::sendDashboard() {
  if (!webAssetsReady_) {
    webServer_.send(503, "text/plain",
                    F("Dashboard files are missing. Upload the LittleFS image."));
    return;
  }
  sendFile(FalconConfig::kIndexPath, "text/html", kNoCache);
}

void PortalServer::sendFile(const char* path, const char* contentType,
                            const char* cacheControl) {
  File file = LittleFS.open(path, "r");
  if (!file || file.isDirectory()) {
    webServer_.send(404, "text/plain", F("File not found"));
    return;
  }

  webServer_.sendHeader("Cache-Control", cacheControl);
  webServer_.streamFile(file, contentType);
  file.close();
}

void PortalServer::redirectToDashboard() {
  String location = F("http://");
  location += WiFi.softAPIP().toString();
  webServer_.sendHeader("Location", location, true);
  webServer_.send(302, "text/plain", "");
}

bool PortalServer::validateWebAssets() const {
  return LittleFS.exists(FalconConfig::kIndexPath) &&
         LittleFS.exists(FalconConfig::kStylePath) &&
         LittleFS.exists(FalconConfig::kScriptPath) &&
         LittleFS.exists(FalconConfig::kLogoPath);
}

String PortalServer::escapeJson(const String& value) {
  String escaped = value;
  escaped.replace("\\", "\\\\");
  escaped.replace("\"", "\\\"");
  return escaped;
}
