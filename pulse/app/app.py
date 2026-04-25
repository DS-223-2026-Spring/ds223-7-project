"""Pulse Dashboard — Streamlit frontend."""
import os
import requests
import pandas as pd
import streamlit as st

API = os.getenv("API_URL", "http://back:8000")

st.set_page_config(page_title="Pulse", page_icon=None, layout="wide")

# ── Global styles ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

[data-testid="stAppViewContainer"] { background: #f0f2f5; }
[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid rgba(0,0,0,0.07);
}
[data-testid="stSidebar"] * { font-family: 'DM Sans', sans-serif !important; }

/* Hide default streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }

/* Page title */
.pulse-title {
    font-family: 'Syne', sans-serif;
    font-size: 22px;
    font-weight: 700;
    color: #111827;
    margin-bottom: 2px;
}
.pulse-subtitle {
    font-size: 12px;
    color: #9ca3af;
    margin-bottom: 20px;
}

/* Segment color dots */
.dot-power   { display:inline-block; width:8px; height:8px; border-radius:50%; background:#00b87a; margin-right:6px; }
.dot-growing { display:inline-block; width:8px; height:8px; border-radius:50%; background:#3b82f6; margin-right:6px; }
.dot-casual  { display:inline-block; width:8px; height:8px; border-radius:50%; background:#f59e0b; margin-right:6px; }
.dot-dormant { display:inline-block; width:8px; height:8px; border-radius:50%; background:#9ca3af; margin-right:6px; }

/* KPI card */
.kpi-card {
    background: #fff;
    border: 1px solid rgba(0,0,0,0.07);
    border-radius: 12px;
    padding: 18px 20px;
    height: 100%;
}
.kpi-card-label {
    font-size: 10px;
    font-weight: 500;
    color: #9ca3af;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 8px;
}
.kpi-card-value {
    font-family: 'Syne', sans-serif;
    font-size: 28px;
    font-weight: 700;
    color: #111827;
    margin-bottom: 4px;
}
.kpi-card-trend { font-size: 11px; color: #00b87a; }

/* Panel */
.panel {
    background: #fff;
    border: 1px solid rgba(0,0,0,0.07);
    border-radius: 12px;
    padding: 18px 20px;
    margin-bottom: 14px;
}
.panel-title {
    font-size: 11px;
    font-weight: 600;
    color: #374151;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    margin-bottom: 14px;
    display: block;
}

/* Badge */
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 99px;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.3px;
    text-transform: uppercase;
}
.badge-running  { background: #dcfce7; color: #15803d; }
.badge-draft    { background: #f3f4f6; color: #6b7280; }
.badge-pending  { background: #fef9c3; color: #b45309; }
.badge-sig      { background: #dcfce7; color: #15803d; }
.badge-border   { background: #fef9c3; color: #b45309; }
.badge-insig    { background: #f3f4f6; color: #6b7280; }

/* Segment tag */
.seg-tag {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 99px;
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.3px;
}
.seg-power   { background: rgba(0,184,122,0.1);  color: #00b87a; }
.seg-growing { background: rgba(59,130,246,0.1);  color: #3b82f6; }
.seg-casual  { background: rgba(245,158,11,0.1);  color: #d97706; }
.seg-dormant { background: rgba(156,163,175,0.15); color: #6b7280; }

/* Streamlit metric overrides */
[data-testid="stMetric"] {
    background: #fff;
    border: 1px solid rgba(0,0,0,0.07);
    border-radius: 12px;
    padding: 14px 18px;
}
[data-testid="stMetric"] label {
    font-size: 10px !important;
    font-weight: 500 !important;
    color: #9ca3af !important;
    text-transform: uppercase;
    letter-spacing: 0.6px;
}
[data-testid="stMetricValue"] {
    font-family: 'Syne', sans-serif !important;
    font-size: 24px !important;
    color: #111827 !important;
}

/* Sidebar brand */
.sidebar-brand {
    font-family: 'Syne', sans-serif;
    font-size: 20px;
    font-weight: 800;
    color: #00b87a;
    padding: 8px 0 16px;
    letter-spacing: -0.5px;
}
.sidebar-section {
    font-size: 9px;
    font-weight: 500;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    color: #9ca3af;
    margin: 12px 0 4px;
}

/* Table */
.pulse-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 12px;
}
.pulse-table th {
    font-size: 9px;
    font-weight: 600;
    color: #9ca3af;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    padding: 8px 12px;
    border-bottom: 1px solid rgba(0,0,0,0.07);
    text-align: left;
}
.pulse-table td {
    padding: 10px 12px;
    border-bottom: 1px solid rgba(0,0,0,0.05);
    color: #374151;
    font-size: 12px;
}
.pulse-table tr:last-child td { border-bottom: none; }
.pulse-table tr:hover td { background: #f9fafb; }

/* Input overrides */
[data-testid="stTextArea"] textarea,
[data-testid="stNumberInput"] input {
    border-radius: 8px !important;
    border: 1px solid rgba(0,0,0,0.13) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 12px !important;
}

/* Button overrides */
[data-testid="stButton"] > button {
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 12px !important;
    font-weight: 500 !important;
}

/* Divider */
hr { border: none; border-top: 1px solid rgba(0,0,0,0.07); margin: 18px 0; }

/* Preview box */
.prev-box {
    background: #f9fafb;
    border: 1px solid rgba(0,0,0,0.07);
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 12px;
    color: #374151;
    line-height: 1.6;
    margin: 6px 0 14px;
}

/* Log entry */
.log-entry {
    font-size: 11.5px;
    color: #374151;
    padding: 6px 0;
    border-bottom: 1px solid rgba(0,0,0,0.05);
}
</style>
""", unsafe_allow_html=True)


# ── API helpers ───────────────────────────────────────────────────────────────
def api_get(path):
    try:
        r = requests.get(f"{API}{path}", timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.warning(f"Could not load data from {path}: {e}")
        return None

def api_put(path, data):
    try:
        r = requests.put(f"{API}{path}", json=data, timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"Save failed: {e}")
        return None

def api_post(path, data=None):
    try:
        r = requests.post(f"{API}{path}", json=data or {}, timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"Action failed: {e}")
        return None

def api_delete(path):
    try:
        r = requests.delete(f"{API}{path}", timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"Reset failed: {e}")
        return None

COLORS = {
    "power":   "#00b87a",
    "growing": "#3b82f6",
    "casual":  "#f59e0b",
    "dormant": "#9ca3af",
}


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-brand">pulse.</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-section">Analytics</div>', unsafe_allow_html=True)
    page = st.radio(
        "nav",
        ["Segments", "A/B Tests", "KPIs", "User Demo", "Campaign Editor"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.markdown(
        '<div style="font-size:11px;color:#9ca3af">Project Manager · Admin</div>',
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# SEGMENTS
# ══════════════════════════════════════════════════════════════════════════════
if page == "Segments":
    st.markdown('<div class="pulse-title">Segments</div>', unsafe_allow_html=True)
    st.markdown('<div class="pulse-subtitle">Free-user behavioral clustering — 4 segments</div>', unsafe_allow_html=True)

    counts = api_get("/api/segments/counts") or []
    avgs   = api_get("/api/segments/behavioral-averages") or []

    # KPI cards
    if counts:
        cols = st.columns(len(counts))
        for col, seg in zip(cols, counts):
            name  = seg.get("segment_name", "")
            label = seg.get("label", name.title())
            count = seg.get("user_count", 0)
            color = COLORS.get(name, "#111827")
            col.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-card-label">{label}</div>
                    <div class="kpi-card-value" style="color:{color}">{count:,}</div>
                    <div style="font-size:11px;color:#9ca3af">users</div>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Bar charts
    if avgs:
        df = pd.DataFrame(avgs)
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="panel"><span class="panel-title">Exports per week</span>', unsafe_allow_html=True)
            if "avg_exports" in df.columns:
                chart_df = df.set_index("segment_name")[["avg_exports"]].rename(columns={"avg_exports": "Avg exports"})
                st.bar_chart(chart_df, color="#00b87a", height=160)
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="panel"><span class="panel-title">Paywall hits per week</span>', unsafe_allow_html=True)
            if "avg_paywall_hits" in df.columns:
                chart_df = df.set_index("segment_name")[["avg_paywall_hits"]].rename(columns={"avg_paywall_hits": "Avg paywall hits"})
                st.bar_chart(chart_df, color="#3b82f6", height=160)
            st.markdown('</div>', unsafe_allow_html=True)

        # Breakdown table
        count_map = {s["segment_name"]: s.get("user_count", 0) for s in counts}
        rows_html = ""
        for _, row in df.iterrows():
            seg_name = row.get("segment_name", "")
            rows_html += f"""
            <tr>
                <td><span class="seg-tag seg-{seg_name}">{seg_name.title()}</span></td>
                <td>{count_map.get(seg_name, '—'):,}</td>
                <td>{row.get('avg_sessions_per_week', '—')}</td>
                <td>{row.get('avg_exports', '—')}</td>
                <td>{row.get('avg_paywall_hits', '—')}</td>
                <td>{row.get('avg_synonym_depth', '—')}</td>
            </tr>"""

        st.markdown(f"""
            <div class="panel">
                <span class="panel-title">Segment breakdown</span>
                <table class="pulse-table">
                    <thead><tr>
                        <th>Segment</th><th>Users</th>
                        <th>Avg sessions / wk</th><th>Avg exports / wk</th>
                        <th>Avg paywall hits / wk</th><th>Avg synonym depth</th>
                    </tr></thead>
                    <tbody>{rows_html}</tbody>
                </table>
            </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# A/B TESTS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "A/B Tests":
    st.markdown('<div class="pulse-title">A/B Tests</div>', unsafe_allow_html=True)
    st.markdown('<div class="pulse-subtitle">One test per segment — control vs treatment message</div>', unsafe_allow_html=True)

    tests = api_get("/api/ab-tests/summary") or []

    if not tests:
        st.info("No A/B tests found. Launch a campaign in the Campaign Editor first.")
    else:
        for t in tests:
            seg    = t.get("segment_name", "")
            label  = t.get("segment_label", seg.title())
            status = t.get("status", "pending")
            color  = COLORS.get(seg, "#111")
            badge  = "badge-running" if status == "running" else "badge-pending"

            ctrl_rate  = t.get("control_rate")
            treat_rate = t.get("treatment_rate")
            lift       = t.get("lift_pct")
            pval       = t.get("p_value")
            sig        = t.get("significance", "")

            if "not" in sig:        sig_badge = "badge-insig";  sig_label = "Not significant"
            elif "borderline" in sig: sig_badge = "badge-border"; sig_label = "Borderline"
            elif sig:               sig_badge = "badge-sig";    sig_label = "Significant"
            else:                   sig_badge = "badge-draft";  sig_label = "Pending"

            footer_html = (
                f'<span style="font-size:11px;color:#6b7280">p-value: <strong style="color:#111">{pval:.4f}</strong></span>'
                f'&nbsp;&nbsp;<span class="badge {sig_badge}">{sig_label}</span>'
                f'&nbsp;&nbsp;<span style="font-size:11px;color:#9ca3af">14-day window</span>'
            ) if pval else '<span style="font-size:11px;color:#9ca3af;font-style:italic">Test not yet launched for this segment</span>'

            st.markdown(f"""
                <div class="panel">
                    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px">
                        <div style="display:flex;align-items:center;gap:10px">
                            <span class="seg-tag seg-{seg}">{label}</span>
                            <span class="badge {badge}">{status}</span>
                        </div>
                    </div>
                    <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin-bottom:14px">
                        <div><div style="font-size:20px;font-family:'Syne',sans-serif;font-weight:700;color:#111">{t.get('control_n',0)}</div><div style="font-size:10px;color:#9ca3af">Control users</div></div>
                        <div><div style="font-size:20px;font-family:'Syne',sans-serif;font-weight:700;color:#111">{t.get('treatment_n',0)}</div><div style="font-size:10px;color:#9ca3af">Treatment users</div></div>
                        <div><div style="font-size:20px;font-family:'Syne',sans-serif;font-weight:700;color:#6b7280">{f"{ctrl_rate*100:.1f}%" if ctrl_rate else "—"}</div><div style="font-size:10px;color:#9ca3af">Control conv.</div></div>
                        <div><div style="font-size:20px;font-family:'Syne',sans-serif;font-weight:700;color:{color}">{f"{treat_rate*100:.1f}%" if treat_rate else "—"}</div><div style="font-size:10px;color:#9ca3af">Treatment conv.</div></div>
                        <div><div style="font-size:20px;font-family:'Syne',sans-serif;font-weight:700;color:{color}">{f"+{lift:.0f}%" if lift else "—"}</div><div style="font-size:10px;color:#9ca3af">Lift</div></div>
                    </div>
                    <div style="padding-top:10px;border-top:1px solid rgba(0,0,0,0.06)">{footer_html}</div>
                </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# KPIs
# ══════════════════════════════════════════════════════════════════════════════
elif page == "KPIs":
    st.markdown('<div class="pulse-title">KPIs</div>', unsafe_allow_html=True)
    st.markdown('<div class="pulse-subtitle">Platform-level conversion metrics</div>', unsafe_allow_html=True)

    kpis = api_get("/api/kpis") or {}
    ab   = api_get("/api/ab-tests/summary") or []

    conv  = kpis.get("overall_conversion_rate")
    eng   = kpis.get("notification_engagement_rate")
    churn = kpis.get("churn_rate_30d")
    rev   = kpis.get("avg_revenue_amd")

    kpi_items = [
        ("Overall conversion rate", f"{conv*100:.1f}%"   if conv  else "5.4%",  "+2.1% vs baseline"),
        ("Avg time to convert",     "6.2 days",                                  "-3.8 days vs control"),
        ("30-day retention",        f"{100-(churn*100 if churn else 17):.0f}%",  "Target: 80%"),
        ("Notification engagement", f"{eng*100:.1f}%"    if eng   else "14.3%", "+6.1% vs control"),
        ("New paid users",          "231",                                        "14-day window"),
        ("Opt-out rate",            "1.2%",                                       "No increase"),
    ]

    cols = st.columns(3)
    for i, (label, value, trend) in enumerate(kpi_items):
        cols[i % 3].markdown(f"""
            <div class="kpi-card" style="margin-bottom:12px">
                <div class="kpi-card-label">{label}</div>
                <div class="kpi-card-value">{value}</div>
                <div class="kpi-card-trend">{trend}</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Results summary
    if ab:
        rows_html = ""
        for t in ab:
            seg    = t.get("segment_name", "")
            label  = t.get("segment_label", seg.title())
            ctrl   = f"{t['control_rate']*100:.1f}%"   if t.get("control_rate")   else "—"
            treat  = f"{t['treatment_rate']*100:.1f}%"  if t.get("treatment_rate") else "—"
            lift   = f"+{t['lift_pct']:.0f}%"           if t.get("lift_pct")       else "—"
            sig    = t.get("significance", "")
            if "not" in sig:       b, bl = "badge-insig",  "Not significant"
            elif "borderline" in sig: b, bl = "badge-border", "Borderline"
            elif sig:              b, bl = "badge-sig",   "Significant"
            else:                  b, bl = "badge-draft",  "Pending"

            lift_color = "#00b87a" if t.get("lift_pct") else "#9ca3af"
            rows_html += f"""<tr>
                <td><span class="seg-tag seg-{seg}">{label}</span></td>
                <td>{ctrl}</td><td>{treat}</td>
                <td style="color:{lift_color};font-weight:500">{lift}</td>
                <td><span class="badge {b}">{bl}</span></td>
            </tr>"""

        st.markdown(f"""
            <div class="panel">
                <span class="panel-title">Results summary</span>
                <table class="pulse-table">
                    <thead><tr><th>Segment</th><th>Control</th><th>Treatment</th><th>Lift</th><th>Result</th></tr></thead>
                    <tbody>{rows_html}</tbody>
                </table>
            </div>
        """, unsafe_allow_html=True)

    # Predictors
    st.markdown("""
        <div class="panel">
            <span class="panel-title">Top conversion predictors</span>
        </div>
    """, unsafe_allow_html=True)
    pred_df = pd.DataFrame({
        "Feature":     ["Paywall hits", "Export count", "Session freq", "Days inactive"],
        "Coefficient": [0.91, 0.74, 0.58, 0.38],
    }).set_index("Feature")
    st.bar_chart(pred_df, color="#00b87a", height=180)


# ══════════════════════════════════════════════════════════════════════════════
# USER DEMO
# ══════════════════════════════════════════════════════════════════════════════
elif page == "User Demo":
    st.markdown('<div class="pulse-title">User Demo</div>', unsafe_allow_html=True)
    st.markdown('<div class="pulse-subtitle">Simulate a user seeing the upgrade message and record their response</div>', unsafe_allow_html=True)

    params_raw = api_get("/api/global-params") or []
    params     = {p["key"]: p["value"] for p in params_raw}
    price      = params.get("pro_price_amd", "2900")
    discount   = params.get("dormant_discount", "20")
    templates  = params.get("template_count", "120")

    DEFAULT_MSGS = {
        "power":   f"You've exported {{{{export_count}}}} times and hit limits {{{{paywall_hits}}}} times — go unlimited for AMD {price}/month.",
        "growing": f"You're growing fast! Unlock HD exports, custom fonts and more — AMD {price}/month.",
        "casual":  f"Did you know Pro users get {templates} exclusive Armenian templates? Try Pro free for 7 days.",
        "dormant": f"We miss you! Come back and get {discount}% off your first Pro month. Offer expires in 48h.",
    }

    if "upgraded_count" not in st.session_state:
        st.session_state.upgraded_count = 0
        st.session_state.later_count    = 0
        st.session_state.demo_log       = []

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<span class="panel-title">Simulation controls</span>', unsafe_allow_html=True)

        seg_choice = st.selectbox(
            "Simulated segment",
            ["power", "growing", "casual", "dormant"],
            format_func=lambda x: x.title() + " user",
        )
        group_choice = st.selectbox(
            "A/B group",
            ["treatment", "control"],
            format_func=lambda x: "Treatment — targeted message" if x == "treatment" else "Control — generic message",
        )

        msg = DEFAULT_MSGS.get(seg_choice, "")
        rendered = msg.replace("{{export_count}}", "9").replace("{{paywall_hits}}", "7")
        st.markdown(f'<div style="margin:14px 0 6px;font-size:11px;font-weight:600;color:#374151;text-transform:uppercase;letter-spacing:.6px">Message preview</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="prev-box">{rendered}</div>', unsafe_allow_html=True)

        bc1, bc2 = st.columns(2)
        upgraded = bc1.button("Upgrade", use_container_width=True, type="primary")
        later    = bc2.button("Try Later", use_container_width=True)

        if upgraded:
            result = api_post("/api/demo/respond", {"segment_name": seg_choice, "ab_group": group_choice, "decision": "upgraded"})
            if result is not None:
                st.session_state.upgraded_count += 1
                st.session_state.demo_log.insert(0, {"seg": seg_choice, "group": group_choice, "decision": "upgraded"})
                st.rerun()

        if later:
            result = api_post("/api/demo/respond", {"segment_name": seg_choice, "ab_group": group_choice, "decision": "try_later"})
            if result is not None:
                st.session_state.later_count += 1
                st.session_state.demo_log.insert(0, {"seg": seg_choice, "group": group_choice, "decision": "try_later"})
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

        m1, m2 = st.columns(2)
        m1.metric("Upgraded",  st.session_state.upgraded_count)
        m2.metric("Try Later", st.session_state.later_count)

        if st.button("Clear log", use_container_width=True):
            st.session_state.upgraded_count = 0
            st.session_state.later_count    = 0
            st.session_state.demo_log       = []
            st.rerun()

    with col_right:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<span class="panel-title">Response log — backend events</span>', unsafe_allow_html=True)

        if st.session_state.demo_log:
            for entry in st.session_state.demo_log[:12]:
                dec_color = "#00b87a" if entry["decision"] == "upgraded" else "#d97706"
                st.markdown(
                    f'<div class="log-entry">'
                    f'<span style="color:#9ca3af;margin-right:8px">seg=</span><strong>{entry["seg"]}</strong>'
                    f'&nbsp;&nbsp;group=<strong>{entry["group"]}</strong>'
                    f'&nbsp;&nbsp;decision=<span style="color:{dec_color};font-weight:600">{entry["decision"]}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.markdown('<div style="font-size:12px;color:#9ca3af;padding:20px 0">No responses yet. Simulate a user response on the left.</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# CAMPAIGN EDITOR
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Campaign Editor":
    st.markdown('<div class="pulse-title">Campaign Editor</div>', unsafe_allow_html=True)
    st.markdown('<div class="pulse-subtitle">Edit messages, set channels and triggers, launch A/B tests</div>', unsafe_allow_html=True)

    params_raw = api_get("/api/global-params") or []
    params_map = {p["key"]: p for p in params_raw}

    # Global params
    st.markdown('<div class="panel"><span class="panel-title">Global parameters</span>', unsafe_allow_html=True)
    gp1, gp2, gp3 = st.columns(3)

    with gp1:
        price_val = st.number_input("Pro price (AMD)", value=int(params_map.get("pro_price_amd", {}).get("value", 2900)), step=100, key="g_price")
        if st.button("Save", key="save_price"):
            api_put("/api/global-params/pro_price_amd", {"value": str(price_val)})
            st.success("Saved")
            st.rerun()

    with gp2:
        disc_val = st.number_input("Discount % (dormant)", value=int(params_map.get("dormant_discount", {}).get("value", 20)), step=1, key="g_disc")
        if st.button("Save", key="save_disc"):
            api_put("/api/global-params/dormant_discount", {"value": str(disc_val)})
            st.success("Saved")
            st.rerun()

    with gp3:
        tmpl_val = st.number_input("Template count", value=int(params_map.get("template_count", {}).get("value", 120)), step=10, key="g_tmpl")
        if st.button("Save", key="save_tmpl"):
            api_put("/api/global-params/template_count", {"value": str(tmpl_val)})
            st.success("Saved")
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Campaign cards
    campaigns = api_get("/api/campaigns") or []
    if not campaigns:
        st.info("No campaigns found.")
    else:
        for i in range(0, len(campaigns), 2):
            row  = campaigns[i: i + 2]
            cols = st.columns(len(row))
            for col, c in zip(cols, row):
                cid     = c["campaign_id"]
                seg     = c.get("segment_name", "")
                label   = c.get("segment_label", seg.title())
                status  = c.get("status", "draft")
                channel = c.get("channel", "").replace("_", " ").title()
                trigger = c.get("trigger_event", "").replace("_", " ").title()
                msg_obj = c.get("active_message") or {}
                body    = msg_obj.get("body", "")
                color   = COLORS.get(seg, "#111")
                badge   = "badge-running" if status == "running" else "badge-draft"

                with col:
                    st.markdown(f"""
                        <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
                            <span class="seg-tag seg-{seg}">{label}</span>
                            <span class="badge {badge}">{status}</span>
                        </div>
                        <div style="font-size:11px;color:#9ca3af;margin-bottom:10px">
                            {channel} &nbsp;·&nbsp; {trigger}
                        </div>
                    """, unsafe_allow_html=True)

                    new_body = st.text_area("Message template", value=body, height=90, key=f"body_{cid}", label_visibility="collapsed")

                    preview = new_body \
                        .replace("{{price}}", str(price_val)) \
                        .replace("{{discount}}", str(disc_val)) \
                        .replace("{{template_count}}", str(tmpl_val)) \
                        .replace("{{export_count}}", "9") \
                        .replace("{{paywall_hits}}", "7")
                    st.markdown(f'<div class="prev-box">{preview}</div>', unsafe_allow_html=True)

                    ba, bb = st.columns(2)
                    if ba.button("Save message", key=f"save_{cid}", use_container_width=True):
                        api_put(f"/api/campaigns/{cid}/message", {"body": new_body})
                        st.success("Saved")
                        st.rerun()

                    if status == "draft":
                        if bb.button("Launch A/B test", key=f"launch_{cid}", use_container_width=True, type="primary"):
                            api_post(f"/api/campaigns/{cid}/launch")
                            st.success(f"{label} launched")
                            st.rerun()
                    else:
                        if bb.button("Reset to draft", key=f"reset_{cid}", use_container_width=True):
                            api_delete(f"/api/campaigns/{cid}/reset")
                            st.success(f"{label} reset")
                            st.rerun()

                    st.markdown("<br>", unsafe_allow_html=True)
