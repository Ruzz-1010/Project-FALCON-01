# FALCON-01 Wokwi View — Historical BNO085 Prototype

> Historical record only. This predates adviser revision v6.0 and is not the required sensor/wiring baseline. BNO085 is optional/deprecated; use `PROJECT_CONTEXT.md` and `PINOUT.md` for current work.

## Open the Interactive Wiring

1. Build the firmware with PlatformIO.
2. Open the clean page you need in VS Code:
   - `diagram.all.json` — all selected parts in one overview;
   - `diagram.json` — BNO085, Bar02, and GPS core sensors;
   - `diagram.environment.json` — pressure, temperature, wind, and ADC; or
   - `diagram.power.json` — battery/solar monitors and Orange Pi.
3. If it opens as text, right-click the tab, choose **Reopen Editor With...**,
   then select **Wokwi Diagram Editor**.
4. Click the green Play button, or press `F1` and run
   **Wokwi: Start Simulator**.
5. If requested, follow **Wokwi: Request a New License**. The graphical editor
   may require a Wokwi plan; the JSON remains editable as text.

## Important Accuracy Note

Wokwi does not provide native models for every selected FALCON sensor. The
complete view therefore includes visual-only custom breakouts for BNO085,
Bar02, two INA260 monitors, MCP9808, ADS1115, UART GPS, and Orange Pi. Their
named pins and wires document the physical plan, but their protocol behavior is
not simulated yet. The view also uses:

- a potentiometer to exercise wind-direction analog input;
- a pushbutton to exercise anemometer pulses;
- a real simulated DS18B20 for the optional temperature channel; and
- a logic analyzer for the bus signals.

The BNO085 custom breakout now shows its actual SPI signal plan, including INT,
RST, P0, and P1. `docs/PINOUT.md` remains the authority for physical assembly.
The Orange Pi block is visual-only because its USB cable and separate 5 V power
branch cannot be represented as ordinary ESP32 GPIO wires.

## Build Path

`wokwi.toml` loads:

- `.pio/build/esp32dev/firmware.bin`
- `.pio/build/esp32dev/firmware.elf`

Rebuild after firmware changes so the simulator loads the latest files.

## Wire Colors

- red: 3.3 V power;
- black: common ground;
- teal pair: I2C SDA/SCL;
- violet: BNO085 SPI;
- green: UART or pulse signal;
- amber: analog wind-vane signal; and
- blue-gray: interrupt, reset, or OneWire.
