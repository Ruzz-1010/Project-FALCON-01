# Adviser-Revised Electronics Wiring v6.1


<!-- FALCON-DOST-REVISION-NOTE:START -->
> **Current revision note (2026-10-10):** Use the DOST major revision baseline in [`docs/REVISION_2026-10-10.md`](REVISION_2026-10-10.md) unless this file is explicitly archived. The active proposal core is a compact ESP32-based buoy with **water pressure sensing, wind speed/direction sensing, GPS for exact position and security, battery + solar power, and Wi-Fi/LTE internet communication**. LoRa, large Bay Station hardware, tall tower layouts, and continuous every-second uploads are legacy or optional fallback assumptions.
<!-- FALCON-DOST-REVISION-NOTE:END -->

> Functional net requirements remain useful, but connector positions, cable lengths, glands, and enclosure routing are under redesign. Verify the exact selected parts and replacement prototype before fabrication.

The previous BNO085-centered wiring drawings are retained only as historical prototype visuals and must not be used as the final Phase 1 harness. Use [PINOUT.md](PINOUT.md) and [HARDWARE.md](HARDWARE.md) for the current baseline.

## Current connection flow

```text
Bar02 + health I2C devices -> protected 3.3 V I2C -> ESP32
GPS -> protected UART -> ESP32
Wind speed/direction -> digital pulse + ADC interface -> ESP32
DS18B20 -> protected OneWire -> ESP32
Tamper + enclosure switch -> filtered/debounced GPIO -> ESP32
ESP32 GPIO -> buzzer transistor/driver -> buzzer
ESP32 -> Wi-Fi or LTE modem -> cloud API/database/dashboard

USB serial to the development laptop remains a bench-only substitute. A 4G/LTE modem may be installed in the buoy for a remote trial and must have its own protected regulator and antenna. No computer or cloud server is wired into or powered by the buoy enclosure.
```

Disconnect power before wiring. Confirm exact pin labels, logic voltage, connector pin 1, polarity, pull-ups, cable shield/ground strategy, and module revision. Add one device at a time, verify rail voltage/current, scan interfaces, record raw readings, then test invalid/disconnected behavior. Never infer final marine wiring from illustrative 3D images.

The final harness requires fused branches, reverse-polarity and transient protection, marine connectors/glands, strain relief, corrosion control, service loops, labeled cables, and a continuity/insulation checklist. Passive mooring has no electrical load-cell connection.
