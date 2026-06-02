# Operations Workspaces

## Command Center

The Command Center is the executive operational view.

Use it to answer:

- Is the fleet healthy?
- Which pressure dimension is dominant?
- Is this a simulation, network, replication, physics, memory, AI, matchmaking, or player-impact issue?
- Which source profile, region, or server is most affected?

Important sections:

| Section | Use |
|---|---|
| Live Pressure Overview | Top-level pressure cards |
| Pressure Timeline | See pressure changes over time |
| Pressure Drilldown | Find affected server/map/zone windows |
| Baseline Preview | Early context-aware threshold view |
| Source + Regional Summary | Compare pressure by source and region |

## Selected Server

Use this for focused investigation after the Command Center identifies a risky server.

Typical flow:

```text
Command Center
  ↓
Select region/server in sidebar
  ↓
Selected Server
```

## Scaling Readiness

Use this when preparing for events, releases, or higher load.

Questions it helps answer:

- Are current zones close to risk thresholds?
- Which regions are least ready for scale?
- Are network or replication pressures already high?
- Is a planned traffic increase safe?
