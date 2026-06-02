# Phase 11 — Portfolio Demo Mode and Scenario Library

This phase adds a polished portfolio/demo control surface.

## New workspace

```text
Demo > Demo Control Center
```

## What it adds

```text
Configurable scenario library
Start scenario
Stop all scenario generators
Stop individual generator
Reset demo data with confirmation
Generated terminal commands
Downloadable demo runbook
Recent demo launch history
```

## Scenario library

Scenarios are configured in:

```text
config/demo_scenarios.json
```

This keeps the demo system editable without code changes.

Each scenario supports:

```text
id
title
category
description
recommended workspace
default duration
default events per second
one or more simulator commands
talk track
```

## Robust launch behavior

Launch behavior is controlled in:

```text
config/dashboard_performance.json
```

under:

```text
demo_control_center
```

Important settings:

```text
allow_subprocess_launch
python_executable
simulator_script_path
collector_url
default_batch_size
max_parallel_scenario_processes
enable_data_reset
reset_tables
scenario_history_path
```

If subprocess launch is disabled, the workspace still shows copyable commands.

## Included scenarios

```text
Normal Load
Weekend Event Meltdown
Network Packet Pressure
AI Pathfinding Spike
Memory Pressure
Physics Spike
Build Regression
Fix Validation
Custom Rule Trigger
```

## Safety

Demo data reset requires an explicit confirmation checkbox and only truncates configured tables.
