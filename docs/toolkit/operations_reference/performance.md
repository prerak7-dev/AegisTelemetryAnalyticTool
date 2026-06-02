# Performance and Query Strategy

## Current performance approach

The toolkit uses:

- ClickHouse aggregate tables
- query caching
- query budgets
- lazy-loaded expensive sections
- row limits
- filter-aware queries
- live feedback panels
- optional rollup SQL templates

## Query Performance workspace

Use:

```text
Data & Schemas > Query Performance
```

to review:

- query duration
- query budget
- over-budget status
- returned rows
- query errors
- cache policy

## How to improve slow workspaces

Prioritize:

```text
1. Narrow filters
2. Reduce row limits
3. Use aggregate tables
4. Add ClickHouse rollups
5. Add materialized views
6. Add indexes/order-by strategy
7. Only then consider parallelism
```

## Why not just add threads?

Multiple threads can help concurrent independent queries, but they do not fix:

- inefficient scans
- missing rollups
- large result sets
- broad filters
- expensive group-bys
- high-cardinality joins

The toolkit favors data-shape improvements before concurrency.

## Production recommendations

For production scale, add:

- materialized rollups for pressure summaries
- precomputed baseline windows
- build regression result tables
- fix validation result tables
- incident workflow database store
- consumer lag monitoring
- ClickHouse partitioning review
