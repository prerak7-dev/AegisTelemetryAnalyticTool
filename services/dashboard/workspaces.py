from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from services.dashboard.context import DashboardContext
from services.dashboard.views import (
    command_center,
    data_quality,
    incident_dossier,
    incident_timeline,
    scaling_readiness,
    selected_server,
    source_schemas,
    timeline_stages,
    recommendation_rules,
    rule_testing,
    query_performance,
    performance_config,
)

@dataclass(frozen=True)
class Workspace:
    """Dashboard workspace registry entry.

    To add a new workspace:
    1. Create `services/dashboard/views/<your_view>.py` with `render(context)`.
    2. Import it above.
    3. Add a `Workspace(...)` entry below.
    4. Add its key to a WorkspaceGroup.
    """
    key: str
    label: str
    renderer: Callable[[DashboardContext], None]

@dataclass(frozen=True)
class WorkspaceGroup:
    """Top-level navigation group for hover-expanded sub-navigation."""
    key: str
    label: str
    description: str
    workspace_keys: tuple[str, ...]

WORKSPACES: list[Workspace] = [
    Workspace("command_center", "Command Center", command_center.render),
    Workspace("selected_server", "Selected Server", selected_server.render),
    Workspace("scaling_readiness", "Scaling Readiness", scaling_readiness.render),
    Workspace("incident_dossier", "Incident Dossier", incident_dossier.render),
    Workspace("incident_timeline", "Incident Timeline", incident_timeline.render),
    Workspace("rule_testing", "Rule Testing", rule_testing.render),
    Workspace("recommendation_rules", "Recommendation Rules", recommendation_rules.render),
    Workspace("timeline_stages", "Timeline Stages", timeline_stages.render),
    Workspace("data_quality", "Data Quality", data_quality.render),
    Workspace("source_schemas", "Source Schemas", source_schemas.render),
    Workspace("query_performance", "Query Performance", query_performance.render),
    Workspace("performance_config", "Performance Config", performance_config.render),
]

WORKSPACE_GROUPS: list[WorkspaceGroup] = [
    WorkspaceGroup(
        key="operations",
        label="Operations",
        description="Fleet health, selected-server drilldown, and scaling readiness.",
        workspace_keys=("command_center", "selected_server", "scaling_readiness"),
    ),
    WorkspaceGroup(
        key="incidents",
        label="Incidents",
        description="Incident triage, evidence drilldown, and historical root-cause replay.",
        workspace_keys=("incident_dossier", "incident_timeline"),
    ),
    WorkspaceGroup(
        key="rules_replay",
        label="Rules & Replay",
        description="Rule testing, recommendation logic, and configurable timeline stages.",
        workspace_keys=("rule_testing", "recommendation_rules", "timeline_stages"),
    ),
    WorkspaceGroup(
        key="data_governance",
        label="Data & Schemas",
        description="Telemetry quality and source schema adaptability.",
        workspace_keys=("data_quality", "source_schemas", "query_performance", "performance_config"),
    ),
]

def workspace_by_key(key: str) -> Workspace:
    for workspace in WORKSPACES:
        if workspace.key == key:
            return workspace
    return WORKSPACES[0]

def workspace_by_label(label: str) -> Workspace:
    for workspace in WORKSPACES:
        if workspace.label == label:
            return workspace
    return WORKSPACES[0]

def group_by_key(key: str) -> WorkspaceGroup:
    for group in WORKSPACE_GROUPS:
        if group.key == key:
            return group
    return WORKSPACE_GROUPS[0]

def group_for_workspace_key(workspace_key: str) -> WorkspaceGroup:
    for group in WORKSPACE_GROUPS:
        if workspace_key in group.workspace_keys:
            return group
    return WORKSPACE_GROUPS[0]

def workspace_label_map() -> dict[str, str]:
    return {workspace.key: workspace.label for workspace in WORKSPACES}

def group_label_map() -> dict[str, str]:
    return {group.key: group.label for group in WORKSPACE_GROUPS}
