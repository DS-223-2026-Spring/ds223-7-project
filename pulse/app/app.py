"""Pulse Dashboard ÃÂ¢ÃÂÃÂ Streamlit frontend (Milestone 3: mock data).

Screens match PM endpoint specs from issues #67 and #68:
  Segments   ÃÂ¢ÃÂÃÂ /api/segments/counts + /api/segments/behavioral-averages
  A/B Tests  ÃÂ¢ÃÂÃÂ /api/ab-tests/summary + /api/ab-tests/comparison
  KPIs       ÃÂ¢ÃÂÃÂ /api/kpis
  Campaign   ÃÂ¢ÃÂÃÂ /api/campaigns/* + /api/global-params/*
  User Demo  ÃÂ¢ÃÂÃÂ /api/demo/message/{segment_name} + /api/demo/respond

Issue #91: each screen has data tables, filters, charts, forms, and model results.
"""
import streamlit as st
import pandas as pd
import requests


# Ã¢ÂÂÃ¢ÂÂ API helper Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
BASE_URL = "http://back:8008"

def api_get(path: str):
    """GET helper Ã¢ÂÂ returns parsed JSON or None on error (falls back to mock data)."""
    try:
        r = requests.get(BASE_URL + path, timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None

st.set_page_config(page_title="Pulse", layout="wide")

# ÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂ Mock data ÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂ
# Field names match real API shapes; wiring in M4 is a one-line change.

# /api/segments/counts
SEGMENT_COUNTS = [
    {"segment_name": "power",   "user_count": 124},
    {"segment_name": "growing", "user_count": 158},
    {"segment_name": "casual",  "user_count":  98},
    {"segment_name": "dormant", "user_count":  43},
]

# /api/segments/behavioral-averages
SEGMENT_BEHAVIORAL = [
    {"segment_name": "power",   "avg_sessions_per_week": 8.4, "avg_exports": 9.2, "avg_paywall_hits": 6.8},
    {"segment_name": "growing", "avg_sessions_per_week": 5.1, "avg_exports": 4.3, "avg_paywall_hits": 2.1},
    {"segment_name": "casual",  "avg_sessions_per_week": 2.3, "avg_exports": 1.8, "avg_paywall_hits": 0.6},
    {"segment_name": "dormant", "avg_sessions_per_week": 0.4, "avg_exports": 0.2, "avg_paywall_hits": 0.0},
]

# /api/segments/{name}/users  (mock fallback for M4 until endpoint #114 is ready)
SEGMENT_USERS_MOCK = {
    "power": [
        {"user_id": 1, "email": "alice@example.com", "exports": 14, "sessions": 10, "paywall_hits": 8},
        {"user_id": 2, "email": "bob@example.com",   "exports": 11, "sessions": 9,  "paywall_hits": 7},
        {"user_id": 3, "email": "carol@example.com", "exports": 10, "sessions": 8,  "paywall_hits": 6},
    ],
    "growing": [
        {"user_id": 4, "email": "dave@example.com",  "exports": 6,  "sessions": 6,  "paywall_hits": 3},
        {"user_id": 5, "email": "eve@example.com",   "exports": 5,  "sessions": 5,  "paywall_hits": 2},
        {"user_id": 6, "email": "frank@example.com", "exports": 4,  "sessions": 4,  "paywall_hits": 1},
    ],
    "casual": [
        {"user_id": 7, "email": "grace@example.com", "exports": 2,  "sessions": 2,  "paywall_hits": 1},
        {"user_id": 8, "email": "hank@example.com",  "exports": 1,  "sessions": 2,  "paywall_hits": 0},
    ],
    "dormant": [
        {"user_id": 9,  "email": "ivan@example.com", "exports": 0,  "sessions": 0,  "paywall_hits": 0},
        {"user_id": 10, "email": "judy@example.com", "exports": 0,  "sessions": 1,  "paywall_hits": 0},
    ],
}

# /api/ab-tests/summary
AB_SUMMARY = [
    {"segment_name": "power",   "control_rate": 0.062, "treatment_rate": 0.091, "lift_pct": 46.8, "p_value": 0.012, "significance": "significant",     "status": "running"},
    {"segment_name": "growing", "control_rate": 0.041, "treatment_rate": 0.057, "lift_pct": 39.0, "p_value": 0.034, "significance": "significant",     "status": "running"},
    {"segment_name": "casual",  "control_rate": 0.018, "treatment_rate": 0.022, "lift_pct": 22.2, "p_value": 0.210, "significance": "not_significant", "status": "running"},
    {"segment_name": "dormant", "control_rate": 0.005, "treatment_rate": 0.006, "lift_pct": 20.0, "p_value": 0.480, "significance": "not_significant", "status": "pending"},
]

# /api/ab-tests/comparison
AB_COMPARISON = [
    {"segment_name": "power",   "variant": "control",   "conversion_rate": 0.062, "avg_sessions": 8.1, "avg_exports": 8.8, "sample_size": 62},
    {"segment_name": "power",   "variant": "treatment", "conversion_rate": 0.091, "avg_sessions": 8.9, "avg_exports": 9.6, "sample_size": 62},
    {"segment_name": "growing", "variant": "control",   "conversion_rate": 0.041, "avg_sessions": 5.0, "avg_exports": 4.1, "sample_size": 79},
    {"segment_name": "growing", "variant": "treatment", "conversion_rate": 0.057, "avg_sessions": 5.3, "avg_exports": 4.6, "sample_size": 79},
    {"segment_name": "casual",  "variant": "control",   "conversion_rate": 0.018, "avg_sessions": 2.2, "avg_exports": 1.7, "sample_size": 49},
    {"segment_name": "casual",  "variant": "treatment", "conversion_rate": 0.022, "avg_sessions": 2.4, "avg_exports": 1.9, "sample_size": 49},
    {"segment_name": "dormant", "variant": "control",   "conversion_rate": 0.005, "avg_sessions": 0.3, "avg_exports": 0.2, "sample_size": 21},
    {"segment_name": "dormant", "variant": "treatment", "conversion_rate": 0.006, "avg_sessions": 0.4, "avg_exports": 0.2, "sample_size": 22},
]

# /api/kpis
KPIS = {
    "overall_conversion_rate":      0.054,
    "avg_time_to_convert_days":     6.2,
    "retention_30d":                0.83,
    "notification_engagement_rate": 0.41,
    "avg_revenue_amd":             2900,
}

# /api/campaigns
CAMPAIGNS = [
    {
        "campaign_id": 1, "name": "Power User Upgrade",
        "message": "You're a power user! Unlock unlimited exports with Pro.",
        "channel": "in-app", "trigger": "paywall_hit", "status": "active",
        "discount_pct": 20, "test_duration_days": 14,
    },
    {
        "campaign_id": 2, "name": "Growing User Nudge",
        "message": "You're growing fast ÃÂ¢ÃÂÃÂ go Pro to remove all limits.",
        "channel": "email", "trigger": "session_threshold", "status": "draft",
        "discount_pct": 15, "test_duration_days": 14,
    },
    {
        "campaign_id": 3, "name": "Re-engage Dormant",
        "message": "We miss you! Come back and see what's new in Pulse.",
        "channel": "push", "trigger": "inactivity_14d", "status": "paused",
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
    "growing": "You're on a roll ÃÂ¢ÃÂÃÂ go Pro to remove all export limits and unlock advanced filters.",
    "casual":  "Enjoying Pulse? Pro gives you 5x more exports and premium templates.",
    "dormant": "Welcome back! Upgrade to Pro today and get 30% off for the next 48 hours.",
}

# /api/demo/respond  (cumulative mock response log)
DEMO_RESPONSES = [
    {"segment_name": "power",   "response": "accept",  "count": 38},
    {"segment_name": "power",   "response": "dismiss", "count": 24},
    {"segment_name": "growing", "response": "accept",  "count": 29},
    {"segment_name": "growing", "response": "dismiss", "count": 41},
    {"segment_name": "casual",  "response": "accept",  "count": 11},
    {"segment_name": "casual",  "response": "dismiss", "count": 52},
    {"segment_name": "dormant", "response": "accept",  "count":  3},
    {"segment_name": "dormant", "response": "dismiss", "count": 18},
]

# ÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂ Sidebar navigation ÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂ
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
    st.caption("v1.0 â Milestone 4")
    st.markdown("[Documentation](https://ds-223-2026-spring.github.io/ds223-7-project/)")

# ÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂ
#  SEGMENTS  ÃÂ¢ÃÂÃÂ  /api/segments/counts  +  /api/segments/behavioral-averages
# ÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂ
if page == "Segments":
    st.title("Segments")
    st.caption("Free-user behavioural clustering ÃÂ¢ÃÂÃÂ 4 segments")

    # ÃÂ¢ÃÂÃÂ Filter bar ÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂ
    all_seg_names = [s["segment_name"].title() for s in SEGMENT_COUNTS]
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
    df_counts = pd.DataFrame(SEGMENT_COUNTS)
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
    df_beh = pd.DataFrame(SEGMENT_BEHAVIORAL)
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


    # Section 3: User breakdown table  (/api/segments/{name}/users)
    st.subheader("Top Users by Segment")
    seg_options_lower = [s.lower() for s in seg_filter_options]
    for seg_name in seg_options_lower:
        users_data = api_get(f"/api/segments/{seg_name}/users")
        if users_data is None:
            users_data = SEGMENT_USERS_MOCK.get(seg_name, [])
        if users_data:
            st.subheader(f"Top Users Ã¢ÂÂ {seg_name.title()}")
            st.dataframe(
                pd.DataFrame(users_data),
                use_container_width=True,
                hide_index=True,
            )

# ÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂ
#  A/B TESTS  ÃÂ¢ÃÂÃÂ  /api/ab-tests/summary  +  /api/ab-tests/comparison
# ÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂ
elif page == "A/B Tests":
    st.title("A/B Tests")
    st.caption("Control vs. treatment conversion performance per segment")

    tab_summary, tab_comparison = st.tabs(["Summary", "Variant Comparison"])

    # Tab 1: Summary  (/api/ab-tests/summary)
    with tab_summary:
        st.subheader("Test Summary ÃÂ¢ÃÂÃÂ model results")

        # Filter bar
        f1, f2 = st.columns([1, 1])
        sig_filter = f1.selectbox(
            "Filter by significance",
            ["All", "Significant only", "Borderline", "Not significant only"],
            key="ab_sig_filter",
        )
        status_filter = f2.selectbox(
            "Filter by status",
            ["All", "running", "pending", "complete"],
            key="ab_status_filter",
        )

        df_sum = pd.DataFrame(AB_SUMMARY)
        if sig_filter == "Significant only":
            df_sum = df_sum[df_sum["significance"] == "significant"]
        elif sig_filter == "Borderline":
            df_sum = df_sum[df_sum["significance"] == "borderline"]
        elif sig_filter == "Not significant only":
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
            st.dataframe(
                df_sum.rename(columns={
                    "segment_name":   "Segment",
                    "control_rate":   "Control Rate",
                    "treatment_rate": "Treatment Rate",
                    "lift_pct":       "Lift %",
                    "p_value":        "p-value",
                    "significance":   "Significance",
                    "status":         "Status",
                }).assign(**{
                    "Control Rate":   lambda d: d["Control Rate"].map(lambda x: f"{x:.1%}"),
                    "Treatment Rate": lambda d: d["Treatment Rate"].map(lambda x: f"{x:.1%}"),
                    "Lift %":         lambda d: d["Lift %"].map(lambda x: f"+{x:.1f}%"),
                    "Status":         lambda d: d["Status"].str.title(),
                }),
                use_container_width=True,
                hide_index=True,
            )
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
        df_cmp = pd.DataFrame(AB_COMPARISON)
        df_cmp["segment_name"] = df_cmp["segment_name"].str.title()
        if seg_filter != "All":
            df_cmp = df_cmp[df_cmp["segment_name"] == seg_filter]
        st.dataframe(
            df_cmp.rename(columns={
                "segment_name":    "Segment",
                "variant":         "Variant",
                "conversion_rate": "Conversion Rate",
                "avg_sessions":    "Avg Sessions",
                "avg_exports":     "Avg Exports",
                "sample_size":     "Sample Size",
            }).assign(**{
                "Conversion Rate": lambda d: d["Conversion Rate"].map(lambda x: f"{x:.1%}"),
            }),
            use_container_width=True,
            hide_index=True,
        )

        # Control vs Treatment bar chart per segment
        if not df_cmp.empty:
            import altair as alt
            df_rates = (
                df_cmp[["segment_name", "variant", "conversion_rate"]]
                .copy()
                .rename(columns={"segment_name": "Segment", "variant": "Variant", "conversion_rate": "Conversion Rate"})
            )
            chart = (
                alt.Chart(df_rates)
                .mark_bar()
                .encode(
                    x=alt.X("Segment:N", title="Segment"),
                    y=alt.Y("Conversion Rate:Q", axis=alt.Axis(format=".1%"), title="Conversion Rate"),
                    color=alt.Color("Variant:N", scale=alt.Scale(domain=["control", "treatment"], range=["#4C78A8", "#F58518"])),
                    xOffset="Variant:N",
                    tooltip=[
                        alt.Tooltip("Segment:N"),
                        alt.Tooltip("Variant:N"),
                        alt.Tooltip("Conversion Rate:Q", format=".1%"),
                    ],
                )
                .properties(title="Control vs Treatment Conversion Rate by Segment")
            )
            st.altair_chart(chart, use_container_width=True)
                st.caption("Data from /api/ab-tests/comparison (M3: mock)")

# ÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂ
#  KPIs  ÃÂ¢ÃÂÃÂ  /api/kpis
# ÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂ
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
    st.caption(f"Showing mock data ÃÂ¢ÃÂÃÂ period selector wires to /api/kpis?period=... in M4")
    st.divider()

    # 3 big metric cards
    k1, k2, k3 = st.columns(3)
    k1.metric(
        "Overall Conversion Rate",
        f'{KPIS["overall_conversion_rate"]:.1%}',
        delta="+1.1% vs last period",
    )
    k2.metric(
        "Avg Time to Convert",
        f'{KPIS["avg_time_to_convert_days"]:.1f} days',
        delta="-0.8 days vs last period",
    )
    k3.metric(
        "30-Day Pro Retention",
        f'{KPIS["retention_30d"]:.0%}',
        delta="+2% vs last period",
    )
    st.divider()

    # avg_revenue_amd metric
    k5, _, _ = st.columns(3)
    k5.metric(
        "Avg Revenue (AMD)",
        f'{KPIS["avg_revenue_amd"]:,.0f} AMD',
        delta="+150 AMD vs last period",
    )
    st.divider()

    # 4th metric: notification engagement
    k4, _, _ = st.columns(3)
    k4.metric(
        "Notification Engagement Rate",
        f'{KPIS["notification_engagement_rate"]:.0%}',
        delta="+4% vs last period",
    )
    st.caption("Data from /api/kpis (M3: mock)")

# ÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂ
#  CAMPAIGN EDITOR  ÃÂ¢ÃÂÃÂ  /api/campaigns/*  +  /api/global-params/*
# ÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂ
elif page == "Campaign Editor":
    st.title("Campaign Editor")
    st.caption("Manage upgrade campaigns and global test parameters")

    # Campaign list filter
    status_options = ["All"] + list({c["status"] for c in CAMPAIGNS})
    camp_status_filter = st.selectbox(
        "Filter campaigns by status",
        status_options,
        key="camp_list_filter",
    )
    filtered_campaigns = CAMPAIGNS if camp_status_filter == "All" else [
        c for c in CAMPAIGNS if c["status"] == camp_status_filter
    ]

    left_col, right_col = st.columns([1, 2])

    with left_col:
        st.subheader("Campaigns")
        if not filtered_campaigns:
            st.info("No campaigns match the selected filter.")
            selected_c = CAMPAIGNS[0]
        else:
            campaign_names = [f'#{c["campaign_id"]} ÃÂ¢ÃÂÃÂ {c["name"]}' for c in filtered_campaigns]
            selected_idx = st.selectbox(
                "Select campaign",
                range(len(filtered_campaigns)),
                format_func=lambda i: campaign_names[i],
                key="campaign_select",
            )
            selected_c = filtered_campaigns[selected_idx]

        c = selected_c
        st.write(f"**Channel:** {c['channel'].upper()}")
        st.write(f"**Trigger:** {c['trigger']}")
        status_color = {"active": "ÃÂ¢ÃÂÃÂ", "draft": "ÃÂ¢ÃÂÃÂª", "paused": "ÃÂ¢ÃÂÃÂ¸ÃÂ¯ÃÂ¸ÃÂ"}
        st.write(f"**Status:** {status_color.get(c['status'], 'ÃÂ¢ÃÂÃÂ¢')} {c['status'].title()}")

    with right_col:
        st.subheader("Edit Campaign")
        new_name = st.text_input("Campaign name", value=c["name"], key="camp_name")
        new_msg  = st.text_area(
            "Message template",
            value=c["message"],
            height=100,
            key="camp_msg",
            help="Will call PUT /api/campaigns/{id}/message in M4.",
        )
        ch1, ch2 = st.columns(2)
        new_channel = ch1.selectbox(
            "Channel",
            ["In-App", "Email", "Push"],
            index={"in-app": 0, "email": 1, "push": 2}.get(c["channel"], 0),
            key="camp_channel",
        )
        new_trigger = ch2.selectbox(
            "Trigger",
            ["Paywall Hit", "App Open", "After 3rd Export"],
            index={"paywall_hit": 0, "session_threshold": 1, "inactivity_14d": 2}.get(c["trigger"], 0),
            key="camp_trigger",
        )
        d1, d2 = st.columns(2)
        d1.number_input("Discount %",           min_value=0,  max_value=100, value=c["discount_pct"],       key="camp_discount")
        d2.number_input("Test duration (days)", min_value=1,  max_value=90,  value=c["test_duration_days"], key="camp_duration")
        st.divider()
        b1, b2, b3 = st.columns(3)
        if b1.button("ÃÂ°ÃÂÃÂÃÂ Launch campaign", key="btn_launch", type="primary"):
            st.success(f"Campaign \"{new_name}\" launched (mock). POST /api/campaigns/{c['campaign_id']}/launch")
        if b2.button("ÃÂ°ÃÂÃÂÃÂ¾ Save changes", key="btn_save"):
            st.info("Changes saved (mock). PUT /api/campaigns/{id}")
        if b3.button("ÃÂ¢ÃÂÃÂº Reset to draft", key="btn_reset"):
            st.warning("Campaign reset (mock). DELETE /api/campaigns/{id}/reset")

    st.divider()
    st.subheader("Global Parameters")
    st.caption("Shared defaults applied to all campaigns unless overridden")
    gp1, gp2, gp3, gp4 = st.columns(4)
    gp1.number_input("Test Duration (days)",    value=GLOBAL_PARAMS["test_duration_days"],     min_value=1,  max_value=90,  key="gp_dur")
    gp2.number_input("Discount %",              value=GLOBAL_PARAMS["discount_pct"],           min_value=0,  max_value=100, key="gp_disc")
    gp3.number_input("Min Sample Size",         value=GLOBAL_PARAMS["min_sample_size"],        min_value=10,               key="gp_sample")
    gp4.number_input("Significance Threshold",  value=GLOBAL_PARAMS["significance_threshold"], min_value=0.0, max_value=1.0, step=0.01, key="gp_sig")
    if st.button("Save global params", key="btn_gp_save"):
        st.success("Global params saved (mock). PUT /api/global-params/{key}")

# ÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂ
#  USER DEMO  ÃÂ¢ÃÂÃÂ  /api/demo/message/{segment_name}  +  /api/demo/respond
# ÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂÃÂ¢ÃÂÃÂ
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
        st.divider()
        st.subheader("Upgrade Message")
        msg = DEMO_MESSAGES[seg]
        st.info(msg)
        st.caption("â ï¸ Using demo data â backend unavailable")
        st.divider()

        # Accept / Dismiss buttons  (/api/demo/respond)
        st.write("**How would this user respond?**")
        a_col, d_col = st.columns(2)
        if a_col.button("ÃÂ¢ÃÂÃÂ Accept upgrade", key="btn_accept", type="primary"):
            st.success("Response 'accept' recorded (mock). POST /api/demo/respond")
        if d_col.button("ÃÂ¢ÃÂÃÂ Dismiss", key="btn_dismiss"):
            st.warning("Response 'dismiss' recorded (mock). POST /api/demo/respond")

    with stats_col:
        # Response stats  (aggregated from /api/demo/respond)
        st.subheader("Response Stats by Segment")
        df_resp = pd.DataFrame(DEMO_RESPONSES)
        df_pivot = df_resp.pivot(index="segment_name", columns="response", values="count").fillna(0).astype(int)
        df_pivot.index = df_pivot.index.str.title()
        df_pivot.columns = [col.title() for col in df_pivot.columns]
        df_pivot["Total"] = df_pivot.sum(axis=1)
        if "Accept" in df_pivot.columns:
            df_pivot["Accept Rate"] = (df_pivot["Accept"] / df_pivot["Total"]).map(lambda x: f"{x:.0%}")
        st.dataframe(df_pivot, use_container_width=True)
        st.caption("Aggregated responses from /api/demo/respond (M3: mock)")
        if "Accept" in df_pivot.columns:
            st.bar_chart(
                df_resp[df_resp["response"] == "accept"].set_index("segment_name")["count"]
            )
            st.caption("Accept counts by segment")
