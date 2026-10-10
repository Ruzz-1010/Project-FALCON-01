# 3.3 V Sensor-Rail Baseline


<!-- FALCON-DOST-REVISION-NOTE:START -->
> **Current revision note (2026-10-10):** Use the DOST major revision baseline in [`docs/REVISION_2026-10-10.md`](../../../docs/REVISION_2026-10-10.md) unless this file is explicitly archived. The active design is a compact single-tube / small-buoy, ESP32-based, event-driven, cloud-first system. LoRa, large Bay Station hardware, tall tower layouts, and continuous every-second uploads are legacy or optional fallback assumptions.
<!-- FALCON-DOST-REVISION-NOTE:END -->

Status: **schematic and placement v0.9; bench current and thermal validation
still required before fabrication**. Updated 2026-08-21.

## Selected regulator

U1 is `AP2112K-3.3TRG1`, a fixed 3.3 V, 600 mA LDO in SOT25. C1 and C2 are
1.0 uF X7R ceramic input/output capacitors, placed beside U1 as required by the
manufacturer application circuit. U1 EN is tied to its protected 5 V input.

```text
+5V_PROTECTED ----+---- U1 pin 1 VIN      U1 pin 5 VOUT ---- +3V3_SENSOR
                  |     U1 pin 3 EN       |
                 C1 1uF                   C2 1uF
                  |     U1 pin 2 GND       |
GND --------------+-----------+------------+
```

The ESP32 DevKitC 3V3 header is deliberately left unconnected. This prevents
the carrier LDO and the DevKitC onboard regulator from driving each other.
Sensor GPIO remains 3.3 V logic and all grounds remain common.

## Limits and release tests

- The 600 mA rating is not permission to operate at 600 mA without a thermal
  test. LDO heat is approximately `(5 V - 3.3 V) x sensor current`.
- Measure actual combined sensor startup and steady current before release.
- Record 3.3 V minimum/maximum, ripple, and U1 temperature during Wi-Fi, GPS
  acquisition, SPI activity, and both fans starting.
- Confirm every connected breakout accepts 3.3 V on its selected power pin.
- Verify C1/C2 value after DC-bias derating and use X7R or X5R dielectric.
- Do not fit a jumper between the DevKitC 3V3 header and `+3V3_SENSOR`.

## Primary references

- [Diodes Incorporated AP2112 product page](https://www.diodes.com/part/view/AP2112/)
- [AP2112 official datasheet](https://www.diodes.com/datasheet/download/AP2112.pdf)

