# PROJECT FALCON-01 Assembly Safety Rules

1. Never delete, transform, edit, suppress, hide, or replace an existing component.
2. Every generator creates only one new separate component unless explicitly approved.
3. Before creating geometry, stop if Fusion reports uncaptured component positions.
4. Never assign a name through `Occurrence.name`; name only the new component.
5. On rerun, stop without changes if the target component already exists.
6. After each successful component, inspect, Capture Position, and save before continuing.
