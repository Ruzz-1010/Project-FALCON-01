# Event Driven Cloud Buoy Architecture v2.0


<!-- FALCON-DOST-REVISION-NOTE:START -->
> **Current revision note (2026-10-10):** Use the DOST major revision baseline in [`docs/REVISION_2026-10-10.md`](REVISION_2026-10-10.md) unless this file is explicitly archived. The active design is a compact single-tube / small-buoy, ESP32-based, event-driven, cloud-first system. LoRa, large Bay Station hardware, tall tower layouts, and continuous every-second uploads are legacy or optional fallback assumptions.
<!-- FALCON-DOST-REVISION-NOTE:END -->

Authority: `PROJECT_CONTEXT.md` and the revised BOM in `THESIS DOCUMENTATION/FALCON Revised Event Driven BOM and Sensor Options.docx`.

## Approved split

```text
Buoy sensors -> ESP32 acquisition / validation / event detection / buffer
             -> Wi-Fi for laboratory tests or 4G/LTE for field tests
             -> cloud API / database / dashboard / alerts
             -> authorized laptop, tablet, or phone
```

No mini PC, LoRa gateway, database server, or AI runtime is installed on the buoy. The ESP32 is the only required controller. The cloud service may be hosted on a development computer during testing and moved to a selected provider after the endpoint, security, and cost are approved.

## Buoy responsibilities

- Acquire timestamped pressure and approved optional wind, GPS, power, health, and security signals.
- Sample locally at the selected rate and calculate short-window summaries.
- Detect significant pressure or movement changes, displacement, tamper, low battery, sensor faults, and connection recovery.
- Frame versioned event and summary telemetry with a unique packet identifier.
- Upload summaries every 1–5 minutes during normal operation and event packets immediately when a threshold is met.
- Buffer records in flash or microSD during Wi-Fi/LTE outages and preserve original timestamps.
- Reconnect with backoff and retransmit queued records without duplicate insertion.

## Cloud responsibilities

- Authenticate the buoy and validate payloads.
- Store raw or summarized records and retain event history.
- Derive pressure-based estimated wave height and expose its calibration/quality state.
- Serve the responsive dashboard, logs, alerts, and exports.
- Run optional heavier prediction or analysis without blocking acquisition.
- Mark stale, offline, simulated, estimated, and calibration-required states explicitly.

## Event-driven reporting rule

The ocean is continuously moving, so “movement” must not mean every individual wave. The ESP32 keeps sampling locally. It sends a regular summary so the cloud remains current, then sends an immediate event when the measured signal changes materially from its learned baseline or when a system-health rule is met. Thresholds must be tuned from measured baseline data rather than invented before calibration.

```text
continuous local samples
        |
one-minute pressure/motion summary
        |-------------------------------|
normal summary every 1–5 minutes    immediate event on anomaly/fault
        |-------------------------------|
Wi-Fi or LTE upload / local buffer when offline
```

## Selection gates

The exact pressure transmitter, wind sensor, movement sensor, LTE modem, antenna, SIM/data plan, cloud endpoint, HTTPS or MQTT protocol, device identity, packet format, retry policy, buffer capacity, and security controls remain `TBD` until supplier and site tests are complete. Wi-Fi is the approved bench path. LTE is required for a remote field path unless the site provides reliable shore Wi-Fi.

## Failure and power boundaries

- Wi-Fi/LTE loss: sensing and local event detection continue; records are buffered and synchronized after reconnection.
- Cloud outage: the buoy continues sampling and buffering; the dashboard marks data stale or offline.
- LTE reconnect: the modem may draw a short current peak; the regulator and battery must be tested against that peak.
- Stale or uncalibrated inputs: wave estimates are withheld or explicitly qualified.
- Prediction failure: acquisition, storage, live status, and alerts continue.
- Buoy power budget covers ESP32, approved sensors, modem, security inputs, storage, and conversion losses.
- Cloud or development-computer power is a separate shore/infrastructure budget.

## Required acceptance tests

1. Wi-Fi bench upload and cloud authentication.
2. LTE registration, signal survey, data-usage measurement, and reconnect test at the proposed site.
3. Event threshold tests using controlled pressure and tilt changes.
4. Summary upload interval, immediate event latency, duplicate prevention, and timestamp preservation.
5. Offline buffering, restart recovery, and queued-record synchronization.
6. Battery-regulator test during modem registration and transmit peaks.
7. Cloud storage, dashboard freshness, stale-state behavior, and export verification.

