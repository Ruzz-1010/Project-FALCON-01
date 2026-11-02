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

The map is designed to list each approved FALCON station as it becomes available. It does not invent additional deployed buoy locations for the demonstration.
