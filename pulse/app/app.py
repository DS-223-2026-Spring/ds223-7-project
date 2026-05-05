"""Pulse Dashboard — Streamlit frontend (Milestone 3: mock data)."""
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Pulse", layout="wide")

# ── Mock data ───────────────────────────────────────────────────────────────────────
# Field names match the real API shapes so wiring in M4 is a one-line change.

SEGMENTS = [
    {"segment_name": "power",   "label": "Power",   "user_count": 124,
     "avg_sessions_per_week": 8.4, "avg_exports": 9.2, "avg_paywall_hits": 6.8},
    {"segment_name": "growing", "label": "Growing", "user_count": 158,
     "avg_sessions_per_week": 5.1, "avg_exports": 4.3, "avg_paywall_hits": 2.1},
    {"segment_name": "casual",  "label": "Casual",  "user_count": 98,
     "avg_sessions_per_week": 2.3, "avg_exports": 1.8, "avg_paywall_hits": 0.6},
    {"segment_name": "dormant", "label": "Dormant", "user_count": 62,
     "avg_sessions_per_week": 0.4, "avg_exports": 0.2, "avg_paywall_hits": 0.1},
]

AB_TESTS = [
    {"segment_name": "power",   "segment_label": "Power",
     "control_rate": 0.042, "treatment_rate": 0.071, "lift_pct": 69, "p_value": 0.031, "significance": "significant", "status": "running"},
    {"segment_name": "growing", "segment_label": "Growing",
     "control_rate": 0.038, "treatment_rate": 0.055, "lift_pct": 45, "p_value": 0.087, "significance": "borderline",   "status": "running"},
    {"segment_name": "casual",  "segment_label": "Casual",
     "control_rate": 0.021, "treatment_rate": 0.028, "lift_pct": 33, "p_value": 0.210, "significance": "not significant", "status": "pending"},
    {"segment_name": "dormant", "label": "Dormant",
     "control_rate": 0.015, "treatment_rate": 0.024, "lift_pct": 60, "p_value": 0.045, "significance": "significant", "status": "running"},
]

KPIS = {
    "overall_conversion_rate":       0.054,
    "avg_time_to_convert_days":      6.2,
    "retention_30d":                 0.83,
    "notification_engagement_rate":  0.143,
    "new_paid_users":                231,
    "opt_out_rate":                  0.012,
}

CAMPAIGNS = [
    {"campaign_id": 1, "segment_name": "power",   "segment_label": "Power",
     "status": "running", "channel": "in_app", "trigger_event": "paywall_hit",
     "active_message": {"body": "You’ve exported {{export_count}} times — go unlimited for AMD {{price}}/month."}},
    {"campaign_id": 2, "segment_name": "growing",  "segment_label": "Growing",
     "status": "draft",   "channel": "email",  "trigger_event": "session_start",
     "active_message": {"body": "You’re growing fast! Unlock HD exports for AMD {{price}}/month."}},
    {"campaign_id": 3, "segment_name": "casual",   "segment_label": "Casual",
     "status": "draft",   "channel": "push",   "trigger_event": "login",
     "active_message": {"body": "Did you know Pro users get {{template_count}} exclusive Armenian templates?"}},
    {"campaign_id": 4, "segment_name": "dormant",  "segment_label": "Dormant",
     "status": "draft",   "channel": "email",  "trigger_event": "re_engage",
     "active_message": {"body": "We miss you! Get {{discount}}% off your first Pro month — 48h only."}},
]

GLOBAL_PARAMS = {"pro_price_amd": 2900, "dormant_discount": 20, "template_count": 120}

DEFAULT_MSGS = {
    "power":   "You’ve exported 9 times and hit limits 7 times — go unlimited for AMD 2900/month.",
    "growing": "You’re growing fast! Unlock HD exports, custom fonts and more — AMD 2900/month.",
    "casual":  "Did you know Pro users get 120 exclusive Armenian templates? Try Pro free for 7 days.",
    "dormant": "We miss you! Come back and get 20% off your first Pro month. Offer expires in 48h.",
}


# ── Sidebar ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("pulse.")
    page = st.radio(
        "Navigation",
        ["Segments", "A/B Tests", "KPIs", "Campaign Editor", "User Demo"],
        label_visibility="collapsed",
    )
    st.caption("Milestone 3 — mock data")



# ────────────────────────────────────────────────────────────────────────────────
# SEGMENTS — user counts per segment, avg sessions, avg exports, avg paywall hits
# ────────────────────────────────────────────────────────────────────────────────
if page == "Segments":
    st.title("Segments")
    st.caption("Free-user behavioural clustering — 4 segments")

    # Metrics row: user count per segment
    cols = st.columns(4)
    for col, seg in zip(cols, SEGMENTS):
        col.metric(seg["label"], seg["user_count"], help="Total free users in this segment")

    st.divider()

    # Bar charts: avg sessions & avg exports side by side
    df = pd.DataFrame(SEGMENTS).set_index("segment_name")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Avg sessions / week")
        st.bar_chart(df[["avg_sessions_per_week"]])
    with c2:
        st.subheader("Avg exports / week")
        st.bar_chart(df[["avg_exports"]])

    st.divider()

    # Breakdown data table
    st.subheader("Segment breakdown")
    table_df = pd.DataFrame(SEGMENTS)[
        ["label", "user_count", "avg_sessions_per_week", "avg_exports", "avg_paywall_hits"]
    ].rename(columns={
        "label":                  "Segment",
        "user_count":             "Users",
        "avg_sessions_per_week":  "Avg sessions / wk",
        "avg_exports":            "Avg exports / wk",
        "avg_paywall_hits":       "Avg paywall hits / wk",
    })
    st.dataframe(table_df, use_container_width=True, hide_index=True)



# ────────────────────────────────────────────────────────────────────────────────
# A/B TESTS — control vs treatment conversion rate, lift %, p-value per segment
# ────────────────────────────────────────────────────────────────────────────────
elif page == "A/B Tests":
    st.title("A/B Tests")
    st.caption("One test per segment — control vs treatment message")

    # Summary metrics
    running = sum(1 for t in AB_TESTS if t.get("status") == "running")
    sig     = sum(1 for t in AB_TESTS if "not" not in t.get("significance", "") and "significant" in t.get("significance", ""))
    m1, m2, m3 = st.columns(3)
    m1.metric("Tests running", running)
    m2.metric("Significant results", sig)
    m3.metric("Segments tested", len(AB_TESTS))

    st.divider()

    # Comparison table with lift and p-value columns
    st.subheader("Results by segment")
    rows = []
    for t in AB_TESTS:
        rows.append({
            "Segment":       t.get("segment_label", t.get("segment_name", "").title()),
            "Control rate":  f"{t['control_rate']*100:.1f}%"   if t.get("control_rate")   else "—",
            "Treatment rate":f"{t['treatment_rate']*100:.1f}%" if t.get("treatment_rate") else "—",
            "Lift %":        f"+{t['lift_pct']:.0f}%"          if t.get("lift_pct")       else "—",
            "p-value":       f"{t['p_value']:.3f}"             if t.get("p_value")        else "—",
            "Significance":  t.get("significance", "pending").title(),
            "Status":        t.get("status", "pending").title(),
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.divider()

    # Lift bar chart
    st.subheader("Lift % by segment")
    lift_df = pd.DataFrame([
        {"segment": t.get("segment_label", t.get("segment_name", "")), "lift_pct": t.get("lift_pct", 0)}
        for t in AB_TESTS
    ]).set_index("segment")
    st.bar_chart(lift_df[["lift_pct"]])



# ────────────────────────────────────────────────────────────────────────────────
# KPIs — conversion rate (5.4%), avg time to convert (6.2 days), 30-day retention (83%)
# ────────────────────────────────────────────────────────────────────────────────
elif page == "KPIs":
    st.title("KPIs")
    st.caption("Platform-level conversion metrics")

    # 3 big metric cards (row 1)
    k1, k2, k3 = st.columns(3)
    k1.metric(
        "Overall conversion rate",
        f"{KPIS['overall_conversion_rate']*100:.1f}%",
        delta="+2.1% vs baseline",
    )
    k2.metric(
        "Avg time to convert",
        f"{KPIS['avg_time_to_convert_days']} days",
        delta="-3.8 days vs control",
    )
    k3.metric(
        "30-day retention",
        f"{KPIS['retention_30d']*100:.0f}%",
        delta="Target: 80%",
    )

    # Row 2
    k4, k5, k6 = st.columns(3)
    k4.metric(
        "Notification engagement",
        f"{KPIS['notification_engagement_rate']*100:.1f}%",
        delta="+6.1% vs control",
    )
    k5.metric("New paid users", KPIS["new_paid_users"], delta="14-day window")
    k6.metric(
        "Opt-out rate",
        f"{KPIS['opt_out_rate']*100:.1f}%",
        delta="No increase",
        delta_color="off",
    )

    st.divider()

    # Results summary table from A/B tests
    st.subheader("A/B results summary")
    summary_rows = []
    for t in AB_TESTS:
        summary_rows.append({
            "Segment":       t.get("segment_label", t.get("segment_name", "").title()),
            "Control rate":  f"{t['control_rate']*100:.1f}%"   if t.get("control_rate")   else "—",
            "Treatment rate":f"{t['treatment_rate']*100:.1f}%" if t.get("treatment_rate") else "—",
            "Lift %":        f"+{t['lift_pct']:.0f}%"          if t.get("lift_pct")       else "—",
            "Significance":  t.get("significance", "pending").title(),
        })
    st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)

    st.divider()

    # Top conversion predictors bar chart
    st.subheader("Top conversion predictors")
    pred_df = pd.DataFrame({
        "Feature":     ["Paywall hits", "Export count", "Session freq", "Days inactive"],
        "Coefficient": [0.91, 0.74, 0.58, 0.38],
    }).set_index("Feature")
    st.bar_chart(pred_df[["Coefficient"]])



# ────────────────────────────────────────────────────────────────────────────────
# CAMPAIGN EDITOR — campaign list, message text editor, launch button, global params
# ────────────────────────────────────────────────────────────────────────────────
elif page == "Campaign Editor":
    st.title("Campaign Editor")
    st.caption("Edit messages, set channels and triggers, launch A/B tests")

    # Global parameters
    with st.expander("Global parameters", expanded=True):
        gp1, gp2, gp3 = st.columns(3)
        price_val = gp1.number_input(
            "Pro price (AMD)", value=GLOBAL_PARAMS["pro_price_amd"], step=100, key="g_price"
        )
        disc_val = gp2.number_input(
            "Discount % (dormant)", value=GLOBAL_PARAMS["dormant_discount"], step=1, key="g_disc"
        )
        tmpl_val = gp3.number_input(
            "Template count", value=GLOBAL_PARAMS["template_count"], step=10, key="g_tmpl"
        )
        if st.button("Save global params"):
            st.success("Global params saved (mock — no API in M3)")

    st.divider()

    # Campaign list with message text editor + launch button
    st.subheader("Campaigns")
    for i in range(0, len(CAMPAIGNS), 2):
        row = CAMPAIGNS[i: i + 2]
        cols = st.columns(len(row))
        for col, c in zip(cols, row):
            cid    = c["campaign_id"]
            seg    = c.get("segment_label", c.get("segment_name", "").title())
            status = c.get("status", "draft")
            ch     = c.get("channel", "").replace("_", " ").title()
            trig   = c.get("trigger_event", "").replace("_", " ").title()
            body   = c.get("active_message", {}).get("body", "")
            with col:
                st.markdown(f"**{seg}** · `{status}`")
                st.caption(f"{ch} · {trig}")
                new_body = st.text_area(
                    "Message template", value=body, height=90,
                    key=f"body_{cid}", label_visibility="collapsed"
                )
                # Live preview
                preview = (
                    new_body
                    .replace("{{price}}", str(int(price_val)))
                    .replace("{{discount}}", str(int(disc_val)))
                    .replace("{{template_count}}", str(int(tmpl_val)))
                    .replace("{{export_count}}", "9")
                    .replace("{{paywall_hits}}", "7")
                )
                st.info(preview)
                ba, bb = st.columns(2)
                if ba.button("Save message", key=f"save_{cid}", use_container_width=True):
                    st.success("Saved (mock)")
                if status == "draft":
                    if bb.button("Launch A/B test", key=f"launch_{cid}",
                                 use_container_width=True, type="primary"):
                        st.success(f"{seg} launched (mock)")
                else:
                    if bb.button("Reset to draft", key=f"reset_{cid}", use_container_width=True):
                        st.success(f"{seg} reset (mock)")



# ────────────────────────────────────────────────────────────────────────────────
# USER DEMO — segment selector, upgrade message display, accept/dismiss buttons
# ────────────────────────────────────────────────────────────────────────────────
elif page == "User Demo":
    st.title("User Demo")
    st.caption("Simulate a user seeing the upgrade message and record their response")

    # Session-state counters
    if "upgraded_count" not in st.session_state:
        st.session_state.upgraded_count = 0
        st.session_state.later_count    = 0
        st.session_state.demo_log       = []

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.subheader("Simulation controls")

        # Segment selector
        seg_choice = st.selectbox(
            "Simulated segment",
            ["power", "growing", "casual", "dormant"],
            format_func=lambda x: x.title() + " user",
        )
        group_choice = st.selectbox(
            "A/B group",
            ["treatment", "control"],
            format_func=lambda x: "Treatment — targeted message" if x == "treatment"
                                   else "Control — generic message",
        )

        # Upgrade message display
        msg = DEFAULT_MSGS.get(seg_choice, "")
        st.info(msg)

        # Accept / dismiss buttons
        ba, bb = st.columns(2)
        upgraded = ba.button("Upgrade ⬆", use_container_width=True, type="primary")
        later    = bb.button("Try Later", use_container_width=True)

        if upgraded:
            st.session_state.upgraded_count += 1
            st.session_state.demo_log.insert(
                0, {"seg": seg_choice, "group": group_choice, "decision": "upgraded"}
            )
            st.rerun()

        if later:
            st.session_state.later_count += 1
            st.session_state.demo_log.insert(
                0, {"seg": seg_choice, "group": group_choice, "decision": "try_later"}
            )
            st.rerun()

        st.divider()
        m1, m2 = st.columns(2)
        m1.metric("Upgraded",  st.session_state.upgraded_count)
        m2.metric("Try Later", st.session_state.later_count)

        if st.button("Clear log", use_container_width=True):
            st.session_state.upgraded_count = 0
            st.session_state.later_count    = 0
            st.session_state.demo_log       = []
            st.rerun()

    with col_right:
        st.subheader("Response log")
        if st.session_state.demo_log:
            log_df = pd.DataFrame(st.session_state.demo_log[:20]).rename(columns={
                "seg": "Segment", "group": "A/B group", "decision": "Decision"
            })
            st.dataframe(log_df, use_container_width=True, hide_index=True)
        else:
            st.caption("No responses yet — click Upgrade or Try Later.")
