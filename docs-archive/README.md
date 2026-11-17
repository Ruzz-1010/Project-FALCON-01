# FALCON-01 documentation archive

Historical documentation moved out of `docs/` on 2026-11-02. Nothing here is
part of the active specification.

Active docs:

- `docs/prd.md`
- `docs/architecture.md`
- `docs/rules.md`
- `docs/design.md`
- `docs/task.md`
- `docs/memory.md`

Use this archive for provenance, old wiring notes, adviser revision history, and
previous designs. Do not edit archived files to describe current behavior; update
the active docs instead.

To restore a file temporarily:

```bash
mv docs-archive/<file> docs/
```

Remember to move it back or update the active docs so `docs/` stays limited to
the six canonical files.

The archive contains 49 items, including:

- `PROJECT_CONTEXT.md` and `REVISION_2026-10-10.md` — prior master context and
  the DOST revision baseline.
- `SYSTEM_ARCHITECTURE.md`, `HARDWARE.md`, `HARDWARE_BOM.md` — earlier system
  and hardware descriptions.
- `DASHBOARD.md`, `SOFTWARE.md`, `API.md` — earlier software contracts.
- `SENSOR_*`, `CALIBRATION_GUIDE.md`, `TEST_PLAN.md` — sensor and test planning.
- `CHANGELOG.md`, `VERSION_HISTORY.md` — change history.
- `blueprints/` and `diagrams/` — early renders and wiring diagrams.

Some older documents link to paths such as `docs/PROJECT_CONTEXT.md`. Those
links are archived references and may no longer resolve from `docs/`.
