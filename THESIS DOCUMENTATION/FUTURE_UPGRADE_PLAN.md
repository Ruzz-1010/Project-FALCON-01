# Project FALCON Future Upgrade Plan

## Current Baseline

Project FALCON Phase 1 uses a shore-based Bay Station architecture. The final mini PC remains subject to approval and measured workload requirements; no Orange Pi or mini PC is installed on the buoy. The items below are future improvements only after approval, funding, and field validation.

## Recommended Future Improvements

### 1. Improve reliability before adding features

The first upgrade should strengthen waterproofing, corrosion protection, cable
labeling, modular connectors, thermal control, leak detection, remote recovery,
and solar/battery monitoring. These changes make the buoy safer, easier to
maintain, and more sustainable over repeated deployments.

### 2. Add an on-demand viewing camera

A weatherproof USB camera may provide live visual inspection of the buoy and its
surroundings. It should stream only when an authorized operator opens the camera
page. Routine video recording is not proposed, so the camera will not continually
consume local storage. The design still requires power, bandwidth, waterproofing,
condensation, cybersecurity, privacy, and maintenance testing.

### 3. Add research-justified environmental sensors

Possible sensors include pH, salinity/conductivity, turbidity, dissolved oxygen,
water temperature, chlorophyll-a, rain, UV, water current, and a hydrophone. The
team should not install every sensor simply to increase feature count. Each sensor
must answer an approved research question and have a calibration method, reference
instrument, uncertainty estimate, cleaning plan, power budget, and dashboard state.

### 4. Improve long-distance communication

The proposal baseline uses LoRa as the planned low-rate buoy link to a nearby
barangay-hall gateway. SIM/4G/5G is planned at the Bay Station for Internet
backhaul, cloud upload, and authorized remote access. Satellite messaging or
additional gateways may be considered later for remote sites, subject to power,
coverage, cost, cybersecurity, and validation evidence. FALCON should continue
storing data locally and synchronize queued records after a connection returns.

### 5. Upgrade to Raspberry Pi 5 4GB when justified

Raspberry Pi 5 may provide smoother operation for heavier analytics, camera
processing, additional services, or a larger dashboard workload. It is not needed
for the current Phase 1 pipeline. Before upgrading, the team must demonstrate an
Bay Station performance limitation and revise shore power/UPS, cooling, storage, networking, and recovery tests. Raspberry Pi 5 remains shore based and never enters the buoy solar budget.

## Suggested Presentation Script

> “For Phase 1, Project FALCON will use a shore-based Bay Station mini PC selected from measured storage, dashboard, and AI requirements. No mini PC is installed on the buoy. If the project is approved and receives additional funding, we will
> improve reliability first, then consider an on-demand camera, calibrated
> environmental sensors, and stronger remote communication. A Raspberry Pi 5 may
> be adopted later if actual benchmarks show that heavier analytics require more
> processing power. Every upgrade will undergo renewed power, calibration,
> waterproofing, cybersecurity, and field validation before deployment.”

## Important Claim Boundary

These are proposed upgrades, not existing capabilities. They must not be presented
as installed, tested, accurate, or deployment-ready until documented evidence is
available. The detailed engineering gates are maintained in
[`../docs/FUTURE_UPGRADES.md`](../docs/FUTURE_UPGRADES.md).
