# Phase 12.5 — Professional Documentation Workspace

This phase adds a professional documentation layer inside the dashboard.

## New workspace

```text
Data & Schemas > Documentation
```

## What it adds

```text
configuration-backed documentation registry
separate documentation navigation
hierarchical documentation sections
user guide
developer guide
data reference
operations reference
search
page outline
markdown page download
documentation inventory
```

## Configuration

Navigation is configured in:

```text
config/documentation_navigation.json
```

Documentation pages are stored under:

```text
docs/toolkit/
```

Dashboard settings are configured in:

```text
config/dashboard_performance.json
```

under:

```text
documentation_workspace
```

## Documentation hierarchy

```text
Getting Started
User Guide
Developer Guide
Data Reference
Operations Reference
```

## Adding a documentation page

1. Add a markdown file under:

```text
docs/toolkit/<section>/<page>.md
```

2. Register it in:

```text
config/documentation_navigation.json
```

3. Restart or refresh the dashboard.

## Docker packaging

The dashboard now includes and mounts:

```text
docs -> /app/docs
```

so documentation can be edited locally without rebuilding the dashboard image.
