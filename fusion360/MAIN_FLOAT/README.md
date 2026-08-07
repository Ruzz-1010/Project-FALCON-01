# MAIN_FLOAT Fusion 360 Script

This script uses the current active Fusion design and builds the open-top,
closed-bottom HDPE main float inside its existing `MAIN_FLOAT` component. If no
such component exists, it creates one internally. It does not create a new file.

Nominal user parameters:

- `float_OD`: 650 mm
- `float_height`: 380 mm
- `wall_thickness`: 5 mm
- `profile_radius`: 45 mm

The timeline contains a constrained footprint sketch, extrusion, marine-profile
fillet, and inside shell. Save the generated document as `MAIN_FLOAT` after
inspection.
