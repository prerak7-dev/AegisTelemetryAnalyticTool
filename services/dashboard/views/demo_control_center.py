from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

from services.dashboard.components import render_paper_metric, render_table
from services.dashboard.context import DashboardContext
from services.dashboard.demo_control_store import (
    active_process_records,
    build_command,
    build_host_command,
    can_launch_processes,
    cleanup_finished_processes,
    launch_command,
    load_history_records,
    load_scenario_library,
    shell_command,
    stop_all_processes,
    stop_process,
)
from services.dashboard.performance_config import demo_control_cfg
from services.dashboard.query import clear_query_cache, get_client, query_df_named, quote_sql

ALL_CATEGORIES = "All categories"

def _scenario_label(scenario: dict) -> str:
    return f"{scenario.get('title', scenario.get('id', 'unknown'))} · {scenario.get('category', 'uncategorized')}"

def _scenario_dataframe(scenarios: list[dict]) -> pd.DataFrame:
    return pd.DataFrame([
        {
            "id": scenario.get("id", ""),
            "title": scenario.get("title", ""),
            "category": scenario.get("category", ""),
            "recommended_workspace": scenario.get("recommended_workspace", ""),
            "duration_sec": scenario.get("default_duration_sec", ""),
            "events_per_second": scenario.get("default_events_per_second", ""),
            "commands": len(scenario.get("commands", [])),
            "description": scenario.get("description", ""),
        }
        for scenario in scenarios
    ])

def _command_arg_values(scenario: dict, flag: str) -> list[str]:
    values: list[str] = []
    for command in scenario.get("commands", []):
        args = [str(arg) for arg in command.get("args", [])]
        for index, arg in enumerate(args):
            if arg == flag and index + 1 < len(args):
                values.append(args[index + 1])
    return list(dict.fromkeys(values))

def _sql_in(values: list[str]) -> str:
    clean = [str(value) for value in values if str(value)]
    if not clean:
        return "('')"
    return "(" + ", ".join(quote_sql(value) for value in clean) + ")"

def _age_seconds(value) -> float | None:
    try:
        if pd.isna(value):
            return None
        ts = pd.Timestamp(value)
        if ts.tzinfo is None:
            ts = ts.tz_localize("UTC")
        now = pd.Timestamp.utcnow()
        if now.tzinfo is None:
            now = now.tz_localize("UTC")
        return max(0.0, (now - ts.tz_convert("UTC")).total_seconds())
    except Exception:
        return None

def _format_age(seconds: float | None) -> str:
    if seconds is None:
        return "—"
    if seconds < 60:
        return f"{seconds:.0f}s ago"
    return f"{seconds / 60:.1f}m ago"

def _bounded_int_from_text(value: object, default: int, minimum: int, maximum: int) -> int:
    try:
        parsed = int(str(value).strip())
    except Exception:
        return default
    return max(minimum, min(maximum, parsed))

def _set_stepper_value(
    state_key: str,
    input_key: str,
    value: int,
    minimum: int,
    maximum: int,
) -> None:
    bounded = str(max(minimum, min(maximum, int(value))))
    st.session_state[state_key] = bounded
    st.session_state[input_key] = bounded

def _stepper_delta(
    state_key: str,
    input_key: str,
    delta: int,
    default: int,
    minimum: int,
    maximum: int,
) -> None:
    current = _bounded_int_from_text(st.session_state.get(input_key, st.session_state.get(state_key, default)), default, minimum, maximum)
    _set_stepper_value(state_key, input_key, current + int(delta), minimum, maximum)

def _render_bounded_stepper(
    *,
    label: str,
    state_key: str,
    selected_scenario_id: str,
    default: int,
    minimum: int,
    maximum: int,
    step: int,
) -> int:
    """Render a contained numeric control with visible -/+ buttons.

    Streamlit does not allow assigning to the same session_state key after a
    widget with that key has been instantiated. To avoid that, this control uses
    a widget key for the text input and a separate canonical value key for the
    validated integer used by scenario command generation.
    """
    input_key = f"{state_key}_input"
    scenario_state_key = f"{state_key}_scenario_id"
    if (
        state_key not in st.session_state
        or input_key not in st.session_state
        or st.session_state.get(scenario_state_key) != selected_scenario_id
    ):
        bounded_default = str(max(minimum, min(maximum, int(default))))
        st.session_state[state_key] = bounded_default
        st.session_state[input_key] = bounded_default
        st.session_state[scenario_state_key] = selected_scenario_id

    text_col, minus_col, plus_col = st.columns([1, 0.085, 0.085], gap="small")
    with text_col:
        text_value = st.text_input(label, key=input_key)
    with minus_col:
        st.button(
            "−",
            key=f"{state_key}_minus",
            use_container_width=True,
            on_click=_stepper_delta,
            args=(state_key, input_key, -int(step), default, minimum, maximum),
        )
    with plus_col:
        st.button(
            "＋",
            key=f"{state_key}_plus",
            use_container_width=True,
            on_click=_stepper_delta,
            args=(state_key, input_key, int(step), default, minimum, maximum),
        )

    value = _bounded_int_from_text(text_value, default, minimum, maximum)
    st.session_state[state_key] = str(value)
    return value

def _demo_feedback_snapshot(context: DashboardContext, scenario: dict) -> dict:
    """Return lightweight pipeline status for the selected demo scenario.

    This intentionally checks raw_events separately from aggregate windows so
    the user sees progress before the 30s aggregate window closes.
    """
    window_minutes = int(demo_control_cfg("feedback_window_minutes", 10) or 10)
    scenario_names = _command_arg_values(scenario, "--scenario")
    build_versions = _command_arg_values(scenario, "--build-version")
    experiment_ids = _command_arg_values(scenario, "--experiment-id")

    raw_where = [
        f"event_time >= now() - INTERVAL {window_minutes} MINUTE",
        context.active_filter,
    ]
    if scenario_names:
        raw_where.append(f"JSONExtractString(raw_json, 'scenario') IN {_sql_in(scenario_names)}")
    if build_versions:
        raw_where.append(f"build_version IN {_sql_in(build_versions)}")
    if experiment_ids:
        raw_where.append(f"JSONExtractString(raw_json, 'experiment_id') IN {_sql_in(experiment_ids)}")

    agg_where = [
        f"window_start >= now() - INTERVAL {window_minutes} MINUTE",
        context.active_filter,
    ]
    if build_versions:
        agg_where.append(f"build_version IN {_sql_in(build_versions)}")

    incident_where = [
        f"detected_at >= now() - INTERVAL {window_minutes} MINUTE",
        context.active_filter,
    ]
    if build_versions:
        incident_where.append(f"build_version IN {_sql_in(build_versions)}")

    raw = query_df_named(
        "demo_control_raw_ingestion_feedback",
        f"""
        SELECT
          count() AS raw_events,
          max(event_time) AS latest_raw_event,
          countDistinct(server_id) AS raw_servers,
          countDistinct(map_id) AS raw_maps,
          countDistinct(zone_id) AS raw_zones
        FROM raw_events
        WHERE {' AND '.join(raw_where)}
        """,
        cache_policy="live",
    )

    agg = query_df_named(
        "demo_control_aggregate_feedback",
        f"""
        SELECT
          count() AS aggregate_windows,
          sum(events) AS aggregate_events,
          max(window_start) AS latest_aggregate_window,
          countDistinct(server_id) AS aggregate_servers,
          max(hot_zone_risk_score) AS max_risk
        FROM agg_zone_30s
        WHERE {' AND '.join(agg_where)}
        """,
        cache_policy="live",
    )

    incidents = query_df_named(
        "demo_control_incident_feedback",
        f"""
        SELECT
          count() AS incidents,
          max(detected_at) AS latest_incident,
          countIf(severity = 'critical') AS critical_incidents,
          countIf(severity = 'warning') AS warning_incidents
        FROM incidents
        WHERE {' AND '.join(incident_where)}
        """,
        cache_policy="live",
    )

    raw_row = raw.iloc[0].to_dict() if not raw.empty else {}
    agg_row = agg.iloc[0].to_dict() if not agg.empty else {}
    incident_row = incidents.iloc[0].to_dict() if not incidents.empty else {}

    raw_events = int(raw_row.get("raw_events", 0) or 0)
    aggregate_windows = int(agg_row.get("aggregate_windows", 0) or 0)
    incident_count = int(incident_row.get("incidents", 0) or 0)

    if raw_events <= 0:
        stage = "Starting generator / waiting for first processor flush"
        guidance = f"Raw events usually appear after the processor flush interval, about {demo_control_cfg('processor_warmup_seconds', 3)} seconds."
    elif aggregate_windows <= 0:
        stage = "Raw events visible / waiting for aggregate window"
        guidance = (
            f"Aggregates appear after the current {demo_control_cfg('aggregate_window_seconds', 30)}s window closes "
            f"plus roughly {demo_control_cfg('aggregate_grace_seconds', 8)}s of grace. Raw ingestion is already working."
        )
    else:
        stage = "Aggregates available / workspaces ready"
        guidance = "Command Center, Incident Dossier, Baseline Intelligence, and other workspaces can now read aggregated data."

    return {
        "stage": stage,
        "guidance": guidance,
        "raw_events": raw_events,
        "latest_raw_event": raw_row.get("latest_raw_event"),
        "raw_servers": int(raw_row.get("raw_servers", 0) or 0),
        "aggregate_windows": aggregate_windows,
        "aggregate_events": int(agg_row.get("aggregate_events", 0) or 0),
        "latest_aggregate_window": agg_row.get("latest_aggregate_window"),
        "aggregate_servers": int(agg_row.get("aggregate_servers", 0) or 0),
        "max_risk": float(agg_row.get("max_risk", 0) or 0),
        "incidents": incident_count,
        "critical_incidents": int(incident_row.get("critical_incidents", 0) or 0),
        "warning_incidents": int(incident_row.get("warning_incidents", 0) or 0),
        "latest_incident": incident_row.get("latest_incident"),
        "scenario_names": scenario_names,
        "build_versions": build_versions,
        "experiment_ids": experiment_ids,
    }

def _render_demo_feedback(context: DashboardContext, scenario: dict, running: list[dict]) -> None:
    if not bool(demo_control_cfg("show_pipeline_feedback", True)):
        return

    snapshot = _demo_feedback_snapshot(context, scenario)

    st.markdown('<div class="pressure-section-title">Live Demo Feedback</div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="demo-feedback-panel">
          <div class="demo-feedback-stage">{snapshot['stage']}</div>
          <div class="demo-feedback-copy">{snapshot['guidance']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        render_paper_metric("Generator state", "Running" if running else "Idle")
    with k2:
        render_paper_metric("Raw events", str(snapshot["raw_events"]))
    with k3:
        render_paper_metric("Aggregate windows", str(snapshot["aggregate_windows"]))
    with k4:
        render_paper_metric("Incidents", str(snapshot["incidents"]))
    with k5:
        render_paper_metric("Max risk", f"{snapshot['max_risk']:.1f}")

    detail_rows = pd.DataFrame([
        {"signal": "Latest raw event", "value": _format_age(_age_seconds(snapshot["latest_raw_event"]))},
        {"signal": "Latest aggregate window", "value": _format_age(_age_seconds(snapshot["latest_aggregate_window"]))},
        {"signal": "Latest incident", "value": _format_age(_age_seconds(snapshot["latest_incident"]))},
        {"signal": "Scenario filter", "value": ", ".join(snapshot["scenario_names"]) or "—"},
        {"signal": "Build filter", "value": ", ".join(snapshot["build_versions"]) or "—"},
        {"signal": "Experiment filter", "value": ", ".join(snapshot["experiment_ids"]) or "—"},
    ])
    render_table(detail_rows, height=240)


def _safe_table_name(value: str) -> str:
    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_")
    return "".join(ch for ch in str(value) if ch in allowed)

def _reset_demo_data() -> tuple[bool, str]:
    if not bool(demo_control_cfg("enable_data_reset", True)):
        return False, "Data reset is disabled by configuration."

    tables = [_safe_table_name(table) for table in list(demo_control_cfg("reset_tables", []))]
    tables = [table for table in tables if table]

    if not tables:
        return False, "No reset tables are configured."

    client = get_client()
    errors = []
    for table in tables:
        try:
            client.command(f"TRUNCATE TABLE IF EXISTS {table}")
        except Exception as exc:
            errors.append(f"{table}: {exc}")

    clear_query_cache()

    if errors:
        return False, "; ".join(errors)
    return True, f"Reset tables: {', '.join(tables)}"

def _demo_report(scenario: dict, commands: list[list[str]], history: list[dict], host_commands: list[list[str]] | None = None) -> str:
    host_commands = host_commands or []

    lines = [
        "# AegisTelemetry Demo Runbook",
        "",
        f"**Scenario:** {scenario.get('title', scenario.get('id', 'unknown'))}",
        f"**Category:** {scenario.get('category', 'uncategorized')}",
        f"**Recommended workspace:** {scenario.get('recommended_workspace', 'Command Center')}",
        "",
        "## Why this scenario matters",
        scenario.get("description", ""),
        "",
        "## Commands",
    ]

    for command in commands:
        lines += ["", "### Container command", "```bash", shell_command(command), "```"]

    if host_commands:
        lines += ["", "## Host Commands"]
        for command in host_commands:
            lines += ["", "```bash", shell_command(command), "```"]

    talk_track = scenario.get("talk_track", [])
    lines += ["", "## Talk Track"]
    if talk_track:
        for item in talk_track:
            lines.append(f"- {item}")
    else:
        lines.append("- Open the recommended workspace and walk through the generated telemetry evidence.")

    lines += ["", "## Recent Demo Launch History"]
    if history:
        for record in history[-10:]:
            lines.append(f"- {record.get('created_at', '')} · {record.get('scenario_id', '')} · PID {record.get('pid', '')}")
    else:
        lines.append("_No launch history recorded yet._")

    return "\n".join(lines)

def render(context: DashboardContext) -> None:
    cleanup_finished_processes()

    library = load_scenario_library()
    scenarios = list(library.get("scenarios", []))

    st.subheader("Demo Control Center")
    st.caption(
        "Portfolio/demo mode for launching or copying scenario commands without leaving the dashboard."
    )

    if not scenarios:
        st.warning("No demo scenarios are configured. Check config/demo_scenarios.json.")
        return

    launch_enabled = can_launch_processes()
    reset_enabled = bool(demo_control_cfg("enable_data_reset", True))

    running = active_process_records()
    history = load_history_records(limit=50)

    # When a demo is running, refresh this workspace frequently so the user sees
    # process state, raw ingestion, aggregate windows, and incidents arrive.
    if running:
        st_autorefresh(
            interval=int(demo_control_cfg("status_refresh_seconds", 2) or 2) * 1000,
            key="aegis_demo_control_status_refresh",
        )

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_paper_metric("Configured scenarios", str(len(scenarios)))
    with k2:
        render_paper_metric("Active generators", str(len([p for p in running if p["status"] == "running"])))
    with k3:
        render_paper_metric("Launch mode", "Enabled" if launch_enabled else "Commands only")
    with k4:
        render_paper_metric("Reset data", "Enabled" if reset_enabled else "Disabled")

    st.markdown(
        """
        <div class="pressure-callout">
          <b>Demo workflow:</b> choose a scenario, review generated commands, start the scenario when launch is enabled,
          then open the recommended workspace. If launch is disabled, copy the generated commands and run them manually.
        </div>
        """,
        unsafe_allow_html=True,
    )

    categories = [ALL_CATEGORIES] + sorted({str(s.get("category", "uncategorized")) for s in scenarios})
    selected_category = st.selectbox("Scenario category", categories, index=0, key="aegis_demo_category_filter")

    visible_scenarios = scenarios
    if selected_category != ALL_CATEGORIES:
        visible_scenarios = [s for s in scenarios if str(s.get("category", "uncategorized")) == selected_category]

    scenario_options = [_scenario_label(s) for s in visible_scenarios]
    selected_label = st.selectbox(
        "Scenario",
        scenario_options,
        index=0,
        key="aegis_demo_selected_scenario",
    )
    selected_scenario = visible_scenarios[scenario_options.index(selected_label)]

    default_duration = int(selected_scenario.get("default_duration_sec", 180) or 180)
    default_eps = int(selected_scenario.get("default_events_per_second", 120) or 120)

    controls_left, controls_right = st.columns(2, gap="medium")
    selected_scenario_id = str(selected_scenario.get("id", "scenario"))
    with controls_left:
        with st.container(key="aegis_demo_duration_input_wrap"):
            duration_sec = _render_bounded_stepper(
                label="Duration seconds",
                state_key="aegis_demo_duration_sec_text",
                selected_scenario_id=selected_scenario_id,
                default=default_duration,
                minimum=15,
                maximum=3600,
                step=15,
            )
    with controls_right:
        with st.container(key="aegis_demo_eps_input_wrap"):
            events_per_second = _render_bounded_stepper(
                label="Events per second",
                state_key="aegis_demo_events_per_second_text",
                selected_scenario_id=selected_scenario_id,
                default=default_eps,
                minimum=1,
                maximum=5000,
                step=10,
            )

    commands = [
        build_command(
            command.get("args", []),
            duration_sec=int(duration_sec),
            events_per_second=int(events_per_second),
        )
        for command in selected_scenario.get("commands", [])
    ]
    host_commands = [
        build_host_command(
            command.get("args", []),
            duration_sec=int(duration_sec),
            events_per_second=int(events_per_second),
        )
        for command in selected_scenario.get("commands", [])
    ]

    st.markdown('<div class="pressure-section-title">Scenario Details</div>', unsafe_allow_html=True)
    detail_left, detail_right = st.columns([1.0, 1.0])
    with detail_left:
        st.write(f"**Scenario ID:** `{selected_scenario.get('id', '')}`")
        st.write(f"**Category:** `{selected_scenario.get('category', '')}`")
        st.write(f"**Recommended workspace:** `{selected_scenario.get('recommended_workspace', '')}`")
        st.write(selected_scenario.get("description", ""))
    with detail_right:
        talk_track = selected_scenario.get("talk_track", [])
        st.write("**Demo talk track:**")
        for item in talk_track:
            st.write(f"- {item}")

    st.markdown('<div class="pressure-section-title">Generated Commands</div>', unsafe_allow_html=True)
    for command_def, command, host_command in zip(selected_scenario.get("commands", []), commands, host_commands):
        st.caption(command_def.get("label", "Generate telemetry"))
        st.write("Container command used by the dashboard launcher:")
        st.code(shell_command(command), language="bash")
        st.write("Host command you can copy from the project root:")
        st.code(shell_command(host_command), language="bash")

    st.markdown('<div class="pressure-section-title">Scenario Controls</div>', unsafe_allow_html=True)
    action_cols = st.columns([1, 1, 1.15])
    with action_cols[0]:
        with st.container(key="aegis_demo_start_action_wrap"):
            start_clicked = st.button(
                "Start scenario",
                type="primary",
                disabled=not launch_enabled,
                key="aegis_demo_start_scenario",
                use_container_width=True,
            )
    with action_cols[1]:
        with st.container(key="aegis_demo_stop_action_wrap"):
            stop_clicked = st.button(
                "Stop all generators",
                key="aegis_demo_stop_all",
                disabled=not bool(running),
                use_container_width=True,
            )
    with action_cols[2]:
        with st.container(key="aegis_demo_reset_action_wrap"):
            reset_checked = st.checkbox(
                "Confirm reset of demo telemetry tables",
                value=False,
                key="aegis_demo_confirm_reset",
                disabled=not reset_enabled,
            )
            reset_clicked = st.button(
                "Reset demo data",
                disabled=not reset_enabled or not reset_checked,
                key="aegis_demo_reset_data",
                use_container_width=True,
            )
            st.caption("Requires confirmation. Clears only the configured demo tables.")

    if start_clicked:
        messages = []
        for command_def, command in zip(selected_scenario.get("commands", []), commands):
            ok, message = launch_command(
                scenario_id=str(selected_scenario.get("id", "scenario")),
                command_label=str(command_def.get("label", "command")),
                command=command,
            )
            messages.append((ok, message))

        if all(ok for ok, _ in messages):
            st.success(
                "Scenario generator(s) started. Raw events should appear first, then aggregate windows after the "
                "current window closes. The Live Demo Feedback panel will refresh automatically while generators run."
            )
        else:
            for ok, message in messages:
                if ok:
                    st.success(f"Started: {message}")
                else:
                    st.error(f"Could not start: {message}")
        st.rerun()

    if stop_clicked:
        stopped = stop_all_processes()
        st.success(f"Stopped {stopped} generator process(es).")
        st.rerun()

    if reset_clicked:
        ok, message = _reset_demo_data()
        if ok:
            st.success(message)
        else:
            st.error(message)
        st.rerun()

    # Re-read process state after any start/stop/reset branch and show pipeline
    # feedback immediately. Raw events should show before aggregates are ready,
    # which removes the "silent 10-15 second wait" feeling.
    running = active_process_records()
    _render_demo_feedback(context, selected_scenario, running)

    st.markdown('<div class="pressure-section-title">Active Scenario Processes</div>', unsafe_allow_html=True)
    running = active_process_records()
    if running:
        render_table(pd.DataFrame(running), height=220)
        process_keys = [record["process_key"] for record in running]
        selected_process = st.selectbox("Stop individual process", process_keys, key="aegis_demo_stop_process_select")
        if st.button("Stop selected process", key="aegis_demo_stop_selected"):
            if stop_process(selected_process):
                st.success("Process stopped.")
                st.rerun()
            else:
                st.warning("Process was not found.")
    else:
        st.info("No active scenario generators.")

    st.markdown('<div class="pressure-section-title">Scenario Library</div>', unsafe_allow_html=True)
    render_table(_scenario_dataframe(scenarios), height=360)

    report = _demo_report(selected_scenario, commands, history, host_commands)
    st.download_button(
        "Download demo runbook",
        data=report,
        file_name=f"demo_runbook_{selected_scenario.get('id', 'scenario')}.md",
        mime="text/markdown",
    )

    with st.expander("Recent demo launch history", expanded=False):
        if history:
            render_table(pd.DataFrame(history), height=300)
        else:
            st.info("No launch history recorded yet.")

    with st.expander("Demo Control configuration", expanded=False):
        st.json({
            "scenario_library_path": demo_control_cfg("scenario_library_path", ""),
            "allow_subprocess_launch": demo_control_cfg("allow_subprocess_launch", True),
            "simulator_script_path": demo_control_cfg("simulator_script_path", ""),
            "collector_url": demo_control_cfg("collector_url", ""),
            "default_batch_size": demo_control_cfg("default_batch_size", 250),
            "max_parallel_scenario_processes": demo_control_cfg("max_parallel_scenario_processes", 4),
            "enable_data_reset": demo_control_cfg("enable_data_reset", True),
            "reset_tables": demo_control_cfg("reset_tables", []),
            "scenario_history_path": demo_control_cfg("scenario_history_path", ""),
        })
