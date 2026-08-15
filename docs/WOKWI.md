# FALCON-01 Wokwi View

## Open the Interactive Wiring

1. Build the firmware with PlatformIO.
2. Open `diagram.json` in VS Code.
3. If it opens as text, right-click the tab, choose **Reopen Editor With...**,
   then select **Wokwi Diagram Editor**.
4. Click the green Play button, or press `F1` and run
   **Wokwi: Start Simulator**.
5. If requested, follow **Wokwi: Request a New License**. The graphical editor
   may require a Wokwi plan; the JSON remains editable as text.

## Important Accuracy Note

Wokwi does not provide native models for every selected FALCON sensor. The
current view uses:

- an MPU6050 as an **I2C visual/simulation placeholder only**;
- a potentiometer to exercise wind-direction analog input;
- a pushbutton to exercise anemometer pulses;
- a real simulated DS18B20 for the optional temperature channel; and
- a logic analyzer for the bus signals.

The MPU6050 wires shown are not the final BNO085 wires. The physical BNO085 must
use the SPI assignments in `docs/PINOUT.md`. Bar02, INA260, ADS1115, MCP9808,
GPS, and Orange Pi remain documented in the exact pinout/SVG until custom Wokwi
chips are added.

## Build Path

`wokwi.toml` loads:

- `.pio/build/esp32dev/firmware.bin`
- `.pio/build/esp32dev/firmware.elf`

Rebuild after firmware changes so the simulator loads the latest files.
