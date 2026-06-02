# SQL and Notebooks

## Analyst Toolkit

The Analyst Toolkit provides:

- SQL template execution
- CSV export
- JSON export
- notebook download
- template download

## SQL templates

Located in:

```text
sql/analyst_templates/
```

Templates use placeholders:

```text
{time_filter}
{incident_time_filter}
{event_time_filter}
{quality_time_filter}
{active_filter}
{limit}
```

These are filled from current dashboard filters.

## Notebooks

Located in:

```text
notebooks/
```

Included notebooks:

```text
01_hot_zone_analysis.ipynb
02_build_regression_analysis.ipynb
03_fix_validation.ipynb
04_rule_quality_review.ipynb
```

## Recommended workflow

```text
1. Identify a problem in the dashboard
2. Open Analyst Toolkit
3. Run the matching SQL template
4. Export CSV/JSON
5. Continue analysis in notebook
6. Attach finding to Incident Workflow
```

## Notebook environment

The notebooks expect ClickHouse connection environment variables:

```text
CLICKHOUSE_HOST
CLICKHOUSE_PORT
CLICKHOUSE_DATABASE
CLICKHOUSE_USERNAME
CLICKHOUSE_PASSWORD
```

Defaults are configured for local development.
