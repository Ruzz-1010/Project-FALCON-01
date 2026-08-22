# Project FALCON — Flow AI Realistic Deployment Prompt Package

## Reference image

Upload and use this image as the visual reference for **every scene**:

`assets/falcon-approved-prototype.png`

The buoy in the reference image is the only approved Project FALCON prototype.
Do not redesign, simplify, replace, or add parts to it.

## Recommended workflow

Generate each scene as a separate 8–12 second landscape clip. Reuse the same
reference image and the same seed/character reference where Flow permits it.
Arrange the generated clips in the listed order, then add the English captions,
arrows, sensor values, dashboard screen recording, and music in a video editor.

Target output: 16:9, 1920×1080, realistic documentary style, 24 or 30 fps,
approximately 2–3 minutes after editing. Music only; no narrator and no dialogue.

## Master consistency prompt

Use the uploaded reference image as a strict structural and visual reference.
Show the exact same Project FALCON FALCON-01 coastal monitoring buoy already
deployed in real tropical coastal water. Preserve its cylindrical navy-blue
float, yellow structural trim, silver metal tower, dark electronics enclosure,
two side-mounted solar panels, four-cup wind sensor, antenna arrangement,
weather sensors, proportions, component positions, Project FALCON logo, and
overall dimensions. The prototype must remain identical and mechanically
plausible in every shot. Create photorealistic documentary footage with natural
sunlight, realistic seawater reflections, physically accurate waves, gentle
buoy heave, pitch and roll, moving wind, small water splashes, subtle corrosion
and outdoor wear, realistic camera movement, and believable coastal deployment.
No science-fiction styling and no redesign.

## Scene prompts

### Scene 1 — Establishing deployment shot

Wide cinematic drone shot of the exact referenced Project FALCON buoy floating
off a tropical Philippine coastline during clear early morning weather. The
buoy is already anchored and operational. Ocean swells pass beneath it, causing
natural slow heave, pitch, and roll. The wind sensor rotates continuously, both
solar panels catch sunlight, antennas move subtly in the breeze, and small waves
splash against the cylindrical float. Slowly orbit from front-left to front-right
while keeping the prototype large and clearly visible. Photorealistic marine
documentary footage, stable cinematic camera, natural colors.

Suggested caption: `PROJECT FALCON — AI-Powered Coastal Observation System`

### Scene 2 — Ocean movement becomes sensor data

Medium close shot of the same deployed buoy responding physically to real ocean
waves. Follow one wave as it reaches the buoy; the body rises, tilts slightly,
and settles naturally. Keep the wind cups spinning and show visible wind moving
across the water surface. Add subtle clean tracking graphics attached to the
real sensor locations: BNO085 IMU measures roll and pitch, Bar02 pressure sensor
measures water pressure, GPS determines position, and wind sensors measure speed
and direction. Values update continuously without covering the prototype.

Suggested values: `Wave 0.56 m`, `Roll +1.8°`, `Pitch −0.9°`,
`Wind 11.7 km/h`, `GPS VALID`.

### Scene 3 — Sensor placement close-ups

Create a continuous realistic inspection sequence around the exact same buoy.
Use smooth macro close-ups of the rotating wind-speed sensor, wind-direction
sensor, GPS antenna, weather sensor, solar panels, and sealed electronics box.
Each sensor stays in the same position shown by the reference. Use a thin cyan
leader line and a small professional label that tracks the component while the
camera moves. Ocean and buoy movement continue naturally in the background.
No exploded view and no new sensors.

### Scene 4 — Data enters the electronics enclosure

Start outside the exact deployed buoy and move the camera toward its existing
sealed electronics enclosure. Transition into a technically accurate cutaway
view only after reaching the box. Show sensor cables entering through waterproof
cable glands. Animated cyan signal pulses travel along the real cable paths into
the ESP32 DevKit. Show the ESP32 reading IMU, pressure, GPS, wind, temperature,
battery monitor, and solar monitor signals, validating and timestamping them.
The cutaway must look like real maintainable marine electronics, not a futuristic
hologram. Keep the exterior prototype unchanged.

Suggested caption: `Sensors → ESP32 data acquisition and validation`

### Scene 5 — ESP32 to Orange Pi through USB

Inside the same electronics enclosure, show the ESP32 packaging one telemetry
record. A bright but restrained data pulse follows a visible USB cable from the
ESP32 to the Orange Pi Zero 3. Track the pulse with the camera so the viewer can
clearly understand the direction. Show a brief readable telemetry overlay:
`pressure: 0.56 m`, `roll: 1.8°`, `GPS: valid`, `battery: 87%`.
The Orange Pi is powered separately as designed. Use realistic boards, connectors,
wires, cable management, and enclosure lighting.

Suggested caption: `ESP32 → USB Serial → Orange Pi Zero 3`

### Scene 6 — Edge AI processing

Close-up of the Orange Pi Zero 3 operating inside the deployed buoy enclosure.
Show a clean transparent processing overlay connected to the board, progressing
through five steps: Ingest, Validate, Build Features, AI Prediction, and Alert
Check. Data particles move through each step in order. Finish with a restrained
result card: `Predicted wave height: 0.49 m`, `Confidence: 80%`, `Sea state: CALM`.
The electronics remain realistic and the buoy continues moving gently outside.

Suggested caption: `Local edge AI continues even with unstable internet`

### Scene 7 — Internet and cloud transmission

Return to an exterior golden-hour shot of the exact deployed buoy. Begin at the
electronics enclosure, follow a small animated data pulse upward through the
communications antenna, then transition to a clean geographic visualization of
the encrypted internet path from the offshore buoy to a secure cloud service and
coastal monitoring station. Use an animated line that clearly travels in one
direction: `Orange Pi → Internet → Secure Cloud → Dashboard`. Keep the sequence
grounded and professional, not science fiction.

### Scene 8 — Live dashboard result

Show a realistic operator workstation at a Philippine coastal monitoring office.
The Project FALCON dashboard receives the record sent by the buoy. Animate new
data appearing: current wave 0.56 m, predicted wave 0.49 m, wind 11.7 km/h,
battery 87%, GPS valid, system online, and sea state calm. The measured blue wave
line and predicted amber line update smoothly and remain connected. Briefly cut
back to the same buoy moving offshore, then return to the live dashboard to show
that real movement becomes understandable operational information.

Suggested caption: `Live coastal conditions and AI-assisted prediction`

### Scene 9 — Complete connected journey

Final cinematic montage using only the exact referenced prototype: a wave moves
the deployed buoy, sensors react, signals enter the ESP32, a data pulse travels
through USB to the Orange Pi, edge AI produces a prediction, the result travels
through the internet and cloud, and the dashboard updates. Connect every step
with one continuous line-follow animation and directional arrows. End on a wide
sunset shot of the operational buoy with realistic waves and rotating wind cups.

Final caption: `MEASURE → PROCESS → PREDICT → DELIVER`

## Negative prompt / restrictions

- Do not generate a different buoy, tower, float, or enclosure.
- Do not change the navy-blue, yellow, and silver color scheme.
- Do not change the number, size, angle, or position of the solar panels.
- Do not add propellers, turbines, cameras, radar dishes, boats, people, screens,
  robotic arms, underwater creatures, or fictional sensors.
- Do not remove or deform the Project FALCON logo.
- No floating components, broken geometry, duplicated antennas, duplicated wind
  cups, warped solar cells, disconnected wires, or impossible cable routing.
- No dry-land demonstration; the buoy must be visibly deployed and floating.
- No static slideshow, still-photo sequence, or simple zoom-only animation.
- No neon cyberpunk effects, excessive holograms, cartoon style, or fantasy UI.
- No violent storm, capsizing, collision, or unsafe maintenance activity.
- Do not show Orange Pi as a sensor controller; ESP32 performs sensor acquisition,
  while Orange Pi performs edge processing and AI.
- Do not imply that Claude directly controls the buoy or safety-critical hardware.

## Editing notes

Use straight line-follow graphics and small moving dots to make data direction
obvious. Keep overlays on screen long enough to read, but allow the real buoy and
water movement to remain visible. Use subtle ocean ambience mixed below an
instrumental cinematic track. Use cross-dissolves, tracked match cuts, and camera
motion rather than slide transitions. Verify every generated clip against the
reference image before accepting it.
