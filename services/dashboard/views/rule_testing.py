from __future__ import annotations

import pandas as pd
import streamlit as st

from services.dashboard.components import render_table
from services.dashboard.context import DashboardContext
from services.dashboard.rule_testing import (
    list_rule_profiles_for_testing,
    list_rule_test_samples_for_ui,
    preview_sample_for_ui,
    run_profile_tests_for_ui,
)

def render(context: DashboardContext) -> None:
    st.subheader("Rule Testing and Replay")
    st.caption("Preview recommendation rules against known sample telemetry windows before trusting them in live incident analysis.")

    profiles = list_rule_profiles_for_testing()
    if not profiles:
        st.warning("No recommendation rule profiles found.")
        return

    profile_name = st.selectbox("Rule profile", profiles, index=0)

    report = run_profile_tests_for_ui(profile_name)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Samples", report["sample_count"])
    c2.metric("Passed", report["passed"])
    c3.metric("Failed", report["failed"])
    c4.metric("Pass rate", f"{report['pass_rate'] * 100:.1f}%")

    result_rows = []
    for result in report["results"]:
        result_rows.append({
            "sample_id": result["sample_id"],
            "passed": result["passed"],
            "expected": ", ".join(result["expected_issue_ids"]),
            "top_issue": result["top_issue_id"],
            "actual_candidates": ", ".join(result["actual_issue_ids"][:5]),
            "missing_expected": ", ".join(result["missing_expected"]),
            "unexpected_top_issue": result["unexpected_top_issue"] or "",
        })

    st.subheader("Rule test report")
    if result_rows:
        render_table(pd.DataFrame(result_rows), height=360)
    else:
        st.info("No rule test samples found.")

    st.subheader("Single sample replay")
    samples = list_rule_test_samples_for_ui()
    if not samples:
        st.info("No sample files found under recommendation_rules/tests.")
        return

    sample_options = {row["sample_id"]: row for row in samples}
    selected_sample_id = st.selectbox("Sample", list(sample_options.keys()))
    selected_sample = sample_options[selected_sample_id]

    st.write(selected_sample["description"])
    preview = preview_sample_for_ui(selected_sample["path"], profile_name)

    expected = preview.get("expected_issue_ids", [])
    actual = [item.get("issue_type") for item in preview.get("issue_candidates", [])]
    st.write(f"**Expected issue IDs:** `{', '.join(expected)}`")
    st.write(f"**Actual issue candidates:** `{', '.join(actual[:8])}`")

    issues = preview.get("issue_candidates", [])
    if issues:
        issue_rows = []
        for issue in issues:
            issue_rows.append({
                "issue_type": issue.get("issue_type"),
                "title": issue.get("title"),
                "owner": issue.get("owner"),
                "score": issue.get("score"),
                "confidence": issue.get("confidence"),
                "recommended_action_1": (issue.get("recommended_actions") or [""])[0],
            })
        render_table(pd.DataFrame(issue_rows), height=360)

        top_issue = issues[0]
        with st.expander("Top issue detail", expanded=True):
            st.write(f"**Impact:** {top_issue.get('impact', '')}")
            st.write("**Evidence:**")
            for evidence in top_issue.get("evidence", []):
                st.write(f"- {evidence}")
            st.write("**Recommended actions:**")
            for action in top_issue.get("recommended_actions", []):
                st.write(f"- {action}")
            st.write("**Validation plan:**")
            for step in top_issue.get("validation_plan", []):
                st.write(f"- {step}")
            st.write("**Guardrail metrics:**")
            st.write(", ".join(top_issue.get("guardrail_metrics", [])))
    else:
        st.info("No issue candidates matched this sample.")

    with st.expander("Raw sample metrics"):
        st.json(preview.get("metrics", {}))
