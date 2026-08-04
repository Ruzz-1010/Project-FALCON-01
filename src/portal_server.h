#pragma once

#include <Arduino.h>
#include <DNSServer.h>
#include <WebServer.h>

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
  void redirectToDashboard();
  bool validateWebAssets() const;
  static String escapeJson(const String& value);

  DNSServer dnsServer_;
  WebServer webServer_;
  bool running_ = false;
  bool monitoringEnabled_ = true;
  bool webAssetsReady_ = false;
  unsigned long bootTime_ = 0;
};
