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

The map is constrained to Palawan and currently contains FALCON-01 plus clearly labelled test-map stations in Napsan, Dumaran, and Roxas. Test markers are a UI demonstration, not a claim of field deployment.
