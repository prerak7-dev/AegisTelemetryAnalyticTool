from __future__ import annotations

import os
from dataclasses import dataclass

CLICKHOUSE_HOST = os.getenv("CLICKHOUSE_HOST", "localhost")
CLICKHOUSE_PORT = int(os.getenv("CLICKHOUSE_PORT", "8123"))
CLICKHOUSE_DATABASE = os.getenv("CLICKHOUSE_DATABASE", "aegis_telemetry")
CLICKHOUSE_PASSWORD = os.getenv("CLICKHOUSE_PASSWORD", "aegis_dev_password")

SOURCE_SCHEMA_DIR = os.getenv("SOURCE_SCHEMA_DIR", "/app/source_schemas")

QUERY_CACHE_TTL_LIVE = int(os.getenv("AEGIS_QUERY_CACHE_TTL_LIVE", "4"))
QUERY_CACHE_TTL_SHORT = int(os.getenv("AEGIS_QUERY_CACHE_TTL_SHORT", "15"))
QUERY_CACHE_TTL_MEDIUM = int(os.getenv("AEGIS_QUERY_CACHE_TTL_MEDIUM", "60"))
QUERY_CACHE_TTL_STATIC = int(os.getenv("AEGIS_QUERY_CACHE_TTL_STATIC", "300"))

REFRESH_INTERVAL_SECONDS = [5, 10, 20, 30]
TIME_WINDOW_MINUTES = [15, 30, 60, 180, 360]
TABLE_ROW_LIMITS = [25, 50, 100, 200]

ALL_SOURCE_PROFILES = "All source profiles"
ALL_REGIONS = "All regions"
ALL_SERVERS = "All servers"

CHART_PALETTE = [
    "#56B4E9",  # blue
    "#E69F00",  # orange
    "#009E73",  # green
    "#D55E00",  # vermillion
    "#CC79A7",  # reddish purple
    "#0072B2",  # darker blue
    "#F0E442",  # yellow
]

@dataclass(frozen=True)
class DashboardFilters:
    selected_source_profile: str
    selected_region: str
    selected_server: str
    time_window_minutes: int
    max_table_rows: int

    @property
    def source_label(self) -> str:
        return self.selected_source_profile

    @property
    def time_filter(self) -> str:
        return f"window_start >= now() - INTERVAL {int(self.time_window_minutes)} MINUTE"

    @property
    def incident_time_filter(self) -> str:
        return f"detected_at >= now() - INTERVAL {int(self.time_window_minutes)} MINUTE"

    @property
    def quality_time_filter(self) -> str:
        return f"failed_at >= now() - INTERVAL {int(self.time_window_minutes)} MINUTE"

    @property
    def raw_event_time_filter(self) -> str:
        return f"event_time >= now() - INTERVAL {int(self.time_window_minutes)} MINUTE"
