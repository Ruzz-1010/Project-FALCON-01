# Project FALCON Sensor Approval List with Pictures and Price References

Date prepared: 2026-10-11
Status: proposal / validation approval reference; not a purchase order

Use this file for adviser/DOST approval of the revised compact buoy sensor set. Prices are planning references from currently visible online listings. Re-check exact SKU, stock, seller rating, output type, waterproof rating, cable length, range, and shipping before buying.

## Recommended approval package

| Priority | Channel | Recommended item | Planning price | Buy from / reference | Approval decision |
| --- | --- | --- | ---: | --- | --- |
| Required | Water pressure / wave input | Low-range submersible hydrostatic level transmitter, 4–20 mA preferred, target 0–1 mH2O or 0–2 mH2O | ₱2,897–₱3,720 typical; lower listings around ₱1,471 exist but need stricter verification | Lazada QDY30A / hydrostatic transmitter listings show 4–20 mA, 0–0.5 m to 500 m configurable, IP68, 304/316 stainless options, and 12–36 V supply references: [QDY30A listing](https://www.lazada.com.ph/videodetail/?video_id=8000144764410), [1 m/3 m/5 m listing](https://www.lazada.com.ph/videodetail/?video_id=8000146168991), [tag listing](https://www.lazada.com.ph/tag/tank-level-monitoring-system/) | **Approve first.** This is the main research sensor. Do not buy high-range pump/automotive pressure sensors unless low-range water-level units cannot be verified. |
| Required interface | Pressure signal interface | ADS1115 16-bit ADC + 150 Ω precision shunt + RC/protection parts | ₱135–₱290 for ADS1115; add ₱100–₱250 for shunt/protection | Lazada ADS1115 listing at ₱171; other tag results show ₱135–₱290: [ADS1115 listing](https://www.lazada.com.ph/videodetail/?video_id=8000078224372), [ADS1115 tag result](https://www.lazada.com.ph/tag/ld-icoa-12a/) | **Approve with pressure sensor.** Needed because ESP32 cannot directly read 4–20 mA. |
| Required | Wind speed + direction | Combined cup anemometer + wind vane, RS485/0–5 V/4–20 mA output preferred | ₱1,204–₱1,639 low-cost; industrial units ₱3,666–₱9,282 | Shopee search shows 30 m/s wind speed/direction sensor at ₱1,204 and MakerLab anemometer at ₱1,639: [Shopee anemometer search](https://shopee.ph/list/anemometer), [MakerLab Shopee anemometer listing](https://shopee.ph/Anemometer-Wind-Speed-Sensor-0-to-5V-Analog-RS485-i.18252381.40953188107); Lazada industrial speed-only unit: [btnx RS485 anemometer](https://www.lazada.com.ph/videodetail/?video_id=8000146662526) | **Approve low-cost combined model first** if it includes both speed and direction. If only speed is available, buy separate wind vane or document wind direction as pending. |
| Required | GPS / position / security | NEO-6M GPS module with ceramic antenna | ₱299–₱497 common; higher listings up to ₱1,143 | MakerLab PH GPS listing appears in Lazada tag results at ₱299; Lazada GPS listings show ₱433–₱497: [NEO-6M ₱497 listing](https://www.lazada.com.ph/videodetail/?video_id=8000133608045), [NEO-6M ₱433 listing](https://www.lazada.com.ph/videodetail/?video_id=8000137992035), [GPS tag result with MakerLab ₱299](https://www.lazada.com.ph/tag/drone-gps-module-for-precision/) | **Approve.** Used for exact position, drift/geofence, time, and anti-loss/security evidence. |
| Required support | Battery / solar monitor | INA219 current/power module or INA260 upgrade | ₱83–₱180 for INA219; INA260 around ₱593 | Shopee INA219 listing at ₱83; imBento Cebu has INA219 at ₱180 in stock; Lazada tag shows INA260 around ₱593: [Shopee INA219](https://shopee.ph/INA219-GY-219-I2C-Bi-directional-DC-Current-Power-Supply-Sensor-Breakout-Module-for-Arduino-DIY-i.1063532622.25639962980), [imBento INA219](https://imbento.com/shop/product/439), [Lazada sensor module tag](https://www.lazada.com.ph/tag/sensor-module/) | **Approve INA219 first** for low cost. Upgrade to INA260 only if current range/accuracy becomes a problem. |
| Required power | Rechargeable battery pack | Small 12 V LiFePO4 pack with built-in BMS, or protected 18650 pack for prototype validation | Prototype 18650 holders/cases ₱15–₱499; small 12 V LiFePO4 planning range ₱1,500–₱3,500+ | Shopee 18650 holder/BMS listings; Lazada lithium/LiFePO4 battery listings | **Add to approval list.** Battery capacity must be sized after ESP32, LTE/Wi-Fi, GPS, sensors, and flashing beacon current are measured. |
| Required power | Solar panel | Compact DIY solar panel set: best is 1 pc 3 W–5 W mini panel if the buoy top deck can fit it; if using 5.5 V / 0.99 W round mini panels, use 2–4 pcs minimum practical set because 1 pc is display/trickle only | 0.99 W round mini panel about ₱117 each: 2 pcs ≈ ₱235, 3 pcs ≈ ₱353, 4 pcs ≈ ₱470; 6 V / 3.3 W around ₱230; 5 V–6 V / 5 W compact panels commonly ₱186–₱339 | Google Shopping/AliExpress 5.5 V 0.99 W round mini panel; Shopee/Lazada 5 V/5 W, 6 V/5 W, 6 V/3 W, and small solar cell module listings | **Approve with quantity guide.** 1×0.99 W is design-fit/trickle only; 2× is very low-power backup; 3–4× is compact array; 1×3 W–5 W is recommended simple approval choice; 10 W only if buoy size increases. |
| Required power interface | Solar charger and battery protection | Solar charge controller matched to battery chemistry; include BMS for lithium/LiFePO4 packs | Small PWM controllers around ₱189; CN3065/TP4056 class modules lower cost for single-cell prototypes | Shopee solar charge controller listings; CN3065/TP4056 module references | **Required if solar charging is used.** Do not connect solar panel directly to lithium battery without proper charger and protection. |
| Required safety | Flashing marine warning light / buoy beacon | Waterproof flashing marine beacon or buoy signal light, IP66–IP68 preferred, visible as a night marker | Current reference is ₱458.59 plus tax for a 2-piece flashing warning marine buoy light listing; budget around ₱500 and re-check Shopee/Lazada before buying | Shopee/Lazada flashing warning marine buoy light listings; Alibaba 2-piece reference listing around ₱458.59 plus tax | **Add for night marker visibility and safety.** Prefer self-contained solar flashing beacon so it does not drain the main electronics battery. |
| Required communication support | Internet module | ESP32 Wi-Fi for lab; A7670E LTE Cat-1 or Waveshare ESP32-S3 A7670E for field | A7670E core ₱1,015–₱1,151; Waveshare ESP32-S3 A7670E ₱2,614; T-SIM7600 class ₱4,192 | Lazada A7670E search lists multiple core boards around ₱1,015–₱1,151 and Waveshare ESP32-S3 A7670E at ₱2,614: [A7670E search](https://www.lazada.com.ph/tag/a7670e/), [ESP32 SIM/LTE search](https://www.lazada.com.ph/tag/esp32-sim/) | **Approve as communication module, not sensor.** Use Wi-Fi only for lab/near-shore validation. Use LTE only if deployment site has no reliable Wi-Fi. |
| Optional event/security | Tilt / motion | MPU6050 / GY-521 accelerometer + gyroscope | ₱92–₱223 typical | Lazada MPU6050 listings show ₱186, ₱223, and lower tag listings around ₱92–₱101: [MPU6050 listing](https://www.lazada.com.ph/videodetail/?video_id=8000145952787), [MPU6050 tag result](https://www.lazada.com.ph/tag/robotic-projects/) | **Optional but useful.** Adds movement/tilt event trigger. It does not replace the water pressure sensor. |
| Optional event/security | Vibration/tamper | SW-420 vibration sensor module | ₱45–₱70 typical | e-Gizmo lists SW-420 at ₱45; MakerLab lists SW-420 at ₱70; Lazada tag result shows ₱48: [e-Gizmo SW-420](https://e-gizmo.net/gizmoshop/index.php?product_id=1611&route=product%2Fproduct), [MakerLab SW-420](https://makerlab.ph/products/vibration-sensor-sw-420), [Lazada sensor module tag](https://www.lazada.com.ph/tag/sensor-module/) | **Optional.** Good for enclosure hit/tamper trigger; not reliable as wave measurement. |
| Optional event/security | Lid-open / enclosure tamper | Reed switch / magnetic switch | ₱70–₱309 depending style | Lazada magnetic switch listing shows ₱308.58; local reed switch modules are available from hobby stores: [Lazada magnetic switch](https://www.lazada.com.ph/videodetail/?video_id=8000131458280), [CircuitRocks reed switch module](https://circuit.rocks/products/reed-switch-module) | **Optional.** Good for security event if enclosure is opened. |
| Optional data safety | Local buffer | microSD module + 8–32 GB card, or ESP32 flash buffer for short tests | ₱100–₱300 module/card planning allowance | General ESP32 microSD modules are widely available; include only if field trial has intermittent internet | **Recommended if LTE/Wi-Fi is unstable.** Not a sensor, but prevents data loss. |

## Quantity list for approval

| Item | Quantity | Purpose | Panel note |
| --- | ---: | --- | --- |
| Water pressure transmitter | 1 pc | Core wave/pressure input | Buy first after seller confirms low range, waterproof rating, and output type. |
| ADS1115 + shunt/protection parts | 1 set | Pressure signal interface | Needed if pressure sensor is 4-20 mA; ESP32 cannot read 4-20 mA directly. |
| Wind speed + direction sensor | 1 pc | Wind condition data | Prefer combined cup anemometer + direction vane to reduce mast parts. |
| GPS / GNSS module | 1 pc | Exact buoy position and security | Use external/ceramic antenna with clear sky view. |
| INA219 power monitor | 1 pc | Battery/solar current and voltage tracking | Use during validation to measure real load and charging behavior. |
| Rechargeable battery pack with BMS | 1 pack | Main power source | Final capacity depends on measured load; do not use loose cells without BMS. |
| Compact solar panel | 1 pc 3W-5W preferred, or 2-4 pcs 0.99W mini panels | Solar charging support | One 0.99W panel is only for display/trickle charging, not full buoy load. |
| Solar charger / BMS interface | 1 pc / 1 set | Safe charging path | Required between solar panel and lithium/LiFePO4 battery. |
| Flashing marine warning light / buoy beacon | 1 pc needed; 2 pcs if buying the listed bundle | Night marker and safety warning | Use 1 flashing waterproof beacon on the buoy; 2-piece listings are acceptable as spare. Not a steady area light. Prefer self-contained solar type. |
| Internet module | 1 pc only if no stable Wi-Fi | Cloud upload from field site | Use ESP32 Wi-Fi for lab/near-shore validation; buy LTE only if needed. |
| Tilt/motion sensor MPU6050 | 1 pc optional | Tilt or motion event support | Optional; does not replace the water pressure sensor. |
| Vibration/tamper sensor SW-420 | 1 pc optional | Hit/tamper trigger | Optional security/event input only. |
| Reed switch / magnetic switch | 1 pc optional | Lid-open security trigger | Optional enclosure tamper sensor. |
| microSD module + card | 1 set optional | Data backup when internet drops | Recommended for field tests with weak Wi-Fi/LTE. |

## Product picture references

Pictures below are reference images only. Buy based on the linked seller page/spec sheet, not only on the picture.

| Channel | Reference picture | What it looks like |
| --- | --- | --- |
| Water pressure sensor | ![Submersible hydrostatic water level transmitter](https://www.intercyprus.com/cdn/shop/files/S2122ec2c29e64d69a6540a860d8d50dby.webp?v=1757590185&width=1200) | Stainless cylindrical probe with fixed waterproof cable. This is the correct physical style for a pressure/level sensor. |
| ADS1115 pressure interface | ![ADS1115 ADC module](https://www.tecneu.com/cdn/shop/files/modulo-ads1115-amplificador-de-ganancia-programable-16-b-adc-650300.jpg?v=1750204354) | Small 16-bit I2C ADC board used to read the pressure sensor loop voltage. |
| Wind speed + direction | ![Cup anemometer with wind vane](https://image.made-in-china.com/2f0j00MlTcsOSnSvkG/2022-Hot-sale-Firstrate-FST200-205-RS485-CE-Certificated-Wind-Speed-And-Direction-Sensor.jpg) | Cup anemometer plus vane. Prefer combined speed and direction to reduce mast parts. |
| GPS module | ![ESP32 and NEO-6M GPS module](https://jameselsey.github.io/assets/post_images/2024/gps/gpsbreadboard.jpg) | NEO-6M GPS board with ceramic antenna, wired to ESP32 through UART. |
| INA219 power monitor | ![INA219 current sensor module](https://mikrobot.pl/userdata/public/gfx/4754/Zdjecie-produktu-Miernik-INA219-pradu-napiecia-I2C-modul-26V-3.2A-czujnik-mocy-do-Arduino-1.png) | Blue INA219 module with screw terminal for current/power monitoring. |
| Rechargeable battery pack | Reference image should match the final selected protected pack/BMS. | Use LiFePO4 or protected 18650 pack only after measured load estimate. |
| Compact DIY solar panel | Reference should show the small round/square mini solar cell style used in the buoy design. | For 0.99 W units, list 2–4 pieces; for simpler approval choose one 3 W–5 W compact panel if it fits. |
| Solar charger / BMS | Reference image should show the selected solar charger module or controller. | Required between solar panel and battery. |
| Marine night beacon | Reference should show an IP66–IP68 buoy/marine navigation light. | Use self-contained solar flashing beacon if possible. |
| A7670E LTE module | ![A7670E LTE module](https://media.s-bol.com/BZDXv3rxk5lQ/pgm0M4p/550x506.jpg) | LTE Cat-1 module for cloud upload when Wi-Fi is not available. |
| MPU6050 motion sensor | ![MPU6050 GY-521 module](https://i-blog.csdnimg.cn/blog_migrate/5989d8ccb28f4c0039b3a8037cba3327.png) | Small accelerometer/gyro module for tilt/motion event detection. |
| SW-420 vibration sensor | ![SW-420 vibration sensor](https://voltros.in/cdn/shop/files/61hyqQGTNVL.jpg?v=1757590947&width=1445) | Simple vibration/tamper trigger module. |
| Reed switch | ![Reed switch module](https://fluxworkshop.com/cdn/shop/products/15954fe8-16e9-4218-a0c3-4a4372c955a4_1200x1200.jpg?v=1611598960) | Magnetic lid-open / enclosure tamper sensor. |

## Pressure sensor approval notes

The pressure sensor is the most important item. The panel should approve the requirement before purchase:

1. **Range:** ask seller for 0–1 mH2O or 0–2 mH2O if possible. Avoid 0–10 m unless no lower range is available because high range reduces wave sensitivity.
2. **Output:** 4–20 mA is preferred because it is more tolerant of cable noise than direct voltage output.
3. **Material:** 316 stainless is preferred; 304 stainless may be acceptable only if seller confirms seawater/medium compatibility.
4. **Cable:** fixed waterproof cable, preferably vented gauge cable if using gauge pressure.
5. **Waterproofing:** IP68/continuous immersion statement required.
6. **Calibration:** document a bucket/static-depth test and a small wave-response test before claiming wave estimation.

## Alternatives by channel

| Channel | Lower-cost option | Better / safer option | Do not approve as replacement |
| --- | --- | --- | --- |
| Water pressure | Generic low-range 4–20 mA hydrostatic transmitter | Holykell HPT604 Type A or equivalent quoted industrial unit; RS485 Modbus transmitter if cable length/noise becomes a problem | Float switch, rain sensor, ultrasonic HC-SR04, automotive oil/fuel pressure sensor. These do not validate the same wave-pressure method. |
| Wind | Low-cost combined 3-cup speed + vane direction sensor | Industrial RS485 combined sensor with IP65/IP66 housing | Handheld anemometer as installed sensor; DIY toy vane as final field sensor. |
| GPS | NEO-6M | NEO-M8N / GNSS board with better antenna; LTE module with GNSS as backup | Phone GPS as final buoy position record. It can help during testing only. |
| Battery/solar monitor | INA219 | INA260 or external calibrated meter during validation | Voltage divider only if current/charge trend is not required. |
| Solar panel | 2–4 pcs 0.99 W round mini panels if they fit the top deck | 1 pc 3 W–5 W compact mini panel if size allows | One 0.99 W panel as the only power source for ESP32 + GPS + internet module. |
| Internet | ESP32 Wi-Fi for lab | A7670E LTE Cat-1 or SIM7600 class board for field | Always-on every-second upload; it increases battery and data cost. |
| Motion/tamper | SW-420 or reed switch | MPU6050 plus enclosure reed switch | Motion sensor as replacement for pressure sensor. Motion can detect movement but cannot prove water pressure/wave estimation. |

## Estimated package costs

| Package | Includes | Estimated sensor/telemetry cost |
| --- | --- | ---: |
| Minimum lab validation | Pressure transmitter, ADS1115/shunt, wind speed/direction, GPS, INA219, ESP32 Wi-Fi | about ₱4,700–₱7,900 plus ESP32 and wiring/enclosure |
| Field-ready low-cost validation | Minimum lab package + A7670E LTE + microSD buffer + SW-420/reed tamper | about ₱6,000–₱10,500 plus SIM load, waterproofing, battery, solar panel/charger, night beacon, buoy body, chain, and anchor |
| Safer industrial sensor option | Field-ready package + better pressure unit + industrial wind sensor | about ₱10,000–₱20,000+ depending supplier quotations |

## Recommendation for approval

Approve the **field-ready low-cost validation package** but buy in stages:

1. Buy and test ESP32, GPS, INA219, ADS1115, SW-420/reed, battery/charger, and mini solar options first because they are cheap and easy to validate.
2. Confirm the pressure sensor range/output/material with seller before payment.
3. Confirm whether the wind listing includes both speed and direction before payment.
4. Use Wi-Fi for bench/lab validation. Buy LTE only when the validation site needs internet away from Wi-Fi.
5. Keep LoRa as fallback only. The revised design should be cloud/event-driven if internet is available.
