# Adviser-Revised Electronics Wiring v6.1

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
ESP32 USB serial -> Orange Pi Zero 3
```

Disconnect power before wiring. Confirm exact pin labels, logic voltage, connector pin 1, polarity, pull-ups, cable shield/ground strategy, and module revision. Add one device at a time, verify rail voltage/current, scan interfaces, record raw readings, then test invalid/disconnected behavior. Never infer final marine wiring from illustrative 3D images.

The final harness requires fused branches, reverse-polarity and transient protection, marine connectors/glands, strain relief, corrosion control, service loops, labeled cables, and a continuity/insulation checklist. Passive mooring has no electrical load-cell connection.
