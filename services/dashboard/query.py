
from __future__ import annotations

import hashlib
import time
from concurrent.futures import ThreadPoolExecutor

import clickhouse_connect
import pandas as pd
import streamlit as st

from services.dashboard.config import (
    ALL_REGIONS,
    ALL_SERVERS,
    ALL_SOURCE_PROFILES,
    CLICKHOUSE_DATABASE,
    CLICKHOUSE_HOST,
    CLICKHOUSE_PASSWORD,
    CLICKHOUSE_PORT,
    QUERY_CACHE_TTL_LIVE,
    QUERY_CACHE_TTL_MEDIUM,
    QUERY_CACHE_TTL_SHORT,
    QUERY_CACHE_TTL_STATIC,
)
from services.dashboard.performance_config import (
    feature_enabled,
    query_budget_ms,
    cfg_get,
)

QUERY_HISTORY_KEY = "aegis_query_history"
MAX_QUERY_HISTORY = 250

@st.cache_resource
def get_client():
    return clickhouse_connect.get_client(
        host=CLICKHOUSE_HOST,
        port=CLICKHOUSE_PORT,
        database=CLICKHOUSE_DATABASE,
        username="default",
        password=CLICKHOUSE_PASSWORD,
    )

@st.cache_data(ttl=QUERY_CACHE_TTL_LIVE, show_spinner=False)
def query_df_cached_live(sql: str) -> pd.DataFrame:
    return get_client().query_df(sql)

@st.cache_data(ttl=QUERY_CACHE_TTL_SHORT, show_spinner=False)
def query_df_cached_short(sql: str) -> pd.DataFrame:
    return get_client().query_df(sql)

@st.cache_data(ttl=QUERY_CACHE_TTL_MEDIUM, show_spinner=False)
def query_df_cached_medium(sql: str) -> pd.DataFrame:
    return get_client().query_df(sql)

@st.cache_data(ttl=QUERY_CACHE_TTL_STATIC, show_spinner=False)
def query_df_cached_static(sql: str) -> pd.DataFrame:
    return get_client().query_df(sql)

def _sql_hash(sql: str) -> str:
    return hashlib.sha1(sql.encode("utf-8")).hexdigest()[:10]

def _record_query_metric(
    *,
    name: str,
    sql: str,
    duration_ms: float,
    rows: int,
    cache_policy: str,
    cached: bool,
    budget_ms: float | None = None,
    error: str | None = None,
) -> None:
    """Record lightweight query telemetry in Streamlit session state."""
    try:
        budget = float(budget_ms if budget_ms is not None else query_budget_ms(name))
        over_budget = bool(feature_enabled("enable_query_budget_warnings", True) and duration_ms > budget)
        history = st.session_state.setdefault(QUERY_HISTORY_KEY, [])
        history.append(
            {
                "query_name": name,
                "sql_hash": _sql_hash(sql),
                "duration_ms": round(float(duration_ms), 2),
                "budget_ms": round(float(budget), 2),
                "over_budget": over_budget,
                "rows": int(rows),
                "cache_policy": cache_policy,
                "cached": bool(cached),
                "error": error or "",
                "recorded_at": pd.Timestamp.utcnow().isoformat(),
            }
        )
        if len(history) > MAX_QUERY_HISTORY:
            del history[:-MAX_QUERY_HISTORY]
    except Exception:
        return

def _cached_query(sql: str, cache_policy: str) -> pd.DataFrame:
    policy = (cache_policy or "live").lower()
    if policy == "live":
        return query_df_cached_live(sql)
    if policy == "short":
        return query_df_cached_short(sql)
    if policy == "medium":
        return query_df_cached_medium(sql)
    if policy == "static":
        return query_df_cached_static(sql)
    return query_df_cached_live(sql)

def query_df(
    sql: str,
    *,
    cached: bool = True,
    cache_policy: str = "live",
    name: str | None = None,
    budget_ms: float | None = None,
) -> pd.DataFrame:
    """Run a ClickHouse query with diagnostics, cache tiers, and budgets."""
    query_name = name or "anonymous_query"
    start = time.perf_counter()
    try:
        if cached:
            df = _cached_query(sql, cache_policy)
        else:
            df = get_client().query_df(sql)
        duration_ms = (time.perf_counter() - start) * 1000
        _record_query_metric(
            name=query_name,
            sql=sql,
            duration_ms=duration_ms,
            rows=len(df),
            cache_policy=cache_policy,
            cached=cached,
            budget_ms=budget_ms,
        )
        return df
    except Exception as exc:
        duration_ms = (time.perf_counter() - start) * 1000
        _record_query_metric(
            name=query_name,
            sql=sql,
            duration_ms=duration_ms,
            rows=0,
            cache_policy=cache_policy,
            cached=cached,
            budget_ms=budget_ms,
            error=str(exc),
        )
        raise

def query_df_named(
    name: str,
    sql: str,
    *,
    cache_policy: str = "live",
    cached: bool = True,
    budget_ms: float | None = None,
) -> pd.DataFrame:
    return query_df(sql, cached=cached, cache_policy=cache_policy, name=name, budget_ms=budget_ms)

def run_parallel_queries(
    query_specs: dict[str, tuple[str, str]],
    *,
    max_workers: int | None = None,
) -> dict[str, pd.DataFrame]:
    """Run independent queries concurrently with a small configurable worker cap.

    `query_specs` maps query_name -> (sql, cache_policy).

    This should be used sparingly for independent dashboard panels only.
    """
    if not query_specs:
        return {}

    configured = int(cfg_get("parallelism.max_dashboard_workers", 3) or 3)
    fanout_cap = int(cfg_get("parallelism.max_clickhouse_fanout", 4) or 4)
    requested = int(max_workers or configured)
    worker_count = max(1, min(requested, fanout_cap, len(query_specs)))

    def _run(item: tuple[str, tuple[str, str]]) -> tuple[str, pd.DataFrame]:
        name, (sql, cache_policy) = item
        return name, query_df_named(name, sql, cache_policy=cache_policy)

    with ThreadPoolExecutor(max_workers=worker_count) as pool:
        return dict(pool.map(_run, query_specs.items()))

def get_query_history() -> pd.DataFrame:
    history = st.session_state.get(QUERY_HISTORY_KEY, [])
    if not history:
        return pd.DataFrame(
            columns=[
                "recorded_at",
                "query_name",
                "duration_ms",
                "budget_ms",
                "over_budget",
                "rows",
                "cache_policy",
                "cached",
                "sql_hash",
                "error",
            ]
        )
    return pd.DataFrame(history)

def clear_query_cache() -> None:
    query_df_cached_live.clear()
    query_df_cached_short.clear()
    query_df_cached_medium.clear()
    query_df_cached_static.clear()
    try:
        st.session_state[QUERY_HISTORY_KEY] = []
    except Exception:
        pass

def quote_sql(value: str) -> str:
    return "'" + value.replace("\\", "\\\\").replace("'", "\\'") + "'"

def source_filter_sql(selected_source_profile: str, table_alias: str | None = None) -> str:
    if selected_source_profile == ALL_SOURCE_PROFILES:
        return "1 = 1"
    prefix = f"{table_alias}." if table_alias else ""
    return f"{prefix}source_profile = {quote_sql(selected_source_profile)}"

def region_filter_sql(selected_region: str, table_alias: str | None = None) -> str:
    if selected_region == ALL_REGIONS:
        return "1 = 1"
    prefix = f"{table_alias}." if table_alias else ""
    return f"{prefix}region = {quote_sql(selected_region)}"

def server_filter_sql(selected_server: str, table_alias: str | None = None) -> str:
    if selected_server == ALL_SERVERS:
        return "1 = 1"
    prefix = f"{table_alias}." if table_alias else ""
    return f"{prefix}server_id = {quote_sql(selected_server)}"

def combined_filter_sql(
    selected_source_profile: str,
    selected_region: str,
    selected_server: str,
    table_alias: str | None = None,
) -> str:
    return (
        f"{source_filter_sql(selected_source_profile, table_alias)} "
        f"AND {region_filter_sql(selected_region, table_alias)} "
        f"AND {server_filter_sql(selected_server, table_alias)}"
    )
