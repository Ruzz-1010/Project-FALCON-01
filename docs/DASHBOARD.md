# Dashboard Specification v6.1

> Prototype visual status: the current 3D buoy asset is a reference model under redesign. Live data behavior and the four-page Bay Station information architecture remain valid; replace the model only from the approved new mechanical revision.

The shore Bay Station-hosted `dashboard-next/` application has four primary pages in this order: **Overview**, **Buoy Motion**, **Sensors**, and **Logs & Alerts**. GPS position/security details are grouped under Sensors and summarized on Overview. Logs & Alerts is intentionally last, while Settings remains a compact header action.

Overview requires no graph-selection controls. It shows one large Estimated Wave Height graph with a muted blue-gray pressure-derived line and a labeled red historical AI-comparison line; the future predicted value remains in a separate always-visible FALCON AI card so it cannot be mistaken for a measured value. It also shows one Station Status summary and compact trends for Water Pressure, Wind Speed, and GPS Distance from Anchor. Battery, solar, water temperature, and enclosure temperature remain clear current readings. FALCON Assistant assets are preserved but not currently mounted. Buoy Motion remains a pressure-driven visualization, while Sensors groups Wave & Pressure, GPS & Security, Wind, Water, Power, and System. Logs & Alerts combines active alerts with persisted telemetry, security/calibration events, search, acknowledgement, and export.

The operator palette uses a warm light-gray background, soft-white cards, charcoal text, muted teal accents, pale borders, and low-opacity graph fills. Strong green, amber, and red are reserved for meaningful status changes and alerts to reduce visual fatigue for older users.

Typography is intentionally neutral across every page: soft charcoal for headings and primary values, calm gray for labels and explanations, and no decorative colored text. Green, amber, and red text is reserved only for genuine normal, warning, and alert states.

Graph styling is also standardized across Overview and technical pages: measured data uses one muted blue-gray/teal line, rolling trends use a nearby neutral gray, fills remain very light, and grid lines remain pale. Forecast, limit, or warning references may use subdued brown/amber solely to distinguish their meaning; bright cyan, orange, purple, and green graph lines are not used.

The Overview automatically shows a large `CALM`, `MODERATE`, or `ROUGH` sea-condition badge beside the current estimated wave height. Thresholds are consistent with the edge classification: below 0.60 m is Calm, 0.60–2.49 m is Moderate, and 2.50 m or higher is Rough. This is a current monitoring classification, not a forecast and not a clickable scenario control.

All values must distinguish `LIVE`, `SIMULATED`, `ESTIMATED`, `CALIBRATION REQUIRED`, `STALE`, `OFFLINE`, `COLLECTING`, and `MODEL OUTPUT`. AI prediction is visible by default and is never presented as a measured value or official forecast. The former separate Wave, GPS, Power, System, History, and Alerts modules are legacy implementation files and are not primary navigation.

The dashboard must remain responsive at 320 px and above, keyboard usable, readable in light/dark themes, and functional when the AI predictor is collecting data or unavailable.
