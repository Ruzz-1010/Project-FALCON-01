# FALCON Public Dashboard

Read-only public-facing coastal map for Project FALCON. It intentionally shows only a simplified station summary:

- station status;
- pressure-derived estimated wave condition;
- wind observation; and
- last update time.

It does not expose raw records, controls, exact buoy coordinates, maintenance settings, security status, or operator logs.

## Run locally

Start the FALCON edge service first (the default Vite proxy points to its demo service at port `8767`):

```bash
cd edge
python3 -m falcon_edge.service --source simulator --port 8767
```

In another terminal:

```bash
cd public-dashboard
npm run dev
```

Open `http://127.0.0.1:5176/`.

The map is constrained to Palawan and currently contains four test-map stations at the team-provided pins for Puerto Princesa, Dumaran, Roxas, and San Vicente. FALCON-01 reads from the edge service; the other cards use visibly simulated live values until their physical buoy endpoints are connected. Test markers are a UI demonstration, not a claim of field deployment.
