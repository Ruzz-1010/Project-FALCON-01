# Adviser-Revised Electronics Wiring v6.2

> Functional net requirements remain useful, but connector positions, cable lengths, glands, and enclosure routing are under redesign. Verify the exact selected parts and replacement prototype before fabrication.

The previous BNO085-centered wiring drawings are retained only as historical prototype visuals and must not be used as the final Phase 1 harness. Use [PINOUT.md](PINOUT.md) and [HARDWARE.md](HARDWARE.md) for the current baseline.

## Current connection flow

```text
HPT604 4–20 mA -> protected 150 ohm shunt + ADS1115 -> protected 3.3 V I2C -> ESP32
GPS -> protected UART -> ESP32
Wind speed/direction -> digital pulse + ADC interface -> ESP32
DS18B20 -> protected OneWire -> ESP32
Tamper + enclosure switch -> filtered/debounced GPIO -> ESP32
ESP32 GPIO -> buzzer transistor/driver -> buzzer
ESP32 -> LoRa primary -> barangay-hall gateway/Bay Station -> SIM/4G/5G Internet backhaul

USB serial to the development laptop remains a bench-only substitute. The SIM/4G/5G modem belongs at the barangay-hall Bay Station, not in the buoy. No Bay Station computer or Internet-backhaul modem is wired into or powered by the buoy enclosure.
```

Disconnect power before wiring. Confirm exact pin labels, logic voltage, connector pin 1, polarity, pull-ups, cable shield/ground strategy, and module revision. Add one device at a time, verify rail voltage/current, scan interfaces, record raw readings, then test invalid/disconnected behavior. Never infer final marine wiring from illustrative 3D images.

The final harness requires fused branches, reverse-polarity and transient protection, marine connectors/glands, strain relief, corrosion control, service loops, labeled cables, and a continuity/insulation checklist. Passive mooring has no electrical load-cell connection.

The HPT604 candidate is powered from the protected 12 V domain, not the ESP32 3.3 V rail. Its vent tube must remain dry and breathable through a supplier-approved desiccant/breather termination. The previous Bar02 JST-GH wiring is bench-only and must not be used for the deployment sensor. See [PRESSURE_SENSOR_BASELINE.md](PRESSURE_SENSOR_BASELINE.md).
