from __future__ import annotations

import pandas as pd
import streamlit as st
import clickhouse_connect

from services.dashboard.config import (
    ALL_REGIONS,
    ALL_SERVERS,
    ALL_SOURCE_PROFILES,
    CLICKHOUSE_DATABASE,
    CLICKHOUSE_HOST,
    CLICKHOUSE_PASSWORD,
    CLICKHOUSE_PORT,
)

@st.cache_resource
def get_client():
    return clickhouse_connect.get_client(
        host=CLICKHOUSE_HOST,
        port=CLICKHOUSE_PORT,
        database=CLICKHOUSE_DATABASE,
        username="default",
        password=CLICKHOUSE_PASSWORD,
    )

@st.cache_data(ttl=4, show_spinner=False)
def query_df_cached(sql: str) -> pd.DataFrame:
    return get_client().query_df(sql)

def query_df(sql: str, *, cached: bool = True) -> pd.DataFrame:
    if cached:
        return query_df_cached(sql)
    return get_client().query_df(sql)

def clear_query_cache() -> None:
    query_df_cached.clear()

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
