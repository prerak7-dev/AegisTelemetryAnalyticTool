# Phase 2.5 — Performance and Premium Dashboard Design

## Why the dashboard felt laggy

The previous dashboard used Streamlit tabs. Streamlit evaluates every tab body on each rerun, even when the user is only viewing one tab. With live refresh enabled, the app repeatedly queried Command Center, Selected Server Analytics, Incident Deep Dive, Data Quality, and Scaling Readiness.

## Performance fixes

1. Replaced tabs with a folder-style workspace selector.
   - Only the selected workspace runs its ClickHouse queries.
   - This significantly reduces dashboard query load.

2. Added cached ClickHouse reads.
   - Query results are cached for a short TTL.
   - A `Refresh now` button clears the query cache manually.

3. Live refresh is off by default.
   - This prevents constant reruns while exploring.
   - The sidebar lets the user choose 5, 10, 20, or 30 second refresh cadence.

4. Added table row limits.
   - Expensive table views default to limited rows.
   - The user can increase the limit from the sidebar.

5. Bounded dashboard queries.
   - Server inventory now uses the selected time window.
   - Charts and tables use explicit `LIMIT` clauses.

## Premium visual update

The dashboard now uses a dark studio-dossier style:

- Bold hero header
- Dark red/gold accents
- Folder-like workspace selector
- Paper-card metric panels
- Glass/dossier panels
- More premium portfolio presentation

This is inspired by the broad feel of the Guerrilla Games website—bold dark presentation, prominent navigation, and cinematic studio identity—without copying proprietary assets, logos, or exact branded artwork.

## Usage

```bash
docker compose down -v
docker compose up --build
```

Then generate traffic:

```bash
cd simulator
python generate_traffic.py --scenario weekend_event_meltdown --collector-url http://localhost:8000 --events-per-second 1000 --duration-sec 240
```

Open:

```text
http://localhost:8501
```

Recommended demo settings:

- Live refresh: off while exploring
- Refresh now: use manually between narration beats
- Analysis window: last 30 minutes
- Table row limit: 50
