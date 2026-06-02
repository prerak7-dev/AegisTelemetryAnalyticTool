# Phase 13.7 — Consistent Subnav Row Strategy

This patch changes the row-splitting rule to avoid uneven two-row layouts.

## Fixed

```text
Incidents no longer splits into an uneven 3/2 layout.
The empty trailing space caused by uneven row counts is removed.
Data & Schemas remains a clean 3/3 two-row layout.
Odd five-tab groups are kept as one balanced row.
Even long groups split evenly into two rows.
```

## Rule

```text
1-4 tabs:
  single row

5 tabs:
  single row to avoid 3/2 empty-space layout

6 tabs:
  two rows, 3/3

8 tabs:
  two rows, 4/4

larger odd counts:
  most balanced split possible
```

## Why this is more robust

The previous attempt tried to stretch the short second row after rendering, but Streamlit's nested column sizing could still produce leftover panel space. This patch avoids the bad layout case entirely by not creating uneven 3/2 rows.
