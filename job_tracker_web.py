"""
1000 Days Job Application Tracker — Web App
Built with Streamlit + SQLite
Run:  streamlit run job_tracker_web.py
"""

import sqlite3
from contextlib import contextmanager
from datetime import datetime

import pandas as pd
import streamlit as st

# ─────────────────────────── CONFIG ───────────────────────────
DB_FILE = "job_applications.db"
TARGET_DAYS = 1000
VALID_STATUSES = ["applied", "interview", "offer", "rejected"]

STATUS_COLORS = {
    "applied":   "#3B82F6",
    "interview": "#F59E0B",
    "offer":     "#10B981",
    "rejected":  "#EF4444",
}

st.set_page_config(page_title="1000 Days Job Tracker", page_icon="🎯", layout="wide")


# ─────────────────────────── DATABASE ───────────────────────────

@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                company       TEXT NOT NULL,
                position      TEXT NOT NULL,
                status        TEXT NOT NULL DEFAULT 'applied',
                date_applied  TEXT NOT NULL,
                notes         TEXT DEFAULT ''
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS meta (
                key   TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)


def get_start_date():
    with get_conn() as conn:
        row = conn.execute("SELECT value FROM meta WHERE key='start_date'").fetchone()
        if row:
            return datetime.strptime(row["value"], "%Y-%m-%d").date()
        start = datetime.now().date()
        conn.execute("INSERT INTO meta (key,value) VALUES ('start_date',?)",
                     (start.strftime("%Y-%m-%d"),))
        return start


def db_add(company, position, status="applied", notes=""):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO applications (company,position,status,date_applied,notes) "
            "VALUES (?,?,?,?,?)",
            (company, position, status,
             datetime.now().strftime("%Y-%m-%d %H:%M:%S"), notes)
        )


def db_update(app_id, company, position, status, notes=""):
    with get_conn() as conn:
        conn.execute(
            "UPDATE applications SET company=?, position=?, status=?, notes=? WHERE id=?",
            (company, position, status, notes, app_id)
        )


def db_delete(app_id):
    with get_conn() as conn:
        conn.execute("DELETE FROM applications WHERE id=?", (app_id,))


def db_all(keyword=""):
    with get_conn() as conn:
        if keyword:
            rows = conn.execute(
                "SELECT * FROM applications "
                "WHERE company LIKE ? OR position LIKE ? ORDER BY id DESC",
                (f"%{keyword}%", f"%{keyword}%")
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM applications ORDER BY id DESC").fetchall()
    return [dict(r) for r in rows]


def db_stats():
    with get_conn() as conn:
        total = conn.execute("SELECT COUNT(*) c FROM applications").fetchone()["c"]
        counts = {}
        for s in VALID_STATUSES:
            counts[s] = conn.execute(
                "SELECT COUNT(*) c FROM applications WHERE status=?", (s,)
            ).fetchone()["c"]
    return total, counts


init_db()

# ─────────────────────────── SESSION STATE ───────────────────────────
if "editing_id" not in st.session_state:
    st.session_state.editing_id = None
if "confirm_delete_id" not in st.session_state:
    st.session_state.confirm_delete_id = None

# ─────────────────────────── SIDEBAR ───────────────────────────
with st.sidebar:
    st.markdown("## 🎯 JobTracker")
    st.caption("1000 days challenge")

    start = get_start_date()
    today = datetime.now().date()
    elapsed = (today - start).days
    pct = min(elapsed / TARGET_DAYS, 1.0)
    remaining = max(TARGET_DAYS - elapsed, 0)

    st.progress(pct)
    st.caption(f"{elapsed} / {TARGET_DAYS} days ({remaining} left)")

    st.divider()
    page = st.radio("Navigate", ["📊 Dashboard", "📋 Applications", "🔍 Search"], label_visibility="collapsed")

# ─────────────────────────── DASHBOARD ───────────────────────────
if page == "📊 Dashboard":
    st.title("Dashboard")
    st.caption("Your application journey at a glance")

    total, counts = db_stats()

    cols = st.columns(5)
    cards = [
        ("Total Applications", total),
        ("Applied", counts["applied"]),
        ("Interviews", counts["interview"]),
        ("Offers", counts["offer"]),
        ("Rejected", counts["rejected"]),
    ]
    for col, (label, value) in zip(cols, cards):
        col.metric(label, value)

    st.subheader("🗓 1000 Days Progress")
    st.progress(pct)
    c1, c2 = st.columns(2)
    c1.caption("Day 0")
    c2.markdown(f"<div style='text-align:right'>Day {elapsed} — {remaining} days remaining</div>",
                unsafe_allow_html=True)

    left, right = st.columns(2)
    with left:
        st.subheader("📈 Success Rate")
        if total:
            rate = (counts["interview"] + counts["offer"]) / total * 100
            st.markdown(f"<h1 style='color:#10B981'>{rate:.1f}%</h1>", unsafe_allow_html=True)
        else:
            st.markdown("<h1 style='color:#10B981'>–%</h1>", unsafe_allow_html=True)
        st.caption("Interviews + Offers ÷ Total")

    with right:
        st.subheader("🎨 Status Breakdown")
        for status in VALID_STATUSES:
            n = counts[status]
            spct = (n / total * 100) if total else 0
            st.markdown(f"**{status.capitalize()}** — {n} ({spct:.0f}%)")
            st.markdown(
                f"""<div style="background:#374151;border-radius:5px;height:10px;width:100%;">
                <div style="background:{STATUS_COLORS[status]};border-radius:5px;height:10px;
                width:{spct}%;"></div></div>""",
                unsafe_allow_html=True,
            )

# ─────────────────────────── APPLICATIONS ───────────────────────────
elif page == "📋 Applications":
    st.title("Applications")

    with st.expander("➕ Add application", expanded=False):
        with st.form("add_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            company = c1.text_input("Company *")
            position = c2.text_input("Position *")
            status = st.selectbox("Status", VALID_STATUSES)
            notes = st.text_area("Notes", height=80)
            submitted = st.form_submit_button("Save application")
            if submitted:
                if not company.strip() or not position.strip():
                    st.error("Company and position are required.")
                else:
                    db_add(company.strip(), position.strip(), status, notes.strip())
                    st.success(f"Added {company} — {position}")
                    st.rerun()

    filt = st.radio("Filter", ["all"] + VALID_STATUSES, horizontal=True,
                     format_func=lambda s: "All" if s == "all" else s.capitalize())

    rows = db_all()
    if filt != "all":
        rows = [r for r in rows if r["status"] == filt]

    if not rows:
        st.info("No applications found.")
    else:
        for app in rows:
            if st.session_state.editing_id == app["id"]:
                with st.container(border=True):
                    with st.form(f"edit_form_{app['id']}"):
                        c1, c2 = st.columns(2)
                        e_company = c1.text_input("Company *", value=app["company"])
                        e_position = c2.text_input("Position *", value=app["position"])
                        e_status = st.selectbox("Status", VALID_STATUSES,
                                                 index=VALID_STATUSES.index(app["status"]))
                        e_notes = st.text_area("Notes", value=app["notes"] or "", height=80)
                        s1, s2 = st.columns(2)
                        save = s1.form_submit_button("Save changes", use_container_width=True)
                        cancel = s2.form_submit_button("Cancel", use_container_width=True)
                        if save:
                            if not e_company.strip() or not e_position.strip():
                                st.error("Company and position are required.")
                            else:
                                db_update(app["id"], e_company.strip(), e_position.strip(),
                                           e_status, e_notes.strip())
                                st.session_state.editing_id = None
                                st.rerun()
                        if cancel:
                            st.session_state.editing_id = None
                            st.rerun()
            else:
                with st.container(border=True):
                    c1, c2, c3, c4, c5 = st.columns([2, 2, 1.2, 1.5, 1])
                    c1.markdown(f"**{app['company']}**  \n`#{app['id']}`")
                    c2.markdown(app["position"])
                    color = STATUS_COLORS.get(app["status"], "#6B7280")
                    c3.markdown(
                        f"<span style='background:{color};color:white;padding:2px 10px;"
                        f"border-radius:8px;font-size:12px;font-weight:bold'>"
                        f"{app['status'].upper()}</span>",
                        unsafe_allow_html=True,
                    )
                    c4.caption(app["date_applied"][:10])
                    with c5:
                        b1, b2 = st.columns(2)
                        if b1.button("✏️", key=f"edit_{app['id']}"):
                            st.session_state.editing_id = app["id"]
                            st.rerun()
                        if b2.button("🗑️", key=f"del_{app['id']}"):
                            st.session_state.confirm_delete_id = app["id"]
                            st.rerun()
                    if app["notes"]:
                        st.caption(app["notes"])

                    if st.session_state.confirm_delete_id == app["id"]:
                        st.warning(f"Delete #{app['id']} — {app['company']} / {app['position']}? This cannot be undone.")
                        d1, d2 = st.columns(2)
                        if d1.button("Yes, delete", key=f"confirm_del_{app['id']}"):
                            db_delete(app["id"])
                            st.session_state.confirm_delete_id = None
                            st.rerun()
                        if d2.button("Cancel", key=f"cancel_del_{app['id']}"):
                            st.session_state.confirm_delete_id = None
                            st.rerun()

# ─────────────────────────── SEARCH ───────────────────────────
elif page == "🔍 Search":
    st.title("Search")
    kw = st.text_input("Search by company or position…")

    if kw.strip():
        rows = db_all(keyword=kw.strip())
        st.caption(f"{len(rows)} result(s) for '{kw.strip()}'")
        if rows:
            df = pd.DataFrame(rows)[["id", "company", "position", "status", "date_applied", "notes"]]
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info(f"No results for \"{kw.strip()}\".")
    else:
        st.caption("Enter a search term above.")
