# Phase 11.1 — Demo Configuration Packaging Fix

This patch fixes:

```text
No demo scenarios are configured. Check config/demo_scenarios.json.
```

## Root cause

The scenario library existed in the project at:

```text
config/demo_scenarios.json
```

but the dashboard Docker image did not copy or mount:

```text
config/
simulator/
```

into `/app`.

The Demo Control Center was looking for:

```text
/app/config/demo_scenarios.json
```

so it could not find the scenario library at runtime.

## Fixes

### Dockerfile

`services/dashboard/Dockerfile` now copies:

```text
config -> /app/config
simulator -> /app/simulator
```

and installs simulator requirements so the dashboard can launch scenario generators.

### Docker Compose

The dashboard service now mounts:

```text
./config:/app/config:ro
./simulator:/app/simulator:ro
./data:/app/data
```

This means users can edit scenario/config files without rebuilding the dashboard image.

### Commands

Demo Control Center now shows both:

```text
Container command used by Start Scenario
Host command you can copy from the project root
```

Container commands use:

```text
http://collector:8000
/app/simulator/generate_traffic.py
```

Host commands use:

```text
http://localhost:8000
simulator/generate_traffic.py
```

## Features now backed by actual configuration

```text
configurable scenario library
start scenario from dashboard
stop all scenario generators
stop individual generator
reset demo data with confirmation
copyable generated terminal commands
downloadable demo runbook
recent demo launch history
```
