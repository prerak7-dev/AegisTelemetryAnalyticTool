# Phase 12 — Data Export, Analyst Notebooks, and SQL Templates

This phase adds reusable analyst workflows alongside the real-time dashboard.

## New workspace

```text
Data & Schemas > Analyst Toolkit
```

## What it adds

```text
filter-aware SQL template execution
CSV export
JSON export
downloadable SQL templates
downloadable notebooks
notebook-ready investigation workflows
```

## SQL templates

Added under:

```text
sql/analyst_templates/
```

Templates:

```text
hot_zone_summary.sql
incident_evidence.sql
source_profile_comparison.sql
build_regression_export.sql
fix_validation_export.sql
rule_quality_review.sql
```

Also added top-level discovery copies:

```text
sql/hot_zone_summary.sql
sql/build_regression.sql
sql/incident_evidence.sql
sql/source_profile_comparison.sql
sql/fix_validation.sql
sql/rule_quality_review.sql
```

## Notebooks

Added:

```text
notebooks/01_hot_zone_analysis.ipynb
notebooks/02_build_regression_analysis.ipynb
notebooks/03_fix_validation.ipynb
notebooks/04_rule_quality_review.ipynb
```

Each notebook includes:

```text
ClickHouse connection setup
editable investigation filters
SQL template loading
dataframe output
starter analysis cells
```

## Configuration

New section:

```text
analyst_toolkit
```

in:

```text
config/dashboard_performance.json
```

Configurable values:

```text
sql_template_dir
notebook_dir
export row limit options
default export row limit
template execution enabled/disabled
template registry
download formats
```

## Docker packaging

The dashboard container now includes/mounts:

```text
sql -> /app/sql
notebooks -> /app/notebooks
```

so templates and notebooks are available inside the dashboard workspace.
