# Five-Volt Protection and Source-Interlock Baseline


<!-- FALCON-DOST-REVISION-NOTE:START -->
> **Current revision note (2026-10-10):** Use the DOST major revision baseline in [`docs/REVISION_2026-10-10.md`](../../../docs/REVISION_2026-10-10.md) unless this file is explicitly archived. The active design is a compact single-tube / small-buoy, ESP32-based, event-driven, cloud-first system. LoRa, large Bay Station hardware, tall tower layouts, and continuous every-second uploads are legacy or optional fallback assumptions.
<!-- FALCON-DOST-REVISION-NOTE:END -->

Status: **superseded Orange Pi/USB architecture; LTE revision required; component values and footprints not released
for fabrication**. Updated 2026-08-21.

## Safety decision

Espressif documents the DevKitC V4 Micro-USB, 5 V header, and 3.3 V header power
methods as mutually exclusive. Therefore the carrier does not treat USB and
external 5 V as sources that may be connected casually at the same time.

Normal FALCON operation uses the Orange Pi USB connection for both ESP32 power
and serial telemetry. The protected external input is an alternate bench/service
source enabled only by fitting `JP1 EXT POWER ENABLE` while USB is unplugged.

```text
J1 protected-buck input
  +5V_INPUT_RAW
        |
        +-- input fuse/PTC (rating TBD from measured load/fault current)
        +-- input TVS (part TBD from cable transient test)
        `-- TPS25947-family eFuse candidate
              reverse polarity + overcurrent + inrush + reverse-current block
                            |
                     +5V_EXT_PROTECTED
                            |
                  JP1 EXT POWER ENABLE
                            |
                     +5V_PROTECTED rail
                            +--> DevKitC 5 V header
                            +--> 3.3 V sensor regulator
                            `--> fan stage if a 5 V fan is selected

Normal mode: JP1 OPEN, J1 unused, USB powers DevKitC and +5V_PROTECTED.
Service mode: USB UNPLUGGED, regulated J1 input present, JP1 fitted.
```

## Candidate protection device

The TI TPS25947 family is the current candidate because it accepts 2.7–23 V and
integrates input reverse-polarity protection, true reverse-current blocking,
adjustable current limiting, inrush/soft-start control, overvoltage protection,
short-circuit response, and thermal shutdown. The small QFN package requires a
manufacturer-recommended thermal land pattern and assembly process.

Do not assign the final suffix or resistor/capacitor values yet. `ILIM`, UVLO,
OVLO/clamp behavior, transient blanking, and output slew rate depend on measured
ESP32/sensor/fan currents, buck tolerance/ripple, input capacitance, and startup
behavior. A TVS part also cannot be selected only from “5 V”; its standoff,
breakdown, clamp voltage, pulse energy, leakage, and the upstream fuse must work
together.

## Mandatory physical interlock

- `JP1` shall be a removable shunt with a parked-position holder.
- Silkscreen beside JP1: `EXT 5V — REMOVE USB FIRST`.
- Silkscreen beside J1: `REGULATED 5V ONLY` and explicit `+`/`GND` markings.
- The normal deployed build leaves JP1 open and includes a red service tag.
- Firmware cannot make this safe; the rule is electrical and procedural.
- If simultaneous-source operation becomes a requirement, replace the DevKit
  architecture or expose both source rails independently to a validated power
  mux. Do not assume an eFuse on J1 alone prevents backfeed into USB.

## Release measurements

1. USB-powered idle, Wi-Fi transmit peak, and sensor-startup current.
2. Optional fan startup/running current and supply voltage.
3. J1 buck output minimum/maximum, ripple, startup overshoot, and fault current.
4. Rail droop during ESP32 radio bursts and sensor startup.
5. External cable length and transient waveform/energy.
6. Thermal rise of eFuse, connector, regulator, and copper at worst-case load.
7. Deliberate reverse-polarity, short-circuit, JP1-open, and USB-unplugged tests
   using a current-limited bench supply before connecting the Orange Pi.

## Primary references

- [Espressif ESP32-DevKitC V4 power options and warning](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32/esp32-devkitc/user_guide.html)
- [TI TPS25947 product page](https://www.ti.com/product/TPS25947)
- [TI TPS25947 datasheet](https://www.ti.com/lit/ds/symlink/tps25947.pdf)
