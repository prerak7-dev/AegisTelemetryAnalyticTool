from __future__ import annotations

import base64
import html
import math
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

# Phase 13.10 uses a new key namespace so old experimental subnav CSS from
# previous phases cannot interfere with the layout.
NAV_BAR_KEY = "aegis_v2_nav_bar"
MAX_SUBNAV_ITEMS_PER_ROW = 6
MIN_SUBNAV_TAB_REM = 9.5


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
    return f"aegis_v2_nav_group_{group_key}"


def _subnav_container_key(group_key: str) -> str:
    return f"aegis_v2_subnav_{group_key}"


def _subnav_row_key(group_key: str, row_index: int) -> str:
    return f"aegis_v2_subnav_row_{group_key}_{row_index}"


def _subnav_button_key(workspace_key: str) -> str:
    return f"aegis_v2_nav_btn_{workspace_key}"


def _subnav_item_key(workspace_key: str, active: bool) -> str:
    state = "active" if active else "idle"
    return f"aegis_v2_nav_item_{workspace_key}_{state}"


def _label_units(label: str) -> int:
    return max(14, len(label) + 6)


def _group_weight(group) -> int:
    return _label_units(group.label)


def _workspace_weight(workspace_key: str) -> int:
    return _label_units(workspace_by_key(workspace_key).label)


def _subnav_estimated_units(group) -> int:
    return sum(_workspace_weight(workspace_key) for workspace_key in group.workspace_keys)


def _compact_subnav_width_rem(group) -> float:
    """Width for compact dropdowns based on the number and labels of options."""
    item_count = max(1, len(group.workspace_keys))
    widest_label = max(
        (len(workspace_by_key(workspace_key).label) for workspace_key in group.workspace_keys),
        default=len(group.label),
    )

    # Keep single-tab dropdowns compact, but still allow longer labels to breathe.
    if item_count == 1:
        return max(10.5, min(18.0, widest_label * 0.55 + 4.5))

    return max(12.0, min(42.0, item_count * max(9.25, min(13.0, widest_label * 0.42 + 6.5))))


def _is_viewport_safe_full_row_group(group, index: int, total_groups: int, previous_weight: int, total_weight: int) -> bool:
    """Return True when the dropdown should use the full nav-row width.

    This is registry-driven, not hardcoded to a group name. It handles future
    workspace additions/removals by looking at item count, estimated label width,
    and whether the dropdown would clip if opened from the group tab.
    """
    estimated_units = _subnav_estimated_units(group)
    would_clip_if_group_aligned = previous_weight + max(estimated_units, _group_weight(group)) > total_weight

    # Small groups should never claim the full nav-row width just because they
    # sit near the right edge. They stay compact and right-align to their main
    # tab when needed.
    if len(group.workspace_keys) <= 2:
        return False

    return (
        len(group.workspace_keys) > 4
        or estimated_units >= 70
        or would_clip_if_group_aligned
    )


def _subnav_rows(group, use_full_row: bool) -> list[tuple[str, ...]]:
    keys = tuple(group.workspace_keys)
    if not keys:
        return []

    # Compact groups and all groups up to the row limit remain horizontal in one row.
    if len(keys) <= MAX_SUBNAV_ITEMS_PER_ROW:
        return [keys]

    # For larger custom groups, create balanced horizontal rows. This is still
    # customizable because the rows are derived from count, not group names.
    row_count = math.ceil(len(keys) / MAX_SUBNAV_ITEMS_PER_ROW)
    items_per_row = math.ceil(len(keys) / row_count)
    return [keys[start : start + items_per_row] for start in range(0, len(keys), items_per_row)]


def _render_dynamic_nav_css() -> None:
    """Generate viewport-safe horizontal subnav CSS from the workspace registry."""
    group_weights = [_group_weight(group) for group in WORKSPACE_GROUPS]
    total_weight = max(1, sum(group_weights))
    previous_weight = 0
    rules: list[str] = []

    for index, (group, group_weight) in enumerate(zip(WORKSPACE_GROUPS, group_weights)):
        group_key = html.escape(group.key, quote=True)
        use_full_row = _is_viewport_safe_full_row_group(
            group,
            index,
            len(WORKSPACE_GROUPS),
            previous_weight,
            total_weight,
        )
        rows = _subnav_rows(group, use_full_row)
        row_count = max(1, len(rows))

        if use_full_row:
            left = f"calc(-{previous_weight / max(group_weight, 1):.8f} * 100%)"
            right = "auto"
            width = f"calc({total_weight / max(group_weight, 1):.8f} * 100%)"
        else:
            # Compact subnavs use dynamic width based on option count/labels.
            # If a compact dropdown is near the right edge, keep it compact but
            # right-align it to the main tab instead of expanding to full-row.
            estimated_rem = _compact_subnav_width_rem(group)
            compact_units = max(group_weight, estimated_rem / 0.72)
            would_clip_compact = previous_weight + compact_units > total_weight
            left = "auto" if would_clip_compact else "0"
            right = "0" if would_clip_compact else "auto"
            width = f"{estimated_rem:.2f}rem"

        max_height = f"{row_count * 3.15 + 0.35:.2f}rem"

        rules.append(
            f"""
            .st-key-aegis_v2_nav_group_{group_key} {{
              position: relative !important;
              overflow: visible !important;
            }}

            .st-key-aegis_v2_nav_group_{group_key} .st-key-aegis_v2_subnav_{group_key} {{
              position: absolute !important;
              top: calc(100% - 1px) !important;
              left: {left} !important;
              right: {right} !important;
              width: {width} !important;
              min-width: 0 !important;
              max-width: {width} !important;
              max-height: 0 !important;
              opacity: 0 !important;
              overflow: hidden !important;
              pointer-events: none !important;
              transform: translateY(-0.35rem) !important;
              z-index: 9500 !important;
            }}

            .st-key-aegis_v2_nav_group_{group_key}:hover .st-key-aegis_v2_subnav_{group_key},
            .st-key-aegis_v2_subnav_{group_key}:hover {{
              max-height: {max_height} !important;
              opacity: 1 !important;
              overflow: visible !important;
              pointer-events: auto !important;
              transform: translateY(0) !important;
            }}
            """
        )

        previous_weight += group_weight

    st.markdown("<style>" + "\n".join(rules) + "</style>", unsafe_allow_html=True)


def _render_subnav_button(workspace_key: str, active_workspace_key: str) -> None:
    workspace = workspace_by_key(workspace_key)
    is_active_workspace = workspace.key == active_workspace_key

    with st.container(key=_subnav_item_key(workspace.key, is_active_workspace)):
        st.button(
            workspace.label,
            key=_subnav_button_key(workspace.key),
            type="primary" if is_active_workspace else "secondary",
            use_container_width=True,
            on_click=_set_active_workspace,
            args=(workspace.key,),
        )


def render_workspace_navigation() -> Workspace:
    if ACTIVE_WORKSPACE_KEY not in st.session_state:
        st.session_state[ACTIVE_WORKSPACE_KEY] = DEFAULT_WORKSPACE_KEY

    active_workspace_key = _valid_workspace_key(st.session_state.get(ACTIVE_WORKSPACE_KEY))
    active_workspace = workspace_by_key(active_workspace_key)
    active_group = group_for_workspace_key(active_workspace.key)

    _render_dynamic_nav_css()

    with st.container(key=NAV_BAR_KEY):
        group_column_weights = [_group_weight(group) for group in WORKSPACE_GROUPS]
        columns = st.columns(group_column_weights, gap="small")

        for group_index, (column, group) in enumerate(zip(columns, WORKSPACE_GROUPS)):
            is_active_group = group.key == active_group.key
            active_class = " active" if is_active_group else ""

            with column:
                with st.container(key=_group_container_key(group.key)):
                    st.markdown(
                        f"<div class='aegis-v2-main-group-tab{active_class}'><span>{group.label}</span></div>",
                        unsafe_allow_html=True,
                    )

                    with st.container(key=_subnav_container_key(group.key)):
                        previous_weight = sum(_group_weight(g) for g in WORKSPACE_GROUPS[:group_index])
                        total_weight = sum(_group_weight(g) for g in WORKSPACE_GROUPS)
                        use_full_row = _is_viewport_safe_full_row_group(
                            group,
                            group_index,
                            len(WORKSPACE_GROUPS),
                            previous_weight,
                            total_weight,
                        )

                        for row_index, row_keys in enumerate(_subnav_rows(group, use_full_row)):
                            with st.container(key=_subnav_row_key(group.key, row_index)):
                                row_columns = st.columns([1] * len(row_keys), gap="small")
                                for subnav_column, workspace_key in zip(row_columns, row_keys):
                                    with subnav_column:
                                        _render_subnav_button(workspace_key, active_workspace_key)

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
