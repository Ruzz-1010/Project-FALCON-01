# Dashboard Specification v8.4

## Current implemented layout — September 11, 2026

The approved coastal design is applied across Overview, Sensors, Buoy Motion, GPS, Logs & Alerts, and Settings. Navigation retains five main entries; Settings remains a header action. The older four-page proposal below is historical and does not describe the current navigation.

Overview now has one full-width wave chart, a current-condition badge beside the wave-height reading, and a clearly separate numeric AI research estimate in the same card. Earlier AI predictions are labeled separately in the chart legend. The former right-hand status card and mini-trend widgets are removed. A four-column readings strip shows wind, pressure, battery, and solar, followed by GPS security, enclosure temperature, and last-update information.

White cards, an off-white background, dark blue-gray text, muted blue navigation, larger controls, and responsive spacing are shared across all pages. Motion retains its existing 3D structure and controls. Sensor details remain expandable; logs retain search and export. Gentle transitions respect reduced-motion preferences. Data acquisition, estimation, and forecasting logic are unchanged.

Validation: TypeScript and production build passed. The 3D Motion bundle still triggers the existing large-chunk warning. Browser visual verification remains pending.

## Previous specification and implementation history

Source cleanup 2026-09-11: the saved FalconAssistant component/style remain in `archive/dashboard-next/src/`. Seven disconnected legacy pages were subsequently moved to Trash and remain recoverable from Git history. Active imports, current page components, shared CSS, API contracts, and model assets remain in `dashboard-next/`. See `archive/README.md` for recovery instructions.

UI revision 2026-09-11: the existing implementation keeps five navigation entries (Overview, Sensors, Buoy Motion, GPS, Logs & Alerts) and a Settings header button. This differs from the earlier four-page thesis proposal below; the current redesign preserves the working navigation pending a separate scope decision.

The refreshed shared theme uses white cards, a light gray background, dark blue-gray text, muted blue navigation and teal details. Sensor values and explanatory text are larger, cards reflow on smaller screens, and the current sea condition appears in one clearly labeled block. A wave-chart inspector supports pointer selection and a keyboard/touch range control for reading earlier values. Narrow displays scroll the chart locally to preserve axis readability.

Entrance transitions, expandable sensor details and a floating loading logo provide gentle animation. Reduced-motion preferences disable animation. Chart lines remain fully drawn during polling. Connection failures show the last received values with a reconnect message and a Try again button.

> Prototype visual status: the current 3D buoy asset is a reference model under redesign. Live data behavior and the four-page Bay Station information architecture remain valid; replace the model only from the approved new mechanical revision.

The shore Bay Station-hosted `dashboard-next/` application has four primary pages in this order: **Overview**, **Buoy Motion**, **Sensors**, and **Logs & Alerts**. GPS position/security details are grouped under Sensors and summarized on Overview. Logs & Alerts is intentionally last, while Settings remains a compact header action.

Overview requires no graph-selection controls. It shows one large Estimated Wave Height graph with a muted blue-gray pressure-derived line and a labeled red historical AI-comparison line; the future predicted value remains in a separate always-visible FALCON AI card so it cannot be mistaken for a measured value. It also shows one Station Status summary and compact trends for Water Pressure, Wind Speed, Wind Direction, and GPS Distance from Anchor. Battery and solar status remain supporting telemetry. FALCON Assistant assets are preserved but not currently mounted. Buoy Motion remains a pressure-driven visualization, while Sensors groups Wave & Pressure, Wind, and Supporting Telemetry. Water-temperature and other environmental sensor views are excluded from the active proposal scope. Logs & Alerts combines active alerts with persisted telemetry, security/calibration events, search, acknowledgement, and export.

The operator palette uses a warm light-gray background, soft-white cards, charcoal text, muted teal accents, pale borders, and low-opacity graph fills. Strong green, amber, and red are reserved for meaningful status changes and alerts to reduce visual fatigue for older users.

Typography is intentionally neutral across every page: soft charcoal for headings and primary values, calm gray for labels and explanations, and no decorative colored text. Green, amber, and red text is reserved only for genuine normal, warning, and alert states.

Graph styling is also standardized across Overview and technical pages: measured data uses one muted blue-gray/teal line, rolling trends use a nearby neutral gray, fills remain very light, and grid lines remain pale. Forecast, limit, or warning references may use subdued brown/amber solely to distinguish their meaning; bright cyan, orange, purple, and green graph lines are not used.

The Overview automatically shows a large `CALM`, `MODERATE`, or `ROUGH` sea-condition badge beside the current estimated wave height. Thresholds are consistent with the edge classification: below 0.60 m is Calm, 0.60–2.49 m is Moderate, and 2.50 m or higher is Rough. This is a current monitoring classification, not a forecast and not a clickable scenario control.

All values must distinguish `LIVE`, `SIMULATED`, `ESTIMATED`, `CALIBRATION REQUIRED`, `STALE`, `OFFLINE`, `COLLECTING`, and `MODEL OUTPUT`. AI prediction is visible by default and is never presented as a measured value or official forecast. The former separate Wave, GPS, Power, System, History, and Alerts modules are legacy implementation files and are not primary navigation.

The dashboard must remain responsive at 320 px and above, keyboard usable, readable in light/dark themes, and functional when the AI predictor is collecting data or unavailable.
