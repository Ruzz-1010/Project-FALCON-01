function formatUptime(totalSeconds) {
    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor(
      (totalSeconds % 3600) / 60
    );
    const seconds = totalSeconds % 60;
  
    return `${hours}h ${minutes}m ${seconds}s`;
  }
  
  function setBatteryDisplay(percent) {
    const safePercent = Math.max(
      0,
      Math.min(100, Number(percent))
    );
  
    document.getElementById(
      "batteryValue"
    ).textContent = `${safePercent}%`;
  
    document.getElementById(
      "batteryBar"
    ).style.width = `${safePercent}%`;
  
    const degrees = safePercent * 3.6;
  
    document.querySelector(
      ".battery-ring"
    ).style.background = `
      conic-gradient(
        var(--accent) 0deg,
        var(--accent) ${degrees}deg,
        rgba(255, 255, 255, 0.08) ${degrees}deg
      )
    `;
  }
  
  async function updateDashboard() {
    try {
      const response = await fetch(
        "/api/status",
        {
          cache: "no-store"
        }
      );
  
      if (!response.ok) {
        throw new Error("API request failed");
      }
  
      const data = await response.json();
  
      document.getElementById(
        "systemStatus"
      ).textContent = data.system;

      document.getElementById(
        "systemIndicator"
      ).classList.remove("is-offline");
  
      document.getElementById(
        "clients"
      ).textContent = data.clients;
  
      document.getElementById(
        "uptime"
      ).textContent = formatUptime(data.uptime);
  
      document.getElementById(
        "temperature"
      ).textContent = data.temperature.toFixed(1);
  
      document.getElementById(
        "tilt"
      ).textContent = `${data.tilt.toFixed(1)}°`;
  
      document.getElementById(
        "waveLevel"
      ).textContent = `${data.waveLevel.toFixed(1)} m`;
  
      document.getElementById(
        "seaCondition"
      ).textContent = data.seaCondition;
  
      document.getElementById(
        "gpsStatus"
      ).textContent = data.gps;
  
      document.getElementById(
        "solarStatus"
      ).textContent = data.solar;
  
      document.getElementById(
        "securityStatus"
      ).textContent = data.security;
  
      document.getElementById(
        "monitoringStatus"
      ).textContent =
        data.monitoring ? "ACTIVE" : "STOPPED";
  
      document.getElementById(
        "monitoringButton"
      ).textContent =
        data.monitoring
          ? "Stop Monitoring"
          : "Start Monitoring";
  
      setBatteryDisplay(data.battery);
  
      document.getElementById(
        "lastUpdated"
      ).textContent =
        `Updated ${new Date().toLocaleTimeString()}`;
    } catch (error) {
      document.getElementById(
        "systemStatus"
      ).textContent = "CONNECTION LOST";

      document.getElementById(
        "systemIndicator"
      ).classList.add("is-offline");
  
      document.getElementById(
        "lastUpdated"
      ).textContent = "Update failed";
    }
  }
  
  async function toggleMonitoring() {
    const button = document.getElementById(
      "monitoringButton"
    );
  
    button.disabled = true;
    button.textContent = "Please wait...";
  
    try {
      await fetch(
        "/api/monitoring/toggle",
        {
          method: "POST"
        }
      );
  
      await updateDashboard();
    } catch (error) {
      alert("Unable to change monitoring status.");
    } finally {
      button.disabled = false;
    }
  }
  
  async function restartDevice() {
    const confirmed = confirm(
      "Restart FALCON-01 now?"
    );
  
    if (!confirmed) {
      return;
    }
  
    try {
      await fetch(
        "/api/restart",
        {
          method: "POST"
        }
      );
  
      alert(
        "FALCON-01 is restarting. Reconnect after a few seconds."
      );
    } catch (error) {
      alert(
        "Device connection was interrupted during restart."
      );
    }
  }
  
  updateDashboard();
  
  setInterval(
    updateDashboard,
    2000
  );
