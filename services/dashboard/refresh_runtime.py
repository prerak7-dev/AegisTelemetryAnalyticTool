from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import Any

import pandas as pd
import streamlit as st

from services.dashboard.performance_config import cfg_get

ACTIVE_WORKSPACE_KEY = "aegis_active_workspace_key"
DEFAULT_WORKSPACE_KEY = "command_center"

REFRESH_HISTORY_KEY = "aegis_refresh_history"
LAST_REFRESH_TICK_KEY = "aegis_last_refresh_tick"
LAST_REFRESH_AT_KEY = "aegis_last_refresh_at"
MANUAL_REFRESH_REQUEST_KEY = "aegis_manual_refresh_requested_at"
MAX_REFRESH_HISTORY = 250

LIVE_MODES = {"live", "incident", "demo"}
STATIC_MODES = {"static", "manual", "disabled"}

@dataclass(frozen=True)
class RefreshPolicy:
    workspace_key: str
    mode: str
    auto_refresh: bool
    interval_multiplier: float
    min_interval_seconds: int
    max_interval_seconds: int
    render_kpi_strip: bool
    cache_policy_hint: str
    description: str

    @property
    def is_live(self) -> bool:
        return self.mode in LIVE_MODES and self.auto_refresh

    @property
    def is_static(self) -> bool:
        return self.mode in STATIC_MODES or not self.auto_refresh

def _safe_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except Exception:
        return default

def _safe_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except Exception:
        return default

def active_workspace_key(default: str = DEFAULT_WORKSPACE_KEY) -> str:
    return str(st.session_state.get(ACTIVE_WORKSPACE_KEY, default) or default)

def _default_policy_for(workspace_key: str) -> dict[str, Any]:
    defaults = dict(cfg_get("refresh_runtime.default_workspace_policy", {}) or {})
    by_mode = dict(cfg_get("refresh_runtime.mode_defaults", {}) or {})

    # Conservative fallback when config is missing.
    defaults = {
        "mode": defaults.get("mode", "live"),
        "auto_refresh": defaults.get("auto_refresh", True),
        "interval_multiplier": defaults.get("interval_multiplier", 1.0),
        "min_interval_seconds": defaults.get("min_interval_seconds", 5),
        "max_interval_seconds": defaults.get("max_interval_seconds", 60),
        "render_kpi_strip": defaults.get("render_kpi_strip", True),
        "cache_policy_hint": defaults.get("cache_policy_hint", "live"),
        "description": defaults.get("description", "Default live workspace refresh policy."),
    }

    mode_defaults = by_mode.get(str(defaults["mode"]), {})
    merged = {**defaults, **mode_defaults}
    return merged

def workspace_refresh_policy(workspace_key: str | None = None) -> RefreshPolicy:
    key = str(workspace_key or active_workspace_key())
    base = _default_policy_for(key)
    configured = dict(cfg_get(f"refresh_runtime.workspaces.{key}", {}) or {})
    policy = {**base, **configured}

    mode = str(policy.get("mode", "live")).lower()
    return RefreshPolicy(
        workspace_key=key,
        mode=mode,
        auto_refresh=bool(policy.get("auto_refresh", True)),
        interval_multiplier=max(0.1, _safe_float(policy.get("interval_multiplier", 1.0), 1.0)),
        min_interval_seconds=max(1, _safe_int(policy.get("min_interval_seconds", 5), 5)),
        max_interval_seconds=max(1, _safe_int(policy.get("max_interval_seconds", 60), 60)),
        render_kpi_strip=bool(policy.get("render_kpi_strip", mode not in {"static", "manual", "disabled"})),
        cache_policy_hint=str(policy.get("cache_policy_hint", "live")),
        description=str(policy.get("description", "")),
    )

def effective_refresh_interval_seconds(global_interval_seconds: int, workspace_key: str | None = None) -> int:
    policy = workspace_refresh_policy(workspace_key)
    raw = int(round(max(1, int(global_interval_seconds)) * policy.interval_multiplier))

    adaptive = dict(cfg_get("refresh_runtime.adaptive_intervals", {}) or {})
    if bool(adaptive.get("enabled", True)):
        # Small jitter prevents synchronized refresh spikes when several local
        # sessions are open. It is disabled for very short intervals.
        jitter = _safe_float(adaptive.get("jitter_ratio", 0.08), 0.08)
        if raw >= 5 and jitter > 0:
            jitter_amount = raw * random.uniform(-jitter, jitter)
            raw = int(round(raw + jitter_amount))

    return max(policy.min_interval_seconds, min(policy.max_interval_seconds, raw))

def auto_refresh_allowed(global_live_refresh_enabled: bool, workspace_key: str | None = None) -> bool:
    if not bool(global_live_refresh_enabled):
        return False
    return workspace_refresh_policy(workspace_key).is_live

def should_render_kpi_strip(workspace_key: str | None = None) -> bool:
    return workspace_refresh_policy(workspace_key).render_kpi_strip

def _history() -> list[dict[str, Any]]:
    return st.session_state.setdefault(REFRESH_HISTORY_KEY, [])

def record_refresh_event(
    *,
    workspace_key: str,
    trigger: str,
    interval_seconds: int | None = None,
    skipped: bool = False,
    reason: str = "",
    tick: int | None = None,
) -> None:
    try:
        history = _history()
        now = time.time()
        last_at = st.session_state.get(LAST_REFRESH_AT_KEY)
        elapsed = None if last_at is None else max(0.0, now - float(last_at))
        if not skipped:
            st.session_state[LAST_REFRESH_AT_KEY] = now

        policy = workspace_refresh_policy(workspace_key)
        history.append(
            {
                "recorded_at": pd.Timestamp.utcnow().isoformat(),
                "workspace_key": workspace_key,
                "mode": policy.mode,
                "trigger": trigger,
                "interval_seconds": int(interval_seconds or 0),
                "elapsed_since_last_seconds": round(elapsed, 2) if elapsed is not None else None,
                "skipped": bool(skipped),
                "reason": reason,
                "tick": int(tick) if tick is not None else None,
            }
        )
        if len(history) > MAX_REFRESH_HISTORY:
            del history[:-MAX_REFRESH_HISTORY]
    except Exception:
        return

def record_autorefresh_tick_if_new(
    *,
    tick: int | None,
    workspace_key: str,
    interval_seconds: int,
    enabled: bool,
    skipped_reason: str = "",
) -> None:
    if tick is None:
        return

    last_tick_key = f"{LAST_REFRESH_TICK_KEY}_{workspace_key}"
    last_tick = st.session_state.get(last_tick_key)
    if last_tick == tick:
        return

    st.session_state[last_tick_key] = tick
    record_refresh_event(
        workspace_key=workspace_key,
        trigger="auto" if enabled else "auto_skipped",
        interval_seconds=interval_seconds,
        skipped=not enabled,
        reason=skipped_reason,
        tick=int(tick),
    )

def record_manual_refresh(workspace_key: str) -> None:
    st.session_state[MANUAL_REFRESH_REQUEST_KEY] = time.time()
    record_refresh_event(workspace_key=workspace_key, trigger="manual", interval_seconds=0)

def get_refresh_history() -> pd.DataFrame:
    history = st.session_state.get(REFRESH_HISTORY_KEY, [])
    if not history:
        return pd.DataFrame(
            columns=[
                "recorded_at",
                "workspace_key",
                "mode",
                "trigger",
                "interval_seconds",
                "elapsed_since_last_seconds",
                "skipped",
                "reason",
                "tick",
            ]
        )
    return pd.DataFrame(history)

def clear_refresh_history() -> None:
    st.session_state[REFRESH_HISTORY_KEY] = []

def refresh_status_summary(workspace_key: str | None = None) -> dict[str, Any]:
    key = str(workspace_key or active_workspace_key())
    policy = workspace_refresh_policy(key)
    history = get_refresh_history()
    recent = history.tail(25) if not history.empty else history

    return {
        "workspace_key": key,
        "mode": policy.mode,
        "auto_refresh": policy.auto_refresh,
        "render_kpi_strip": policy.render_kpi_strip,
        "recent_refreshes": int(len(recent)),
        "recent_skipped": int(recent["skipped"].sum()) if not recent.empty and "skipped" in recent.columns else 0,
        "last_trigger": str(recent.iloc[-1].get("trigger", "—")) if not recent.empty else "—",
        "last_recorded_at": str(recent.iloc[-1].get("recorded_at", "—")) if not recent.empty else "—",
    }
