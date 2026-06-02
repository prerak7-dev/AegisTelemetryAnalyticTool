# Quick Start

## 1. Start the stack

From the project root:

```bash
docker compose down --remove-orphans
docker compose up --build
```

Open:

```text
http://localhost:8501
```

## 2. Generate demo telemetry

Open:

```text
Demo > Demo Control Center
```

Choose a scenario, then click:

```text
Start scenario
```

The Live Demo Feedback panel shows whether the scenario has reached:

```text
generator running
raw events visible
aggregate windows available
incidents available
```

## 3. Explore core workspaces

Start with:

```text
Operations > Command Center
```

Then review:

```text
Incidents > Incident Dossier
Incidents > Incident Timeline
Incidents > Incident Workflow
Data & Schemas > Analyst Toolkit
```

## 4. Filter the dashboard

Use the sidebar filters:

```text
Source profile
Region
Server
Analysis window
Table row limit
```

The filter context strip below the workspace navigation shows what every table/chart is scoped to.

## 5. Export evidence

Open:

```text
Data & Schemas > Analyst Toolkit
```

Run a template and download:

```text
CSV
JSON
SQL template
Notebook
```

## Common first demo path

```text
1. Demo > Demo Control Center
2. Run Weekend Event Meltdown
3. Operations > Command Center
4. Incidents > Incident Dossier
5. Incidents > Incident Timeline
6. Incidents > Incident Workflow
7. Data & Schemas > Analyst Toolkit
```
