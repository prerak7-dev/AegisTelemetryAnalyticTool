# Phase 7 — Multi-Dimensional Live Pressure Command Center

Phase 7 promotes all major degradation signals into the Command Center.

Before Phase 7, the Command Center was too frame-time-centric. P95 server frame time was highly visible, while other pressure signals were mostly used as incident evidence.

Phase 7 changes Command Center into a multidimensional live-ops surface.

## New first-class pressure dimensions

```text
Simulation Pressure
Network Pressure
Replication Pressure
Physics Pressure
Memory Pressure
AI Pressure
Matchmaking Pressure
Player Impact Pressure
Telemetry Quality Pressure
```

## Why this matters

P95 server frame time is a symptom. It can tell analysts that the server is slow, but it does not explain why.

Phase 7 surfaces the likely pressure domain before analysts enter the incident dossier:

```text
server slow?
network saturated?
replication too expensive?
physics event storm?
memory pressure?
AI/pathfinding pressure?
matchmaking/capacity stress?
player-facing desync/rubberbanding?
telemetry too incomplete to trust?
```

## Command Center additions

The Command Center now includes:

```text
Live Pressure Overview cards
Pressure Trend Timeline
Pressure Ranking chart
Pressure Drilldown selector/table
Frame-Time Symptom View
Source + Regional Pressure Summary
```

## State model

This phase does not change ingestion, schema adaptation, incident rules, or navigation. It only promotes existing telemetry fields into a better top-level operations surface.
