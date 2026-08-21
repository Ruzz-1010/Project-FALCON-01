# Field Connector Orientation Audit

Status: **orientation locked for the compact presentation board; physical
mating check remains mandatory**. Updated 2026-08-21.

| Ref | Rotation | Pin-1 convention | Mating direction | Result |
| --- | ---: | --- | --- | --- |
| J2 | 0 deg | Leftmost signal pad in board view | Top-entry after lid removal | PASS |
| J7 | 0 deg | Leftmost signal pad in board view | Top-entry after lid removal | PASS |
| J8 | 0 deg | Leftmost signal pad in board view | Top-entry after lid removal | PASS |
| J9 | 0 deg | Leftmost signal pad in board view | Top-entry after lid removal | PASS |
| J10 | 0 deg | Leftmost signal pad in board view | Top-entry after lid removal | PASS |

The five headers form one left-edge service column with a common orientation.
Compact silkscreen legends use `+` for 3.3 V and `G` for ground. The complete
pin names, colors, housings, and assembly tests remain in
`CONNECTOR_HARNESS_PLAN.md`.

Top-entry was retained because it permits straight plug removal after opening
the electronics lid. Do not change to side-entry without first checking cable
gland position, service-loop bend radius, lid height, and latch access.

Before powering the first assembly, place every actual housing over a 1:1 print,
confirm the latch faces the intended direction, and compare pin 1 from the PCB
side and mating-face views. Never infer pin order from wire color alone.

