#pragma once

#include <Arduino.h>
#include <DNSServer.h>
#include <WebServer.h>

#include "system_state.h"

class PortalServer {
 public:
  PortalServer();

  bool begin();
  void handleClient();

 private:
  void configureRoutes();
  void handleStatus();
  void handleMonitoringToggle();
  void handleRestart();
  void handleNotFound();
  void sendDashboard();
  void sendFile(const char* path, const char* contentType,
                const char* cacheControl);
  void sendJson(int statusCode, const String& body);
  void sendNoCacheHeaders();
  void redirectToDashboard();
  bool validateWebAssets() const;
  static String escapeJson(const String& value);

  DNSServer dnsServer_;
  WebServer webServer_;
  SystemState systemState_;
  bool running_ = false;
  bool webAssetsReady_ = false;
  bool restartPending_ = false;
  uint32_t restartAtMs_ = 0;
};
