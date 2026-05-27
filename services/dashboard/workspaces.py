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
    recommendation_rules,
    rule_testing,
)

@dataclass(frozen=True)
class Workspace:
    """Dashboard workspace registry entry.

    To add a new workspace:
    1. Create `services/dashboard/views/<your_view>.py` with `render(context)`.
    2. Import it above.
    3. Add a `Workspace(...)` entry below.

    To remove a workspace, remove its entry from `WORKSPACES`.
    """
    key: str
    label: str
    renderer: Callable[[DashboardContext], None]

WORKSPACES: list[Workspace] = [
    Workspace("command_center", "Command Center", command_center.render),
    Workspace("selected_server", "Selected Server", selected_server.render),
    Workspace("incident_dossier", "Incident Dossier", incident_dossier.render),
    Workspace("incident_timeline", "Incident Timeline", incident_timeline.render),
    Workspace("data_quality", "Data Quality", data_quality.render),
    Workspace("scaling_readiness", "Scaling Readiness", scaling_readiness.render),
    Workspace("source_schemas", "Source Schemas", source_schemas.render),
    Workspace("recommendation_rules", "Recommendation Rules", recommendation_rules.render),
    Workspace("rule_testing", "Rule Testing", rule_testing.render),
]

def workspace_by_label(label: str) -> Workspace:
    for workspace in WORKSPACES:
        if workspace.label == label:
            return workspace
    return WORKSPACES[0]
