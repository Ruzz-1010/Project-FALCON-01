# Version History

## Purpose
Track independently governed component versions.

## Scope
Firmware, dashboard, API, planning documents, and documentation set.

## Current Status
No release tags or firmware version constant exist; labels are not signed releases.

## Architecture
Component versions remain independent until a release manifest is implemented.

## Implementation
| Component | Label | Status |
| --- | --- | --- |
| Firmware | Development | Implemented prototype |
| Dashboard | 2.1 | Implemented prototype |
| API | Development | Three routes implemented |
| Project context | v5.0 | Active |
| Mechanical baseline | v5.0 | CAD direction; validation pending |
| Dashboard 3D asset | Legacy Revision 4 | Replacement export pending |
| Documentation set | 2.0 | Active |

Git milestones: `5387122` initial portal, `5e80fb3` dashboard redesign, `8bec676` expanded root documentation content.

## Future Expansion
Add manifest fields for firmware, dashboard, API, hardware, model, commit, and compatibility.

## Engineering Notes
Record the exact Git commit during flashing until firmware exposes version metadata.

## Revision History
| Version | Date | Change |
| --- | --- | --- |
| 1.0 | 2026-08-05 | Initial version register. |
| 2.0 | 2026-08-13 | Registered mechanical Revision 5 and identified the current 3D visualization as a legacy export pending replacement. |
