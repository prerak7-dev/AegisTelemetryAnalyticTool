from __future__ import annotations

import re

import streamlit as st

from services.dashboard.performance_config import cfg_get, feature_enabled, table_name
from services.dashboard.query import get_client

VALID_TABLE_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)?$")

def _safe_table_identifier(value: str) -> str:
    raw = str(value or "").strip()
    if not VALID_TABLE_RE.match(raw):
        raise ValueError(f"Unsafe ClickHouse table identifier: {raw!r}")
    return raw

@st.cache_data(ttl=30, show_spinner=False)
def clickhouse_table_exists(table_identifier: str) -> bool:
    """Return whether a table/view exists without breaking dashboard render."""
    try:
        safe = _safe_table_identifier(table_identifier)
        if "." in safe:
            database, table = safe.split(".", 1)
            sql = (
                "SELECT count() AS c "
                "FROM system.tables "
                f"WHERE database = '{database}' AND name = '{table}'"
            )
        else:
            sql = (
                "SELECT count() AS c "
                "FROM system.tables "
                "WHERE database = currentDatabase() "
                f"AND name = '{safe}'"
            )
        result = get_client().query(sql)
        return bool(result.result_rows and int(result.result_rows[0][0] or 0) > 0)
    except Exception:
        return False

def live_snapshots_enabled() -> bool:
    return feature_enabled("prefer_live_snapshot_tables", True)

def configured_snapshot_table(config_key: str, fallback_key: str = "aggregate_zone_table") -> str:
    configured = cfg_get(f"tables.{config_key}", None)
    if configured:
        return str(configured)
    return table_name(fallback_key)

def preferred_live_table(
    *,
    snapshot_config_key: str,
    fallback_config_key: str = "aggregate_zone_table",
) -> tuple[str, bool]:
    """Return (table_name, using_snapshot).

    Uses the configured snapshot table when:
    - feature flag prefer_live_snapshot_tables is enabled
    - the table/view exists in ClickHouse

    Otherwise returns the existing aggregate table so old volumes and partial
    deployments continue to work.
    """
    fallback = table_name(fallback_config_key)
    if not live_snapshots_enabled():
        return fallback, False

    candidate = configured_snapshot_table(snapshot_config_key, fallback_config_key)
    if candidate != fallback and clickhouse_table_exists(candidate):
        return candidate, True
    return fallback, False

def snapshot_badge(label: str, using_snapshot: bool) -> str:
    mode = "snapshot" if using_snapshot else "aggregate fallback"
    return f"{label}: {mode}"
