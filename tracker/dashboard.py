"""Streamlit dashboard — visual overview of project health.

Run:  streamlit run tracker/dashboard.py
"""

from __future__ import annotations

import streamlit as st

from tracker import db

st.set_page_config(page_title="Project Tracker", page_icon="📊", layout="wide")
st.title("📊 Project Tracker Dashboard")

# ---------------------------------------------------------------------------
# Sidebar: connection status
# ---------------------------------------------------------------------------

try:
    with db.connect() as conn:
        projects = db.list_projects(conn)
        milestones = db.list_milestones(conn)
        tasks = db.list_tasks(conn)
        members = db.list_members(conn)
        workload = db.workload_summary(conn)
        ms_progress = db.milestone_progress(conn)
    st.sidebar.success("Connected to database")
except Exception as exc:
    st.error(f"Cannot connect to database: {exc}")
    st.info("Start the database with: `docker compose up -d`")
    st.stop()

# ---------------------------------------------------------------------------
# KPI row
# ---------------------------------------------------------------------------

col1, col2, col3, col4 = st.columns(4)
done_count = sum(1 for t in tasks if t.status.value == "done")
blocked_count = sum(1 for t in tasks if t.status.value == "blocked")
overdue_count = sum(1 for t in tasks if t.is_overdue)

col1.metric("Total Tasks", len(tasks))
col2.metric("Completed", done_count)
col3.metric("Blocked", blocked_count, delta_color="inverse")
col4.metric("Overdue", overdue_count, delta_color="inverse")

st.divider()

# ---------------------------------------------------------------------------
# Two-column layout: milestones + workload
# ---------------------------------------------------------------------------

left, right = st.columns(2)

with left:
    st.subheader("Milestone Progress")
    if ms_progress:
        for ms in ms_progress:
            pct = float(ms["pct_complete"])
            label = f"{ms['title']} — {ms['done_tasks']}/{ms['total_tasks']} tasks"
            if ms["target_date"]:
                label += f" (due {ms['target_date']})"
            st.progress(pct / 100, text=label)
    else:
        st.info("No open milestones.")

with right:
    st.subheader("Team Workload")
    if workload:
        for w in workload:
            cap = w["capacity_hours"]
            assigned = float(w["assigned_hours"])
            util = assigned / cap if cap > 0 else 0
            color = "🔴" if util > 1.0 else ("🟡" if util > 0.8 else "🟢")
            st.markdown(
                f"{color} **{w['name']}** — {assigned:.0f}h assigned / "
                f"{cap:.0f}h capacity ({util:.0%}) · "
                f"{w['active_tasks']} active tasks"
            )
    else:
        st.info("No team members yet.")

st.divider()

# ---------------------------------------------------------------------------
# Task board (kanban-style columns)
# ---------------------------------------------------------------------------

st.subheader("Task Board")
statuses = ["backlog", "todo", "in_progress", "in_review", "done", "blocked"]
cols = st.columns(len(statuses))

for col, status_val in zip(cols, statuses, strict=True):
    status_tasks = [t for t in tasks if t.status.value == status_val]
    col.markdown(f"**{status_val.replace('_', ' ').title()}** ({len(status_tasks)})")
    for t in status_tasks:
        pri_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "⚪"}
        overdue_mark = " ⚠️" if t.is_overdue else ""
        col.markdown(
            f"{pri_emoji.get(t.priority.value, '')} {t.title}{overdue_mark}",
            help=f"#{t.id} · Est: {t.estimated_hours}h · Act: {t.actual_hours}h",
        )

st.divider()

# ---------------------------------------------------------------------------
# Team members table
# ---------------------------------------------------------------------------

st.subheader("Team")
if members:
    st.dataframe(
        [
            {"ID": m.id, "Name": m.name, "Role": m.role,
             "Email": m.email, "Capacity (h/wk)": m.capacity_hours}
            for m in members
        ],
        use_container_width=True,
        hide_index=True,
    )
