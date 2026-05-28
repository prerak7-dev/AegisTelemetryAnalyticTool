from __future__ import annotations

import base64
from pathlib import Path

import streamlit as st

from services.dashboard.workspaces import (
    WORKSPACE_GROUPS,
    Workspace,
    group_for_workspace_key,
    workspace_by_key,
)

DEFAULT_WORKSPACE_KEY = "command_center"
ACTIVE_WORKSPACE_KEY = "aegis_active_workspace_key"
NAV_BAR_KEY = "aegis_nav_bar"

def _asset_data_uri(path: Path, mime_type: str) -> str:
    if not path.exists():
        return ""
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"

def _separator_data_uri() -> str:
    return _asset_data_uri(Path(__file__).parent / "assets" / "breadcrumb_arrow.svg", "image/svg+xml")

def _valid_workspace_key(value: str | None) -> str:
    if not value:
        return DEFAULT_WORKSPACE_KEY
    return workspace_by_key(str(value)).key

def _set_active_workspace(workspace_key: str) -> None:
    st.session_state[ACTIVE_WORKSPACE_KEY] = _valid_workspace_key(workspace_key)

def _group_container_key(group_key: str) -> str:
    return f"aegis_nav_group_{group_key}"

def _subnav_container_key(group_key: str) -> str:
    return f"aegis_nav_subnav_{group_key}"

def _subnav_button_key(workspace_key: str) -> str:
    return f"aegis_nav_btn_{workspace_key}"

def _subnav_item_key(workspace_key: str, active: bool) -> str:
    state = "active" if active else "idle"
    return f"aegis_nav_item_{workspace_key}_{state}"

def render_workspace_navigation() -> Workspace:
    if ACTIVE_WORKSPACE_KEY not in st.session_state:
        st.session_state[ACTIVE_WORKSPACE_KEY] = DEFAULT_WORKSPACE_KEY

    active_workspace_key = _valid_workspace_key(st.session_state.get(ACTIVE_WORKSPACE_KEY))
    active_workspace = workspace_by_key(active_workspace_key)
    active_group = group_for_workspace_key(active_workspace.key)

    with st.container(key=NAV_BAR_KEY):
        group_column_weights = [
            max(14, len(group.label) + 6)
            for group in WORKSPACE_GROUPS
        ]
        columns = st.columns(group_column_weights, gap="small")

        for column, group in zip(columns, WORKSPACE_GROUPS):
            is_active_group = group.key == active_group.key
            active_class = " active" if is_active_group else ""

            with column:
                with st.container(key=_group_container_key(group.key)):
                    st.markdown(
                        f"<div class='aegis-main-group-tab{active_class}'><span>{group.label}</span></div>",
                        unsafe_allow_html=True,
                    )

                    with st.container(key=_subnav_container_key(group.key)):
                        subnav_column_weights = [
                            max(14, len(workspace_by_key(workspace_key).label) + 6)
                            for workspace_key in group.workspace_keys
                        ]
                        subnav_columns = st.columns(subnav_column_weights, gap="small")
                        for subnav_column, workspace_key in zip(subnav_columns, group.workspace_keys):
                            workspace = workspace_by_key(workspace_key)
                            is_active_workspace = workspace.key == active_workspace.key

                            with subnav_column:
                                with st.container(key=_subnav_item_key(workspace.key, is_active_workspace)):
                                    st.button(
                                        workspace.label,
                                        key=_subnav_button_key(workspace.key),
                                        type="primary" if is_active_workspace else "secondary",
                                        use_container_width=True,
                                        on_click=_set_active_workspace,
                                        args=(workspace.key,),
                                    )

    selected_workspace_key = _valid_workspace_key(st.session_state.get(ACTIVE_WORKSPACE_KEY))
    selected_workspace = workspace_by_key(selected_workspace_key)
    selected_group = group_for_workspace_key(selected_workspace.key)
    separator_uri = _separator_data_uri()

    if separator_uri:
        separator_html = f"<img class='workspace-title-separator-img' src='{separator_uri}' alt='' />"
    else:
        separator_html = "<span class='workspace-title-separator-fallback'>/</span>"

    st.markdown(
        f"<div class='workspace-title-region'>"
        f"<span class='workspace-title-group'>{selected_group.label}</span>"
        f"{separator_html}"
        f"<span class='workspace-title-current'>{selected_workspace.label}</span>"
        f"</div>",
        unsafe_allow_html=True,
    )

    return selected_workspace
