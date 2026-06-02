from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd
import streamlit as st

from services.dashboard.components import render_paper_metric, render_table
from services.dashboard.context import DashboardContext
from services.dashboard.performance_config import documentation_cfg

DOC_ACTIVE_SECTION_KEY = "aegis_documentation_active_section"
DOC_ACTIVE_PAGE_KEY = "aegis_documentation_active_page"

def _candidate_path(configured_path: str, fallback_relative: str) -> Path:
    candidates = [
        Path(str(configured_path)),
        Path(fallback_relative),
        Path.cwd() / fallback_relative,
        Path(__file__).resolve().parents[3] / fallback_relative,
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]

def _nav_path() -> Path:
    return _candidate_path(
        str(documentation_cfg("navigation_path", "/app/config/documentation_navigation.json")),
        "config/documentation_navigation.json",
    )

def _docs_root() -> Path:
    return _candidate_path(
        str(documentation_cfg("docs_root", "/app/docs/toolkit")),
        "docs/toolkit",
    )

def _load_registry() -> dict:
    path = _nav_path()
    fallback = {"title": "Documentation", "sections": []}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback

    if not isinstance(payload, dict):
        return fallback
    payload.setdefault("sections", [])
    return payload

def _all_pages(registry: dict) -> list[dict]:
    rows: list[dict] = []
    for section in registry.get("sections", []):
        for page in section.get("pages", []):
            rows.append({
                "section_id": section.get("id", ""),
                "section_title": section.get("title", ""),
                "section_description": section.get("description", ""),
                "page_id": page.get("id", ""),
                "page_title": page.get("title", ""),
                "file": page.get("file", ""),
                "audience": page.get("audience", ""),
            })
    return rows

def _read_doc(file_name: str) -> str:
    safe = Path(file_name)
    if safe.is_absolute() or ".." in safe.parts:
        return "# Invalid documentation path\n\nThe configured page path is not allowed."

    path = _docs_root() / safe
    if not path.exists():
        return f"# Missing documentation page\n\nExpected file:\n\n```text\n{path}\n```"

    return path.read_text(encoding="utf-8")

def _extract_headings(markdown: str) -> pd.DataFrame:
    rows = []
    for line in markdown.splitlines():
        match = re.match(r"^(#{1,4})\s+(.+)$", line.strip())
        if not match:
            continue
        level = len(match.group(1))
        title = match.group(2).strip()
        rows.append({"level": level, "heading": title})
    return pd.DataFrame(rows)

def _search_pages(pages: list[dict], query: str, max_results: int) -> pd.DataFrame:
    query = (query or "").strip().lower()
    if not query:
        return pd.DataFrame()

    matches = []
    for page in pages:
        markdown = _read_doc(str(page.get("file", "")))
        haystack = " ".join([
            str(page.get("section_title", "")),
            str(page.get("page_title", "")),
            str(page.get("audience", "")),
            markdown,
        ]).lower()
        if query in haystack:
            first_index = haystack.find(query)
            snippet_start = max(0, first_index - 120)
            snippet_end = min(len(haystack), first_index + 220)
            matches.append({
                "section": page.get("section_title", ""),
                "page": page.get("page_title", ""),
                "audience": page.get("audience", ""),
                "file": page.get("file", ""),
                "snippet": haystack[snippet_start:snippet_end].replace("\n", " "),
            })

    return pd.DataFrame(matches[:max_results])

def _section_by_id(registry: dict, section_id: str) -> dict:
    for section in registry.get("sections", []):
        if section.get("id") == section_id:
            return section
    sections = registry.get("sections", [])
    return sections[0] if sections else {"id": "", "title": "", "pages": []}

def _page_by_id(section: dict, page_id: str) -> dict:
    for page in section.get("pages", []):
        if page.get("id") == page_id:
            return page
    pages = section.get("pages", [])
    return pages[0] if pages else {"id": "", "title": "", "file": ""}


def _default_selection(registry: dict) -> tuple[str, str]:
    default_section_id = str(registry.get("default_section", ""))
    default_page_id = str(registry.get("default_page", ""))

    sections = registry.get("sections", [])
    if not sections:
        return "", ""

    section = _section_by_id(registry, default_section_id)
    if not section.get("id"):
        section = sections[0]

    page = _page_by_id(section, default_page_id)
    if not page.get("id") and section.get("pages"):
        page = section["pages"][0]

    return str(section.get("id", "")), str(page.get("id", ""))

def _selection_from_state(registry: dict) -> tuple[dict, dict]:
    default_section_id, default_page_id = _default_selection(registry)

    section_id = str(st.session_state.get(DOC_ACTIVE_SECTION_KEY, default_section_id))
    selected_section = _section_by_id(registry, section_id)
    if not selected_section.get("id"):
        selected_section = _section_by_id(registry, default_section_id)
        section_id = str(selected_section.get("id", ""))

    page_id = str(st.session_state.get(DOC_ACTIVE_PAGE_KEY, default_page_id))
    selected_page = _page_by_id(selected_section, page_id)
    if not selected_page.get("id"):
        selected_page = _page_by_id(selected_section, str(selected_section.get("pages", [{}])[0].get("id", "")))

    st.session_state[DOC_ACTIVE_SECTION_KEY] = str(selected_section.get("id", ""))
    st.session_state[DOC_ACTIVE_PAGE_KEY] = str(selected_page.get("id", ""))

    return selected_section, selected_page

def _set_documentation_page(section_id: str, page_id: str) -> None:
    st.session_state[DOC_ACTIVE_SECTION_KEY] = str(section_id)
    st.session_state[DOC_ACTIVE_PAGE_KEY] = str(page_id)

def _render_documentation_side_nav(registry: dict, selected_section: dict, selected_page: dict) -> None:
    st.markdown("### Documentation")
    st.caption("Browse user and developer guides.")

    for section in registry.get("sections", []):
        section_id = str(section.get("id", ""))
        section_title = str(section.get("title", section_id or "Section"))
        section_active = section_id == selected_section.get("id")

        with st.expander(section_title, expanded=section_active):
            description = str(section.get("description", ""))
            if description:
                st.markdown(
                    f"<div class='documentation-nav-section-description'>{description}</div>",
                    unsafe_allow_html=True,
                )

            pages = section.get("pages", [])
            if not pages:
                st.caption("No pages configured.")
                continue

            for page in pages:
                page_id = str(page.get("id", ""))
                is_active = section_active and page_id == selected_page.get("id")
                item_key = f"aegis_docs_nav_item_{section_id}_{page_id}_{'active' if is_active else 'idle'}"

                with st.container(key=item_key):
                    st.button(
                        str(page.get("title", page_id or "Page")),
                        key=f"aegis_docs_nav_btn_{section_id}_{page_id}",
                        type="primary" if is_active else "secondary",
                        use_container_width=True,
                        on_click=_set_documentation_page,
                        args=(section_id, page_id),
                    )


def render(context: DashboardContext) -> None:
    registry = _load_registry()
    docs_root = _docs_root()
    pages = _all_pages(registry)

    st.subheader(registry.get("title", "Documentation"))
    st.caption(registry.get("description", "Professional documentation for the toolkit."))

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_paper_metric("Sections", str(len(registry.get("sections", []))))
    with k2:
        render_paper_metric("Pages", str(len(pages)))
    with k3:
        render_paper_metric("Docs root", "Available" if docs_root.exists() else "Missing")
    with k4:
        render_paper_metric("Registry", registry.get("version", "—"))

    st.markdown(
        """
        <div class="pressure-callout">
          <b>Documentation workspace:</b> this is a configuration-backed documentation system.
          Add or reorder pages in <code>config/documentation_navigation.json</code>, then place markdown files under
          <code>docs/toolkit/</code>.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not registry.get("sections"):
        st.warning("No documentation sections are configured.")
        return

    search_query = st.text_input(
        "Search documentation",
        value="",
        key="aegis_documentation_search",
        placeholder="Search architecture, workflow, rules, deployment, troubleshooting...",
    )

    if search_query.strip():
        result_df = _search_pages(
            pages,
            search_query,
            int(documentation_cfg("max_search_results", 20) or 20),
        )
        st.markdown('<div class="pressure-section-title">Search Results</div>', unsafe_allow_html=True)
        if result_df.empty:
            st.info("No matching documentation pages found.")
        else:
            render_table(result_df, height=360)

    selected_section, selected_page = _selection_from_state(registry)

    nav_col, doc_col = st.columns([0.82, 2.18])

    with nav_col:
        with st.container(key="aegis_docs_hierarchical_side_nav"):
            _render_documentation_side_nav(registry, selected_section, selected_page)

            audience = selected_page.get("audience", "users_developers")
            if documentation_cfg("show_audience_badges", True):
                st.markdown(
                    f"<div class='documentation-audience-badge'>Audience · {audience.replace('_', ' + ')}</div>",
                    unsafe_allow_html=True,
                )

    with doc_col:
        markdown = _read_doc(str(selected_page.get("file", "")))
        breadcrumb = f"{selected_section.get('title', '')} / {selected_page.get('title', '')}"
        st.markdown(
            f"<div class='documentation-breadcrumb'>{breadcrumb}</div>",
            unsafe_allow_html=True,
        )

        headings = _extract_headings(markdown)
        if documentation_cfg("show_table_of_contents", True) and not headings.empty:
            with st.expander("Page outline", expanded=False):
                render_table(headings, height=220)

        st.markdown('<div class="documentation-document-shell">', unsafe_allow_html=True)
        st.markdown(markdown)
        st.markdown('</div>', unsafe_allow_html=True)

        if documentation_cfg("enable_markdown_download", True):
            st.download_button(
                "Download current page",
                data=markdown.encode("utf-8"),
                file_name=Path(str(selected_page.get("file", "documentation.md"))).name,
                mime="text/markdown",
            )

    with st.expander("Documentation registry", expanded=False):
        st.json(registry)

    with st.expander("Documentation file inventory", expanded=False):
        inventory = pd.DataFrame(pages)
        if inventory.empty:
            st.info("No pages found in the documentation registry.")
        else:
            render_table(inventory, height=420)
