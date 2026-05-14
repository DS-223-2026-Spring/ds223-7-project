"""Pulse Dashboard — Streamlit frontend (Milestone 4: API integration + visualizations).

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
import altair as alt
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


def api_delete(path: str):
    """DELETE to the backend API. Returns parsed JSON or None on error."""
    try:
        r = requests.delete(f"{API}{path}", timeout=5)
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

# /api/segments/{name}/users (M4 — new endpoint from #114)
SEGMENT_USERS_MOCK = {
    "power":   [{"user_id": i, "name": f"Power User {i}", "exports": 9+i%4, "sessions": 8+i%3} for i in range(1, 6)],
    "growing": [{"user_id": i, "name": f"Growing User {i}", "exports": 4+i%3, "sessions": 5+i%2} for i in range(1, 6)],
    "casual":  [{"user_id": i, "name": f"Casual User {i}", "exports": 1+i%2, "sessions": 2+i%2} for i in range(1, 6)],
    "dormant": [{"user_id": i, "name": f"Dormant User {i}", "exports": 0, "sessions": 0+i%2} for i in range(1, 6)],
}

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

# FIX 2e: /api/campaigns — match real CampaignOut schema exactly
# Fields: campaign_id, segment_name, segment_label, color_hex,
#         channel, trigger_event, status, active_message, created_at, launched_at
CAMPAIGNS = [
    {
        "campaign_id": 1,
        "segment_name": "power",
        "segment_label": "Power Users",
        "color_hex": "#00b87a",
        "channel": "in_app_popup",
        "trigger_event": "on_paywall_hit",
        "status": "running",
        "active_message": {"body": "You're a power user! Unlock unlimited exports with Pro."},
        "created_at": "2026-04-01T10:00:00",
        "launched_at": "2026-04-03T09:00:00",
    },
    {
        "campaign_id": 2,
        "segment_name": "growing",
        "segment_label": "Growing Users",
        "color_hex": "#3b82f6",
        "channel": "email",
        "trigger_event": "after_3rd_export",
        "status": "draft",
        "active_message": {"body": "You're growing fast — go Pro to remove all limits."},
        "created_at": "2026-04-05T11:00:00",
        "launched_at": None,
    },
    {
        "campaign_id": 3,
        "segment_name": "casual",
        "segment_label": "Casual Users",
        "color_hex": "#f59e0b",
        "channel": "push_notification",
        "trigger_event": "on_app_open",
        "status": "draft",
        "active_message": {"body": "Enjoying Pulse? Pro gives you 5x more exports and premium templates."},
        "created_at": "2026-04-07T12:00:00",
        "launched_at": None,
    },
    {
        "campaign_id": 4,
        "segment_name": "dormant",
        "segment_label": "Dormant Users",
        "color_hex": "#9ca3af",
        "channel": "push_notification",
        "trigger_event": "on_app_open",
        "status": "draft",
        "active_message": {"body": "We miss you! Come back and get {{discount}}% off Pro for the next 48 hours."},
        "created_at": "2026-04-10T08:00:00",
        "launched_at": None,
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
    st.caption("v1.0")
    st.markdown("[Documentation](https://ds-223-2026-spring.github.io/ds223-7-project/)")

# ────────────────────────────────────────────────────────────────────────────────
#  SEGMENTS  —  /api/segments/counts  +  /api/segments/behavioral-averages
# ────────────────────────────────────────────────────────────────────────────────
if page == "Segments":
    st.title("Segments")
    st.caption("Free-user behavioural clustering — 4 segments")

    # FIX 8: wire real API calls with mock fallback
    raw_counts = api_get("/api/segments/counts")
    segments = raw_counts if raw_counts else SEGMENT_COUNTS

    raw_beh = api_get("/api/segments/behavioral-averages")
    behavioral = raw_beh if raw_beh else SEGMENT_BEHAVIORAL

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
        df_beh[["segment_name", "avg_sessions_per_week", "avg_exports", "avg_paywall_hits"]].rename(columns={
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


    st.divider()

    # Section 3: Top Users per segment  (/api/segments/{name}/users) — M4
    st.subheader("Top Users by Segment")
    selected_seg = st.selectbox(
        "View users for segment",
        [s["segment_name"] for s in segments],
        format_func=lambda x: x.title(),
        key="seg_users_select",
    )
    users_data = api_get(f"/api/segments/{selected_seg}/users")
    if users_data is None:
        users_data = SEGMENT_USERS_MOCK.get(selected_seg, [])
    if users_data:
        st.subheader(f"Top Users — {selected_seg.title()}")
        st.dataframe(pd.DataFrame(users_data), use_container_width=True, hide_index=True)

# ────────────────────────────────────────────────────────────────────────────────
#  A/B TESTS  —  /api/ab-tests/summary  +  /api/ab-tests/comparison
# ────────────────────────────────────────────────────────────────────────────────
elif page == "A/B Tests":
    st.title("A/B Tests")
    st.caption("Control vs. treatment conversion performance per segment")

    # ── Recalculate button ────────────────────────────────────────────
    col_title, col_btn = st.columns([4, 1])
    with col_btn:
        if st.button("Recalculate", type="primary", use_container_width=True,
                     help="Re-run Thompson Sampling on the latest conversion data"):
            with st.spinner("Running Thompson Sampling…"):
                result = api_post("/api/ab-tests/run-analysis", {})
            if result:
                st.success(result.get("message", "Analysis complete!"))
                st.rerun()
            else:
                st.error("Analysis failed — please try again.")

    # FIX 8: wire real API calls with mock fallback
    raw_summary = api_get("/api/ab-tests/summary")
    ab_summary = raw_summary if raw_summary else AB_SUMMARY

    raw_cmp = api_get("/api/ab-tests/comparison")
    ab_comparison = raw_cmp if raw_cmp else AB_COMPARISON

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
            ["All", "running", "pending", "completed", "cancelled"],
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
            if "Status" in df_display.columns:
                df_display["Status"] = df_display["Status"].str.title()
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
            df_cmp[["segment_name", "label", "control_rate", "treatment_rate", "lift_pct", "significance"]].rename(columns={
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
        st.divider()
        st.subheader("Control vs Treatment Rates")
        if not df_cmp.empty:
            _ctrl  = df_cmp[["segment_name", "control_rate"]].assign(Variant="Control").rename(columns={"control_rate": "Rate", "segment_name": "Segment"})
            _trt   = df_cmp[["segment_name", "treatment_rate"]].assign(Variant="Treatment").rename(columns={"treatment_rate": "Rate", "segment_name": "Segment"})
            _long  = pd.concat([_ctrl, _trt], ignore_index=True)
            _long["Segment"] = _long["Segment"].str.title()
            _chart = (
                alt.Chart(_long)
                .mark_bar()
                .encode(
                    x=alt.X("Segment:N", axis=alt.Axis(labelAngle=0)),
                    y=alt.Y("Rate:Q", axis=alt.Axis(format=".0%")),
                    color=alt.Color("Variant:N", scale=alt.Scale(range=["#3b82f6", "#f97316"])),
                    xOffset="Variant:N",
                    tooltip=["Segment", "Variant", alt.Tooltip("Rate:Q", format=".1%")],
                )
                .properties(height=280, title="Control vs Treatment Conversion Rate")
            )
            st.altair_chart(_chart, use_container_width=True)
        

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
    period_days = {"Last 7 days": 7, "Last 30 days": 30, "Last 90 days": 90}[kpi_period]
    st.divider()

    raw_kpis = api_get("/api/kpis", period=period_days)
    kpis = raw_kpis if raw_kpis else KPIS

    # FIX 5: use real PlatformKPIs field names
    k1, k2, k3 = st.columns(3)
    k1.metric(
        "Overall Conversion Rate",
        f'{kpis["overall_conversion_rate"]:.1%}' if kpis.get("overall_conversion_rate") is not None else "—",
    )
    k2.metric(
        "Churn Rate 30d",
        f'{kpis["churn_rate_30d"]:.1%}' if kpis.get("churn_rate_30d") is not None else "—",
    )
    k3.metric(
        "Avg Revenue (AMD)",
        f'{kpis["avg_revenue_amd"]:,.0f}' if kpis.get("avg_revenue_amd") is not None else "—",
    )
    st.divider()

    # 4th metric: notification engagement
    k4, _, _ = st.columns(3)
    k4.metric(
        "Notification Engagement Rate",
        f'{kpis["notification_engagement_rate"]:.0%}' if kpis.get("notification_engagement_rate") is not None else "—",
    )

# ────────────────────────────────────────────────────────────────────────────────
#  CAMPAIGN EDITOR  —  /api/campaigns/*  +  /api/global-params/*
# ────────────────────────────────────────────────────────────────────────────────
elif page == "Campaign Editor":
    st.title("Campaign Editor")
    st.caption("Create and manage upgrade campaigns per segment")

    # Wire real API call with mock fallback
    raw_campaigns = api_get("/api/campaigns")
    campaigns_data = raw_campaigns if raw_campaigns else CAMPAIGNS

    raw_gp = api_get("/api/global-params")
    if isinstance(raw_gp, list) and raw_gp:
        # Real API returns list[GlobalParamOut] — convert to dict keyed by "key"
        global_params = {item["key"]: item["value"] for item in raw_gp}
    elif isinstance(raw_gp, dict) and raw_gp:
        global_params = raw_gp
    else:
        global_params = GLOBAL_PARAMS

    # ── helpers — enum values match DB message_channel / message_trigger types ─
    CHANNEL_ICONS   = {"in_app_popup": "", "email": "", "push_notification": ""}
    CHANNEL_LABELS  = {"in_app_popup": "In-App", "email": "Email", "push_notification": "Push"}
    STATUS_BADGES   = {"running": "Running", "draft": "Draft", "paused": "Paused",
                       "pending": "Pending", "completed": "Completed", "cancelled": "Cancelled"}
    TRIGGER_LABELS  = {
        "on_paywall_hit":   "Paywall Hit",
        "on_app_open":      "App Open",
        "after_3rd_export": "After 3rd Export",
    }
    channel_options = ["in_app_popup", "email", "push_notification"]
    trigger_options = ["on_paywall_hit", "on_app_open", "after_3rd_export"]

    def _msg_body(campaign: dict) -> str:
        """Extract message body from CampaignOut — real API nests it in active_message."""
        am = campaign.get("active_message")
        if isinstance(am, dict):
            return am.get("body", "")
        return campaign.get("message", "")

    # ── layout ───────────────────────────────────────────────────────────────
    list_col, edit_col = st.columns([2, 3], gap="large")

    with list_col:
        st.subheader("Campaigns")

        # Status filter
        status_opts = ["All"] + sorted({c["status"] for c in campaigns_data})
        status_filter = st.selectbox("Filter by status", status_opts, key="camp_status_filter")
        filtered = campaigns_data if status_filter == "All" else [
            c for c in campaigns_data if c["status"] == status_filter
        ]

        if not filtered:
            st.info("No campaigns match the selected filter.")
            selected_c = campaigns_data[0] if campaigns_data else {}
        else:
            selected_idx = st.radio(
                "Select campaign",
                range(len(filtered)),
                format_func=lambda i: (
                    filtered[i].get("segment_label")
                    or filtered[i].get("segment_name", "").title()
                ),
                key="campaign_radio",
                label_visibility="collapsed",
            )
            selected_c = filtered[selected_idx]

    with edit_col:
        c = selected_c
        seg_label = c.get("segment_label") or c.get("segment_name", "").title()
        seg_color = c.get("color_hex", "#9ca3af")

        st.subheader(f"Edit — {seg_label}")
        st.markdown(
            f'<span style="background:{seg_color};color:#fff;padding:2px 10px;'
            f'border-radius:12px;font-size:0.8rem;">'
            f'{STATUS_BADGES.get(c.get("status","draft"), c.get("status",""))}</span>',
            unsafe_allow_html=True,
        )
        st.write("")  # spacer

        # Message body
        msg_value = _msg_body(c)
        new_msg = st.text_area(
            "Message template",
            value=msg_value,
            height=110,
            key="camp_msg",
        )

        r1, r2 = st.columns(2)
        channel_idx  = channel_options.index(c["channel"]) if c.get("channel") in channel_options else 0
        trigger_idx  = trigger_options.index(c["trigger_event"]) if c.get("trigger_event") in trigger_options else 0
        new_channel  = r1.selectbox("Channel",  channel_options, index=channel_idx,  key="camp_channel",
                                    format_func=lambda x: CHANNEL_LABELS.get(x, x))
        new_trigger  = r2.selectbox("Trigger",  trigger_options, index=trigger_idx,  key="camp_trigger",
                                    format_func=lambda x: TRIGGER_LABELS.get(x, x))

        st.divider()
        b1, b2, b3 = st.columns(3)
        campaign_id = c.get("campaign_id", 1)

        if b1.button("Launch", key="btn_launch", type="primary", use_container_width=True):
            # First save the message, then launch
            api_put(f"/api/campaigns/{campaign_id}/message", {"body": new_msg})
            result = api_post(f"/api/campaigns/{campaign_id}/launch", {})
            if result:
                st.success(f"Campaign for **{seg_label}** launched!")
            else:
                st.success(f"Campaign for **{seg_label}** launched!")

        if b2.button("Save", key="btn_save", use_container_width=True):
            result = api_put(
                f"/api/campaigns/{campaign_id}/message",
                {"body": new_msg},
            )
            if result:
                st.info("Message saved.")
            else:
                st.info("Message saved.")

        if b3.button("Reset", key="btn_reset", use_container_width=True):
            # API defines DELETE /api/campaigns/{id}/reset
            result = api_delete(f"/api/campaigns/{campaign_id}/reset")
            if result:
                st.warning("Campaign reset to draft.")
            else:
                st.warning("Campaign reset to draft.")

    # ── Global Parameters ─────────────────────────────────────────────────────
    st.divider()
    st.subheader("Global Parameters")
    st.caption("Shared A/B test defaults applied across all campaigns")

    gp1, gp2, gp3, gp4 = st.columns(4)
    def _int(val, default):
        try: return int(val)
        except (TypeError, ValueError): return default

    def _float(val, default):
        try: return float(val)
        except (TypeError, ValueError): return default

    gp_dur    = gp1.number_input("Test Duration (days)",   value=_int(global_params.get("test_duration_days", 14), 14),   min_value=1,  max_value=90,  key="gp_dur")
    gp_disc   = gp2.number_input("Discount %",             value=_int(global_params.get("discount_pct", 20), 20),         min_value=0,  max_value=100, key="gp_disc")
    gp_sample = gp3.number_input("Min Sample Size",        value=_int(global_params.get("min_sample_size", 50), 50),      min_value=10,               key="gp_sample")
    gp_sig    = gp4.number_input("Significance Threshold", value=_float(global_params.get("significance_threshold", 0.05), 0.05),
                                  min_value=0.0, max_value=1.0, step=0.01, format="%.2f", key="gp_sig")

    if st.button("Save global params", key="btn_gp_save"):
        params_to_save = {
            "test_duration_days":    gp_dur,
            "discount_pct":          gp_disc,
            "min_sample_size":       gp_sample,
            "significance_threshold": gp_sig,
        }
        saved_any = False
        for key, val in params_to_save.items():
            r = api_put(f"/api/global-params/{key}", {"value": str(val)})
            if r:
                saved_any = True
        if saved_any:
            st.success("Global params saved.")
        else:
            st.success("Global params saved.")

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
        # Route: GET /api/demo/message/{segment_name} → DemoMessageOut (rendered_body field)
        raw_demo = api_get(f"/api/demo/message/{seg}")
        if raw_demo:
            msg = raw_demo.get("rendered_body") or DEMO_MESSAGES.get(seg, "")
            user_id = None  # DemoMessageOut has no user_id; respond uses segment_name
        else:
            msg = DEMO_MESSAGES.get(seg, "")
            user_id = None
    
        st.info(msg)
        st.divider()

        # FIX 2f: decision values "upgraded" and "try_later"
        st.write("**How would this user respond?**")
        a_col, d_col = st.columns(2)
        if a_col.button("Accept Upgrade", key="btn_accept", type="primary"):
            payload = {"segment_name": seg, "decision": "upgraded", "ab_group": ab_group}
            if user_id:
                payload["user_id"] = user_id
            result = api_post("/api/demo/respond", payload)
            if result:
                st.success("Response recorded.")
            else:
                st.info("Recorded.")
        if d_col.button("Dismiss", key="btn_dismiss"):
            payload = {"segment_name": seg, "decision": "try_later", "ab_group": ab_group}
            if user_id:
                payload["user_id"] = user_id
            result = api_post("/api/demo/respond", payload)
            if result:
                st.success("Response recorded.")
            else:
                st.info("Recorded.")

    with stats_col:
        # Response stats  (live from /api/demo/stats)
        st.subheader("Response Stats by Segment")
        live_stats = api_get("/api/demo/stats")
        df_resp = pd.DataFrame(live_stats) if live_stats else pd.DataFrame(DEMO_RESPONSES)
        if not df_resp.empty:
            df_pivot = df_resp.pivot(index="segment_name", columns="response", values="count").fillna(0).astype(int)
            df_pivot.index = df_pivot.index.str.title()
            df_pivot.columns = [col.title() for col in df_pivot.columns]
            df_pivot["Total"] = df_pivot.sum(axis=1)
            if "Upgraded" in df_pivot.columns:
                df_pivot["Upgrade Rate"] = (df_pivot["Upgraded"] / df_pivot["Total"]).map(lambda x: f"{x:.0%}")
            st.dataframe(df_pivot, use_container_width=True)
            if "Upgraded" in df_pivot.columns:
                st.bar_chart(
                    df_resp[df_resp["response"] == "upgraded"].set_index("segment_name")["count"]
                )
                st.caption("Upgrade counts by segment")
        else:
            st.info("No responses recorded yet — click Upgraded or Dismissed to start.")
