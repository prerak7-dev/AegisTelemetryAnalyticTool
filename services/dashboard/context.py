from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from services.dashboard.config import DashboardFilters

@dataclass(frozen=True)
class DashboardContext:
    """Shared state passed to every workspace renderer.

    Workspace files should depend on this context rather than reaching back
    into app.py globals. This makes adding/removing workspaces easier.
    """
    filters: DashboardFilters
    active_filter: str
    source_filter: str
    region_filter: str
    server_filter: str
    server_inventory: pd.DataFrame
    visible_inventory: pd.DataFrame
    selected_server_display: str
