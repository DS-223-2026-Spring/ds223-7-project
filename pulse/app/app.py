"""Pulse Dashboard — Streamlit frontend (Milestone 3: mock data with API fallback).

Screens match PM endpoint specs from issues #67 and #68:
  Segments   — /api/segments/counts + /api/segments/behavioral-averages
  A/B Tests  — /api/ab-tests/summary + /api/ab-tests/comparison
  KPIs       — /api/kpis
  Campaign   — /api/campaigns/* + /api/global-params/*
  User Demo  — /api/demo/message/{segment_name} + /api/demo/respond

Issue #91: each screen has data tables, filters, charts, forms, and model results.
"""
import os

import requests
import streamlit as st
import pandas as pd

# FIX 1: API infrastructure
API = os.getenv("API_URL", "http://back:8000")


def api_get(path: str, **params):
    """GET from the backend API. Returns parsed JSON or None on error."""
    try:
        r = requests.get(f"{API}{path}", params=params, timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


def api_post(path: str, payload: dict):
    """POST to the backend API. Returns parsed JSON or None on error."""
    try:
        r = requests.post(f"{API}{path}", json=payload, timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


def api_put(path: str, payload: dict):
    """PUT to the backend API. Returns parsed JSON or None on error."""
    try:
        r = requests.put(f"{API}{path}", json=payload, timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


st.set_page_config(page_title="Pulse", layout="wide")

# ── Mock data ────────────────────────────────────────────────────────────────────
# Field names match real API shapes; falls back to these when backend unavailable.

# FIX 2a: /api/segments/counts — add missing label and color_hex fields
SEGMENT_COUNTS = [
    {"segment_name": "power",   "label": "Power Users",   "color_hex": "#00b87a", "user_count": 312},
    {"segment_name": "growing", "label": "Growing Users",  "color_hex": "#3b82f6", "user_count": 891},
    {"segment_name": "casual",  "label": "Casual Users",   "color_hex": "#f59e0b", "user_count": 1847},
    {"segment_name": "dormant", "label": "Dormant Users",  "color_hex": "#9ca3af", "user_count": 1370},
]

# /api/segments/behavioral-averages
SEGMENT_BEHAVIORAL = [
    {"segment_name": "power",   "avg_sessions_per_week": 8.4, "avg_exports": 9.2, "avg_paywall_hits": 6.8},
    {"segment_name": "growing", "avg_sessions_per_week": 5.1, "avg_exports": 4.3, "avg_paywall_hits": 2.1},
    {"segment_name": "casual",  "avg_sessions_per_week": 2.3, "avg_exports": 1.8, "avg_paywall_hits": 0.6},
    {"segment_name": "dormant", "avg_sessions_per_week": 0.4, "avg_exports": 0.2, "avg_paywall_hits": 0.0},
]

# FIX 2b: /api/ab-tests/summary — fix "not significant" → "not_significant"
AB_SUMMARY = [
    {"segment_name": "power",   "control_rate": 0.062, "treatment_rate": 0.091, "lift_pct": 46.8, "p_value": 0.012, "significance": "significant",     "status": "running"},
    {"segment_name": "growing", "control_rate": 0.041, "treatment_rate": 0.057, "lift_pct": 39.0, "p_value": 0.034, "significance": "significant",     "status": "running"},
    {"segment_name": "casual",  "control_rate": 0.018, "treatment_rate": 0.022, "lift_pct": 22.2, "p_value": 0.210, "significance": "not_significant", "status": "running"},
    {"segment_name": "dormant", "control_rate": 0.005, "treatment_rate": 0.006, "lift_pct": 20.0, "p_value": 0.480, "significance": "not_significant", "status": "pending"},
]

# FIX 2c: /api/ab-tests/comparison — remove "variant" field, use SegmentABComparison fields
AB_COMPARISON = [
    {"segment_name": "power",   "label": "Power Users",   "color_hex": "#00b87a", "control_rate": 0.142, "treatment_rate": 0.198, "lift_pct": 39.4, "significance": "significant"},
    {"segment_name": "growing", "label": "Growing Users",  "color_hex": "#3b82f6", "control_rate": 0.089, "treatment_rate": 0.103, "lift_pct": 15.7, "significance": "borderline"},
    {"segment_name": "casual",  "label": "Casual Users",   "color_hex": "#f59e0b", "control_rate": 0.031, "treatment_rate": 0.034, "lift_pct":  9.7, "significance": "not_significant"},
    {"segment_name": "dormant", "label": "Dormant Users",  "color_hex": "#9ca3af", "control_rate": 0.008, "treatment_rate": 0.009, "lift_pct": 12.5, "significance": "not_significant"},
]

# FIX 2d: /api/kpis — fix to match PlatformKPIs schema exactly
KPIS = {
    "overall_conversion_rate":      0.054,
    "notification_engagement_rate": 0.143,
    "churn_rate_30d":               0.012,
    "avg_revenue_amd":              2900.0,
}

# FIX 2e: /api/campaigns — rename "trigger" → "trigger_event"
CAMPAIGNS = [
    {
        "campaign_id": 1, "name": "Power User Upgrade",
        "message": "You're a power user! Unlock unlimited exports with Pro.",
        "channel": "in-app", "trigger_event": "paywall_hit", "status": "active",
        "discount_pct": 20, "test_duration_days": 14,
    },
    {
        "campaign_id": 2, "name": "Growing User Nudge",
        "message": "You're growing fast — go Pro to remove all limits.",
        "channel": "email", "trigger_event": "export_attempt", "status": "draft",
        "discount_pct": 15, "test_duration_days": 14,
    },
    {
        "campaign_id": 3, "name": "Re-engage Dormant",
        "message": "We miss you! Come back and see what's new in Pulse.",
        "channel": "push", "trigger_event": "session_start", "status": "paused",
        "discount_pct": 30, "test_duration_days": 7,
    },
]

# /api/global-params
GLOBAL_PARAMS = {
    "test_duration_days": 14,
    "discount_pct": 20,
    "min_sample_size": 50,
    "significance_threshold": 0.05,
}

# /api/demo/message/{segment_name}
DEMO_MESSAGES = {
    "power":   "You're a power user! Upgrade to Pro for unlimited exports and priority support.",
    "growing": "You're on a roll — go Pro to remove all export limits and unlock advanced filters.",
    "casual":  "Enjoying Pulse? Pro gives you 5x more exports and premium templates.",
    "dormant": "Welcome back! Upgrade to Pro today and get 30% off for the next 48 hours.",
}

# FIX 2f: /api/demo/respond — fix "accept"→"upgraded", "dismiss"→"try_later"
DEMO_RESPONSES = [
    {"segment_name": "power",   "response": "upgraded",   "count": 38},
    {"segment_name": "power",   "response": "try_later",  "count": 24},
    {"segment_name": "growing", "response": "upgraded",   "count": 29},
    {"segment_name": "growing", "response": "try_later",  "count": 41},
    {"segment_name": "casual",  "response": "upgraded",   "count": 11},
    {"segment_name": "casual",  "response": "try_later",  "count": 52},
    {"segment_name": "dormant", "response": "upgraded",   "count":  3},
    {"segment_name": "dormant", "response": "try_later",  "count": 18},
]

# ── Sidebar navigation ────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("Pulse")
    st.caption("Analytics Dashboard")
    st.divider()
    page = st.radio(
        "Navigate",
        ["Segments", "A/B Tests", "KPIs", "Campaign Editor", "User Demo"],
        label_visibility="collapsed",
    )
    st.divider()
    st.caption("Milestone 3 — API with mock fallback")

# ────────────────────────────────────────────────────────────────────────────────
#  SEGMENTS  —  /api/segments/counts  +  /api/segments/behavioral-averages
# ────────────────────────────────────────────────────────────────────────────────
if page == "Segments":
    st.title("Segments")
    st.caption("Free-user behavioural clustering — 4 segments")

    # FIX 8: wire real API calls with mock fallback
    raw_counts = api_get("/api/segments/counts")
    segments = raw_counts if raw_counts else SEGMENT_COUNTS
    if raw_counts is None:
        st.caption("⚠️ Using demo data — backend unavailable")

    raw_beh = api_get("/api/segments/behavioral-averages")
    behavioral = raw_beh if raw_beh else SEGMENT_BEHAVIORAL
    if raw_beh is None:
        st.caption("⚠️ Behavioral data — backend unavailable")

    # Filter bar
    all_seg_names = [s["segment_name"].title() for s in segments]
    seg_filter_options = st.multiselect(
        "Filter segments",
        options=all_seg_names,
        default=all_seg_names,
        key="seg_multi_filter",
    )
    if not seg_filter_options:
        seg_filter_options = all_seg_names  # show all if nothing selected

    # Section 1: User counts per segment  (/api/segments/counts)
    st.subheader("User Counts by Segment")
    df_counts = pd.DataFrame(segments)
    df_counts["segment_name"] = df_counts["segment_name"].str.title()
    df_counts = df_counts[df_counts["segment_name"].isin(seg_filter_options)]
    cols = st.columns(len(df_counts) if len(df_counts) > 0 else 1)
    for i, (_, row) in enumerate(df_counts.iterrows()):
        cols[i].metric(row["segment_name"], f'{row["user_count"]:,} users')
    if not df_counts.empty:
        st.bar_chart(df_counts.set_index("segment_name")["user_count"])
    st.divider()

    # Section 2: Behavioral averages  (/api/segments/behavioral-averages)
    st.subheader("Behavioral Averages by Segment")
    df_beh = pd.DataFrame(behavioral)
    df_beh["segment_name"] = df_beh["segment_name"].str.title()
    df_beh = df_beh[df_beh["segment_name"].isin(seg_filter_options)]
    st.dataframe(
        df_beh.rename(columns={
            "segment_name":          "Segment",
            "avg_sessions_per_week": "Avg Sessions / Week",
            "avg_exports":           "Avg Exports",
            "avg_paywall_hits":      "Avg Paywall Hits",
        }),
        use_container_width=True,
        hide_index=True,
    )
    if not df_beh.empty:
        c1, c2, c3 = st.columns(3)
        c1.bar_chart(df_beh.set_index("segment_name")["avg_sessions_per_week"])
        c1.caption("Avg Sessions / Week")
        c2.bar_chart(df_beh.set_index("segment_name")["avg_exports"])
        c2.caption("Avg Exports")
        c3.bar_chart(df_beh.set_index("segment_name")["avg_paywall_hits"])
        c3.caption("Avg Paywall Hits")

# ────────────────────────────────────────────────────────────────────────────────
#  A/B TESTS  —  /api/ab-tests/summary  +  /api/ab-tests/comparison
# ────────────────────────────────────────────────────────────────────────────────
elif page == "A/B Tests":
    st.title("A/B Tests")
    st.caption("Control vs. treatment conversion performance per segment")

    # FIX 8: wire real API calls with mock fallback
    raw_summary = api_get("/api/ab-tests/summary")
    ab_summary = raw_summary if raw_summary else AB_SUMMARY
    if raw_summary is None:
        st.caption("⚠️ Using demo data — backend unavailable")

    raw_cmp = api_get("/api/ab-tests/comparison")
    ab_comparison = raw_cmp if raw_cmp else AB_COMPARISON
    if raw_cmp is None:
        st.caption("⚠️ Comparison data — backend unavailable")

    tab_summary, tab_comparison = st.tabs(["Summary", "Variant Comparison"])

    # Tab 1: Summary  (/api/ab-tests/summary)
    with tab_summary:
        st.subheader("Test Summary — model results")

        # Filter bar
        f1, f2 = st.columns([1, 1])
        sig_filter = f1.selectbox(
            "Filter by significance",
            ["All", "Significant", "Borderline", "Not significant"],
            key="ab_sig_filter",
        )
        status_filter = f2.selectbox(
            "Filter by status",
            ["All", "running", "pending", "complete"],
            key="ab_status_filter",
        )

        df_sum = pd.DataFrame(ab_summary)
        # FIX 3: significance filter comparisons use underscored values
        if sig_filter == "Significant":
            df_sum = df_sum[df_sum["significance"] == "significant"]
        elif sig_filter == "Borderline":
            df_sum = df_sum[df_sum["significance"] == "borderline"]
        elif sig_filter == "Not significant":
            df_sum = df_sum[df_sum["significance"] == "not_significant"]
        if status_filter != "All":
            df_sum = df_sum[df_sum["status"] == status_filter]

        running = df_sum[df_sum["status"] == "running"].shape[0]
        sig     = df_sum[df_sum["significance"] == "significant"].shape[0]
        m1, m2, m3 = st.columns(3)
        m1.metric("Tests in view", len(df_sum))
        m2.metric("Significant results", sig)
        m3.metric("Tests running", running)
        st.divider()

        # Comparison table with lift and p-value columns
        if not df_sum.empty:
            display_cols = {
                "segment_name":   "Segment",
                "control_rate":   "Control Rate",
                "treatment_rate": "Treatment Rate",
                "lift_pct":       "Lift %",
                "significance":   "Significance",
                "status":         "Status",
            }
            # p_value may not be present in all API responses
            if "p_value" in df_sum.columns:
                display_cols["p_value"] = "p-value"
            df_display = df_sum[[c for c in display_cols if c in df_sum.columns]].rename(columns=display_cols)
            if "Control Rate" in df_display.columns:
                df_display["Control Rate"] = df_display["Control Rate"].map(lambda x: f"{x:.1%}" if x is not None else "—")
            if "Treatment Rate" in df_display.columns:
                df_display["Treatment Rate"] = df_display["Treatment Rate"].map(lambda x: f"{x:.1%}" if x is not None else "—")
            if "Lift %" in df_display.columns:
                df_display["Lift %"] = df_display["Lift %"].map(lambda x: f"+{x:.1f}%" if x is not None else "—")
            st.dataframe(df_display, use_container_width=True, hide_index=True)
        else:
            st.info("No results match the selected filters.")

    # Tab 2: Variant Comparison  (/api/ab-tests/comparison)
    with tab_comparison:
        st.subheader("Side-by-Side Variant Comparison")
        seg_filter = st.selectbox(
            "Filter by segment",
            ["All"] + [s["segment_name"].title() for s in SEGMENT_COUNTS],
            key="ab_seg_filter",
        )
        df_cmp = pd.DataFrame(ab_comparison)
        df_cmp["segment_name"] = df_cmp["segment_name"].str.title()
        if seg_filter != "All":
            df_cmp = df_cmp[df_cmp["segment_name"] == seg_filter]
        st.dataframe(
            df_cmp.rename(columns={
                "segment_name":    "Segment",
                "label":           "Label",
                "control_rate":    "Control Rate",
                "treatment_rate":  "Treatment Rate",
                "lift_pct":        "Lift %",
                "significance":    "Significance",
            }).assign(**{
                "Control Rate":   lambda d: d["Control Rate"].map(lambda x: f"{x:.1%}" if x is not None else "—"),
                "Treatment Rate": lambda d: d["Treatment Rate"].map(lambda x: f"{x:.1%}" if x is not None else "—"),
            }),
            use_container_width=True,
            hide_index=True,
        )
        st.caption("Data from /api/ab-tests/comparison")

# ────────────────────────────────────────────────────────────────────────────────
#  KPIs  —  /api/kpis
# ────────────────────────────────────────────────────────────────────────────────
elif page == "KPIs":
    st.title("KPIs")
    st.caption("Platform-level conversion and retention metrics")

    # Period filter
    kpi_period = st.radio(
        "Reporting period",
        ["Last 7 days", "Last 30 days", "Last 90 days"],
        index=1,
        horizontal=True,
        key="kpi_period",
    )
    st.caption(f"Period selector wires to /api/kpis?period=... in M4")
    st.divider()

    # FIX 8: wire real API call with mock fallback
    raw_kpis = api_get("/api/kpis")
    kpis = raw_kpis if raw_kpis else KPIS
    if raw_kpis is None:
        st.caption("⚠️ Using demo data — backend unavailable")

    # FIX 5: use real PlatformKPIs field names
    k1, k2, k3 = st.columns(3)
    k1.metric(
        "Overall Conversion Rate",
        f'{kpis["overall_conversion_rate"]:.1%}' if kpis.get("overall_conversion_rate") is not None else "—",
        delta="+1.1% vs last period",
    )
    k2.metric(
        "Churn Rate 30d",
        f'{kpis["churn_rate_30d"]:.1%}' if kpis.get("churn_rate_30d") is not None else "—",
        delta="-0.1% vs last period",
    )
    k3.metric(
        "Avg Revenue (AMD)",
        f'{kpis["avg_revenue_amd"]:,.0f}' if kpis.get("avg_revenue_amd") is not None else "—",
        delta="+50 AMD vs last period",
    )
    st.divider()

    # 4th metric: notification engagement
    k4, _, _ = st.columns(3)
    k4.metric(
        "Notification Engagement Rate",
        f'{kpis["notification_engagement_rate"]:.0%}' if kpis.get("notification_engagement_rate") is not None else "—",
        delta="+4% vs last period",
    )
    st.caption("Data from /api/kpis")

# ────────────────────────────────────────────────────────────────────────────────
#  CAMPAIGN EDITOR  —  /api/campaigns/*  +  /api/global-params/*
# ────────────────────────────────────────────────────────────────────────────────
elif page == "Campaign Editor":
    st.title("Campaign Editor")
    st.caption("Manage upgrade campaigns and global test parameters")

    # FIX 8: wire real API call with mock fallback
    raw_campaigns = api_get("/api/campaigns")
    campaigns_data = raw_campaigns if raw_campaigns else CAMPAIGNS
    if raw_campaigns is None:
        st.caption("⚠️ Using demo data — backend unavailable")

    # FIX 6: sorted status options for deterministic ordering
    status_options = ["All"] + sorted({c["status"] for c in campaigns_data})
    camp_status_filter = st.selectbox(
        "Filter campaigns by status",
        status_options,
        key="camp_list_filter",
    )
    filtered_campaigns = campaigns_data if camp_status_filter == "All" else [
        c for c in campaigns_data if c["status"] == camp_status_filter
    ]

    left_col, right_col = st.columns([1, 2])

    with left_col:
        st.subheader("Campaigns")
        if not filtered_campaigns:
            st.info("No campaigns match the selected filter.")
            selected_c = campaigns_data[0]
        else:
            campaign_names = [f'#{c["campaign_id"]} — {c["name"]}' for c in filtered_campaigns]
            selected_idx = st.selectbox(
                "Select campaign",
                range(len(filtered_campaigns)),
                format_func=lambda i: campaign_names[i],
                key="campaign_select",
            )
            selected_c = filtered_campaigns[selected_idx]

        c = selected_c
        st.write(f"**Channel:** {c['channel'].upper()}")
        # FIX 2e: read trigger_event not trigger
        st.write(f"**Trigger:** {c.get('trigger_event', '—')}")
        status_color = {"active": "✅", "draft": "⚪", "paused": "⏸️"}
        st.write(f"**Status:** {status_color.get(c['status'], '•')} {c['status'].title()}")

    with right_col:
        st.subheader("Edit Campaign")
        new_name = st.text_input("Campaign name", value=c["name"], key="camp_name")
        # message body may come from active_message.body when real API is used
        msg_value = c.get("message") or (c.get("active_message") or {}).get("body", "")
        new_msg  = st.text_area(
            "Message template",
            value=msg_value,
            height=100,
            key="camp_msg",
            help="Will call PUT /api/campaigns/{id}/message in M4.",
        )
        ch1, ch2 = st.columns(2)

        # FIX 4: safe .index() with fallback to prevent ValueError crash
        channel_options = ["in-app", "email", "push"]
        channel_idx = channel_options.index(c.get("channel", "in-app")) if c.get("channel") in channel_options else 0
        new_channel = ch1.selectbox(
            "Channel",
            channel_options,
            index=channel_idx,
            key="camp_channel",
        )

        # FIX 4: use trigger_event, safe fallback
        trigger_options = ["paywall_hit", "export_attempt", "session_start"]
        trigger_idx = trigger_options.index(c.get("trigger_event", "paywall_hit")) if c.get("trigger_event") in trigger_options else 0
        new_trigger = ch2.selectbox(
            "Trigger",
            trigger_options,
            index=trigger_idx,
            key="camp_trigger",
        )
        d1, d2 = st.columns(2)
        d1.number_input("Discount %",           min_value=0,  max_value=100, value=c.get("discount_pct", 20),       key="camp_discount")
        d2.number_input("Test duration (days)", min_value=1,  max_value=90,  value=c.get("test_duration_days", 14), key="camp_duration")
        st.divider()
        b1, b2, b3 = st.columns(3)
        if b1.button("🚀 Launch campaign", key="btn_launch", type="primary"):
            result = api_post(f"/api/campaigns/{c['campaign_id']}/launch", {})
            if result:
                st.success(f"Campaign \"{new_name}\" launched.")
            else:
                st.success(f"Campaign \"{new_name}\" launched (demo mode — backend unavailable).")
        if b2.button("💾 Save changes", key="btn_save"):
            result = api_put(f"/api/campaigns/{c['campaign_id']}", {"channel": new_channel, "trigger_event": new_trigger})
            if result:
                st.info("Changes saved.")
            else:
                st.info("Changes saved (demo mode — backend unavailable).")
        if b3.button("↩ Reset to draft", key="btn_reset"):
            result = api_post(f"/api/campaigns/{c['campaign_id']}/reset", {})
            if result:
                st.warning("Campaign reset to draft.")
            else:
                st.warning("Campaign reset (demo mode — backend unavailable).")

    st.divider()
    st.subheader("Global Parameters")
    st.caption("Shared defaults applied to all campaigns unless overridden")
    gp1, gp2, gp3, gp4 = st.columns(4)
    gp1.number_input("Test Duration (days)",    value=GLOBAL_PARAMS["test_duration_days"],     min_value=1,  max_value=90,  key="gp_dur")
    gp2.number_input("Discount %",              value=GLOBAL_PARAMS["discount_pct"],           min_value=0,  max_value=100, key="gp_disc")
    gp3.number_input("Min Sample Size",         value=GLOBAL_PARAMS["min_sample_size"],        min_value=10,               key="gp_sample")
    gp4.number_input("Significance Threshold",  value=GLOBAL_PARAMS["significance_threshold"], min_value=0.0, max_value=1.0, step=0.01, key="gp_sig")
    if st.button("Save global params", key="btn_gp_save"):
        result = api_put("/api/global-params/significance_threshold", {"value": str(GLOBAL_PARAMS["significance_threshold"])})
        if result:
            st.success("Global params saved.")
        else:
            st.success("Global params saved (demo mode — backend unavailable).")

# ────────────────────────────────────────────────────────────────────────────────
#  USER DEMO  —  /api/demo/message/{segment_name}  +  /api/demo/respond
# ────────────────────────────────────────────────────────────────────────────────
elif page == "User Demo":
    st.title("User Demo")
    st.caption("Simulate how an upgrade message looks to a user by segment")

    demo_col, stats_col = st.columns([1, 1])

    with demo_col:
        # Segment selector  (/api/demo/message/{segment_name})
        seg = st.selectbox(
            "Select segment",
            [s["segment_name"] for s in SEGMENT_COUNTS],
            format_func=lambda x: x.title(),
            key="demo_seg",
        )

        # FIX 7: ab_group selector
        ab_group = st.radio(
            "Group",
            ["control", "treatment"],
            horizontal=True,
            label_visibility="collapsed",
        )

        st.divider()
        st.subheader("Upgrade Message")

        # FIX 8: wire real API call with mock fallback
        raw_demo = api_get(f"/api/demo/user", segment=seg)
        if raw_demo:
            msg = raw_demo.get("rendered_body") or raw_demo.get("message") or DEMO_MESSAGES.get(seg, "")
            user_id = raw_demo.get("user_id")
        else:
            msg = DEMO_MESSAGES.get(seg, "")
            user_id = None
            st.caption("⚠️ Using demo data — backend unavailable")

        st.info(msg)
        st.caption(f"Source: GET /api/demo/message/{seg}")
        st.divider()

        # FIX 2f: decision values "upgraded" and "try_later"
        st.write("**How would this user respond?**")
        a_col, d_col = st.columns(2)
        if a_col.button("✅ Accept upgrade", key="btn_accept", type="primary"):
            payload = {"segment_name": seg, "decision": "upgraded", "ab_group": ab_group}
            if user_id:
                payload["user_id"] = user_id
            result = api_post("/api/demo/respond", payload)
            if result:
                st.success("Response recorded.")
            else:
                st.info("Recorded (demo mode — backend unavailable).")
        if d_col.button("❌ Dismiss", key="btn_dismiss"):
            payload = {"segment_name": seg, "decision": "try_later", "ab_group": ab_group}
            if user_id:
                payload["user_id"] = user_id
            result = api_post("/api/demo/respond", payload)
            if result:
                st.success("Response recorded.")
            else:
                st.info("Recorded (demo mode — backend unavailable).")

    with stats_col:
        # Response stats  (aggregated from /api/demo/respond)
        st.subheader("Response Stats by Segment")
        df_resp = pd.DataFrame(DEMO_RESPONSES)
        df_pivot = df_resp.pivot(index="segment_name", columns="response", values="count").fillna(0).astype(int)
        df_pivot.index = df_pivot.index.str.title()
        df_pivot.columns = [col.title() for col in df_pivot.columns]
        df_pivot["Total"] = df_pivot.sum(axis=1)
        if "Upgraded" in df_pivot.columns:
            df_pivot["Upgrade Rate"] = (df_pivot["Upgraded"] / df_pivot["Total"]).map(lambda x: f"{x:.0%}")
        st.dataframe(df_pivot, use_container_width=True)
        st.caption("Aggregated responses from /api/demo/respond")
        if "Upgraded" in df_pivot.columns:
            st.bar_chart(
                df_resp[df_resp["response"] == "upgraded"].set_index("segment_name")["count"]
            )
            st.caption("Upgrade counts by segment")
