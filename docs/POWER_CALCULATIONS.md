# FALCON-01 Provisional Power and Protection Schedule

## Energy Model

Baseline battery energy: `12.8 V × 20 Ah = 256 Wh nominal`. At 80% usable,
budget `204.8 Wh`.

| Average complete load | No-solar runtime | Daily energy |
| ---: | ---: | ---: |
| 6 W | 34.1 h | 144 Wh/day |
| 8 W | 25.6 h | 192 Wh/day |
| 10 W | 20.5 h | 240 Wh/day |

Solar estimate at four peak-sun-hours and 70% net efficiency:

| Panel | Estimated harvest | Margin at 6 W load | Margin at 8 W load |
| ---: | ---: | ---: | ---: |
| 60 W | 168 Wh/day | +24 Wh | -24 Wh |
| 80 W | 224 Wh/day | +80 Wh | +32 Wh |

Therefore 60 W is a supervised-test minimum; 80 W is the preferred prototype
starting point. Neither is an endurance claim for a cloudy marine deployment.

## Provisional Branch Schedule

| Branch | Design envelope | Provisional protection | Provisional copper |
| --- | ---: | ---: | --- |
| Battery to distribution | <=10 A design envelope | 10 A DC fuse near battery | 16 AWG marine tinned |
| MPPT/battery charge | Set by panel Isc/controller | Per both manufacturers | 16–18 AWG after calculation |
| Orange Pi buck input | <=3 A at 12 V transient envelope | 5 A DC branch fuse | 18 AWG |
| ESP32/sensor buck input | <=2 A at 12 V envelope | 3 A DC branch fuse | 18 AWG |
| 5 V low-voltage outputs | Per measured load | Fuse to converter/cable limit | 20 AWG short runs |
| 3.3 V sensor signals | milliamp-scale | No branch fuse; protected supply | 22–26 AWG twisted/shielded as needed |

These are prototype starting values, not final marine authorization. Final fuse
selection must be above normal/startup current but below the ampacity of every
downstream conductor and connector. Verify DC interrupt rating. Panel-side
protection must follow panel Isc, conductor count, and MPPT instructions.

## Validation Gates

1. Log current at 12.8 V and both 5 V rails for 24 hours.
2. Capture Orange Pi startup peak, Wi-Fi load, storage writes, and fan startup.
3. Verify each buck at minimum/maximum battery voltage, temperature, and load.
4. Check voltage drop at the Orange Pi; reject brownouts or unstable USB power.
5. Run a fused short/fault test using a protected bench setup.
6. Run 72-hour solar endurance before unattended operation.
7. Replace estimates with measured averages and recalculate autonomy.
