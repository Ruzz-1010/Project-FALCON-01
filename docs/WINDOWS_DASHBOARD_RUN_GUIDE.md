# Project FALCON dashboards — Windows run guide

This guide runs the Project FALCON interfaces on one Windows laptop. The commands use **PowerShell**. Keep each running service in its own PowerShell window.

## Interfaces and local addresses

| Interface | Purpose | Address |
| --- | --- | --- |
| Operator dashboard | Detailed station monitoring, sensors, prediction, logs, and alerts | `http://127.0.0.1:8765/` |
| Public dashboard | Read-only Palawan station map | `http://127.0.0.1:5176/` |
| AI calculation demo | Manual explanation of the pressure-to-wave and damped-trend calculation | `http://127.0.0.1:5178/` |
| Thesis presentation (optional) | Interactive project presentation | `http://127.0.0.1:5175/` |

The values shown by the commands below are **simulated demonstration data**. They are not field-validated sensor measurements.

## 1. Install the required software

Install these once:

1. **Python 3.10 or newer** — enable **Add Python to PATH** during installation.
2. **Node.js 20.19 or newer (LTS)** — npm is included with Node.js.
3. **Git** — required only when cloning or updating the repository from GitHub.

Open PowerShell and verify the installations:

```powershell
py -3 --version
node --version
npm --version
git --version
```

If `py` is unavailable but `python` works, replace `py -3` with `python` in the commands below.

## 2. Set the project location

Change the example path to the actual location of the repository:

```powershell
$FalconRoot = "C:\Users\YOUR_NAME\Documents\PlatformIO\Projects\Project FALCON-01"
Set-Location $FalconRoot
```

Confirm that the correct folder is open:

```powershell
Get-ChildItem
```

The list should include `dashboard-next`, `public-dashboard`, `edge`, and `demo`.

## 3. First-time frontend installation

Run this once, or again after `package.json` changes:

```powershell
Set-Location "$FalconRoot\dashboard-next"
npm install
```

The public dashboard reuses the Vite installation in `dashboard-next\node_modules`, so the command above must finish successfully before running the public dashboard.

## 4. Build the operator dashboard

Build the latest React operator dashboard into the edge service:

```powershell
Set-Location "$FalconRoot\dashboard-next"
npm run build
```

A successful build ends without TypeScript or Vite errors and writes the dashboard to `edge\static\dashboard`.

## 5. Run the operator dashboard

Open a new PowerShell window and run:

```powershell
$FalconRoot = "C:\Users\YOUR_NAME\Documents\PlatformIO\Projects\Project FALCON-01"
Set-Location "$FalconRoot\edge"
py -3 -m falcon_edge.service --source simulator --port 8765
```

Leave this window open. Open the operator dashboard at:

```text
http://127.0.0.1:8765/
```

This is the recommended operator-dashboard command for a defense demonstration because one service provides both the API and the built dashboard.

### Operator development mode

Use this only while editing the React interface. Keep the edge service on port `8765`, then open another PowerShell window:

```powershell
$FalconRoot = "C:\Users\YOUR_NAME\Documents\PlatformIO\Projects\Project FALCON-01"
Set-Location "$FalconRoot\dashboard-next"
npm run dev
```

Open `http://127.0.0.1:5173/`. Changes to the frontend reload automatically. The operator production page remains available at port `8765` until it is rebuilt.

## 6. Run the public dashboard

The public dashboard is configured to read its live demonstration values from a separate edge service on port `8767`. A separate database file prevents the two simulator services from writing to the same SQLite database.

Open another PowerShell window:

```powershell
$FalconRoot = "C:\Users\YOUR_NAME\Documents\PlatformIO\Projects\Project FALCON-01"
Set-Location "$FalconRoot\edge"
py -3 -m falcon_edge.service --source simulator --port 8767 --database data\falcon-public-demo.db
```

Leave it open. Open one more PowerShell window:

```powershell
$FalconRoot = "C:\Users\YOUR_NAME\Documents\PlatformIO\Projects\Project FALCON-01"
Set-Location "$FalconRoot\public-dashboard"
npm run dev
```

Open:

```text
http://127.0.0.1:5176/
```

The four Palawan stations are presentation/test-map stations. FALCON-01 reads from the demonstration edge service; other station values remain clearly labeled as simulated until physical station endpoints exist.

## 7. Run the AI calculation demo

The AI calculation demo is a static teaching page and does not require the edge service.

Open another PowerShell window:

```powershell
$FalconRoot = "C:\Users\YOUR_NAME\Documents\PlatformIO\Projects\Project FALCON-01"
Set-Location $FalconRoot
py -3 -m http.server 5178 --directory "demo\ai-prediction"
```

Open:

```text
http://127.0.0.1:5178/
```

The direct calculation page is:

```text
http://127.0.0.1:5178/calc.html
```

This page demonstrates the damped linear-trend **baseline**. It is not a trained Random Forest model and must not be presented as field-validated AI.

## 8. Run the thesis presentation (optional)

Install its dependencies once:

```powershell
Set-Location "$FalconRoot\static website presentation"
npm install
```

Run it:

```powershell
npm run dev
```

Open:

```text
http://127.0.0.1:5175/
```

## Recommended defense setup

Run these four PowerShell windows and keep them open:

| Window | Command/folder | Required for |
| --- | --- | --- |
| 1 | Edge service on `8765` | Operator dashboard |
| 2 | Edge service on `8767` with `falcon-public-demo.db` | Public-dashboard data |
| 3 | `npm run dev` in `public-dashboard` | Public dashboard |
| 4 | Python HTTP server on `5178` | AI calculation demo |

Before presenting, open all three pages and refresh them once:

```text
Operator: http://127.0.0.1:8765/
Public:   http://127.0.0.1:5176/
AI demo:  http://127.0.0.1:5178/
```

The operator React development server on `5173` is unnecessary during the defense unless the team is actively editing the interface.

## Stop the services

Click each PowerShell window and press:

```text
Ctrl+C
```

## Troubleshooting

### `npm` is not recognized

Install or reinstall Node.js, close all PowerShell windows, and open PowerShell again. Check:

```powershell
node --version
npm --version
```

### `py` or `python` is not recognized

Reinstall Python with **Add Python to PATH** enabled, then reopen PowerShell.

### Port is already in use

Find the process using the port. Replace `8765` with `8767`, `5176`, `5178`, or another affected port:

```powershell
Get-NetTCPConnection -LocalPort 8765 -ErrorAction SilentlyContinue |
    Select-Object LocalAddress, LocalPort, State, OwningProcess
```

Stop only the process that belongs to an old FALCON run:

```powershell
Stop-Process -Id PROCESS_ID
```

Then run the correct command again.

### Public dashboard opens but values do not update

Confirm that both are running:

1. the edge service on `http://127.0.0.1:8767`; and
2. the public Vite server on `http://127.0.0.1:5176`.

Do not point the public dashboard directly at `5176` as its data service; `5176` is the frontend and `8767` is its API.

### Operator page is outdated

Stop the edge service, rebuild, and start it again:

```powershell
Set-Location "$FalconRoot\dashboard-next"
npm run build
Set-Location "$FalconRoot\edge"
py -3 -m falcon_edge.service --source simulator --port 8765
```

Then use `Ctrl+F5` in the browser.

### Windows Firewall prompt

For a demonstration on the same laptop, allow access only on **Private networks**. The pages use local addresses and do not need to be exposed publicly.

## Using physical ESP32 data later

Do not use this during the defense unless the ESP32 endpoint has already been tested. Replace the operator simulator command with:

```powershell
Set-Location "$FalconRoot\edge"
py -3 -m falcon_edge.service --source esp32 --esp32-url http://192.168.4.1 --port 8765
```

The laptop must be connected to the correct ESP32/network endpoint. If the physical connection fails, the service reports the failure rather than silently replacing it with simulated data.
