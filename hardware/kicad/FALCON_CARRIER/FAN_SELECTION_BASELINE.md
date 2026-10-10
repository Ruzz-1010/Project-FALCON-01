# Internal Fan Selection and Interface Baseline


<!-- FALCON-DOST-REVISION-NOTE:START -->
> **Current revision note (2026-10-10):** Use the DOST major revision baseline in [`docs/REVISION_2026-10-10.md`](../../../docs/REVISION_2026-10-10.md) unless this file is explicitly archived. The active design is a compact single-tube / small-buoy, ESP32-based, event-driven, cloud-first system. LoRa, large Bay Station hardware, tall tower layouts, and continuous every-second uploads are legacy or optional fallback assumptions.
<!-- FALCON-DOST-REVISION-NOTE:END -->

Status: **reference-design candidate; purchase and environmental validation
required before fabrication**. Updated 2026-08-21.

## Reference fan

The carrier reference design shall use **two Noctua NF-A8 5V PWM** fans unless
procurement or enclosure testing forces a documented substitution.

| Property | Manufacturer value | Design consequence |
| --- | ---: | --- |
| Size | 80 x 80 x 25 mm | Matches the two 80 mm CAD provisions |
| Mounting-hole spacing | 71.5 x 71.5 mm | Verify against the printed enclosure tray |
| Rated / maximum voltage | 5.0 V / 5.5 V | Power only from the protected regulated 5 V rail |
| Maximum input | 0.15 A, 0.75 W per fan | Two-fan running budget is 0.30 A / 1.50 W |
| Starting voltage | 4 V | Verify the 5 V rail at simultaneous startup |
| PWM | 21–28 kHz; 25 kHz target | ESP32 timer output; do not use slow software PWM |
| PWM input | Fan-internal pull-up; sink no more than 5 mA | Use an open-drain transistor, not direct push-pull GPIO |
| Tachometer | Open-collector RPM output | Give each fan an independent ESP32 input and pull-up |
| Environment | IP50, -10 to +70 deg C, 15–90% RH | Dry sealed-enclosure use only; no salt spray or condensation |

Manufacturer wire order is: pin 1 black GND, pin 2 yellow +5 V, pin 3 green
RPM signal, and pin 4 black PWM signal. Color alone is not sufficient for
receiving inspection; confirm pin order from the housing key and continuity.

## Correct electrical architecture

The current two-wire low-side `FAN_SWITCHED` placeholder is not the release
architecture for this four-wire fan. Each fan needs its own keyed four-position
header and independent tach input:

```text
protected +5 V -------------------------- fan pin 2 VCC
logic GND ------------------------------- fan pin 1 GND
ESP32 timer -> gate resistor -> NMOS ---- fan pin 4 PWM (open-drain sink)
ESP32 input <---- protected/pulled-up ---- fan pin 3 TACH
```

With PWM alone, an un-driven/open PWM input commands full speed. The v0.8
carrier deliberately uses this fail-safe cooling behavior during ESP32 boot;
firmware then assumes speed control after initialization.

Do not place a flyback diode blindly across a four-wire electronically
commutated fan. The fan includes its own driver electronics. Protection shall
instead be based on measured rail transients and the final harness length.

## Connector correction

- The generated v0.8 carrier replaces the provisional three-position J11 with
  two Molex `470531000` four-position fan outputs: J11 fan 1 and J13 fan 2.
- Do not tie the two tachometer outputs together.
- Molex `470531000` is the carrier-side reference header and `470541000` is the
  matching polarized four-position housing baseline. Confirm whether the
  received fan plug mates directly; otherwise document a pin-for-pin adapter.
- Lock the contact SKU and harness drawing only after checking authorized
  availability and the actual fan connector.

The v0.8 control stage uses one 2N7002 open-drain transistor per PWM input,
100-ohm gate resistors, 100-kilohm gate pull-downs, and independent 10-kilohm
3.3 V tach pull-ups. A pulled-down transistor gate leaves the fan PWM input
open during boot, so both fans run at full speed until firmware takes control.
This fail-safe cooling behavior intentionally replaces the earlier default-off
requirement and must be confirmed during the bench test.

## Bench release tests

1. Measure each fan's startup, steady-state, stalled/restart, and 0–100% PWM
   current from a current-limited 5 V supply.
2. Start both fans while the ESP32 transmits Wi-Fi and confirm the 5 V minimum,
   ripple, and regulator/eFuse temperature.
3. Verify 0%, 20%, 50%, and 100% duty at 25 kHz and record RPM from each tach.
4. Disconnect each tach/PWM wire in turn and verify deterministic fault handling.
5. Run an enclosure thermal test with fans off, one fan, and two fans.
6. Confirm no condensation reaches the IP50 fan or electronics.

## Primary references

- [Noctua NF-A8 5V PWM specifications](https://www.noctua.at/en/products/nf-a8-5v-pwm/specifications)
- [Noctua PWM specification white paper](https://www.noctua.at/pub/media/wysiwyg/Noctua_PWM_specifications_white_paper.pdf)
- [Noctua NF-A8 5V PWM information sheet](https://noctua.at/pub/media/blfa_files/infosheet/noctua_nf_a8_5v_pwm_datasheet_en.pdf)
- [Molex 470531000 four-circuit fan header](https://www.molex.com/en-us/products/series-chart/47053)
- [Molex 470541000 polarized housing](https://www.molex.com/en-us/products/part-detail/0470541000)
- [Nexperia 2N7002 datasheet and SOT23 pinning](https://assets.nexperia.com/documents/data-sheet/2N7002.pdf)
