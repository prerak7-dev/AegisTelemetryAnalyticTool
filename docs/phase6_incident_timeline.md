# Phase 6 — Historical Incident Replay and Root-Cause Timeline

Phase 6 adds a new dashboard workspace:

```text
Incident Timeline
```

## Purpose

The Incident Timeline workspace explains how an incident developed before, during, and after the trigger window.

It follows this sequence:

```text
Incident starts
        ↓
Player density rises
        ↓
AoE / physics / network signal spikes
        ↓
Server frame time degrades
        ↓
Desync / rubberband impact appears
        ↓
Recommendation triggers
```

## What the view shows

- incident selector
- source profile, server, zone, map, region, build context
- replay window controls
- root-cause sequence table
- metric timelines before/during/after incident
- subsystem pressure timeline
- network/player-impact timeline
- memory/CPU/AI timeline
- top event type and top ability ID over time
- recommendation changes over the replay window
- raw evidence payload

## Data sources

The workspace uses existing tables:

```text
incidents
agg_zone_30s
```

No new database schema is required.
