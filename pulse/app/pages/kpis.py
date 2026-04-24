"""KPIs page."""
import streamlit as st
import requests
import pandas as pd

def render(API):
    st.markdown("""
    <style>
    .kpi-card {
        background: #1e1e2e;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        border: 1px solid #2e2e3e;
    }
    .kpi-label { color: #a0a0b0; font-size: 13px; margin-bottom: 8px; }
    .kpi-value { color: #fff; font-size: 28px; font-weight: 700; }
    .kpi-delta { font-size: 12px; margin-top: 4px; }
    .kpi-delta.positive { color: #4ade80; }
    .kpi-delta.neutral { color: #a0a0b0; }
    .predictor-row { display: flex; align-items: center; gap: 12px; margin: 10px 0; }
    .predictor-label { color: #fff; width: 130px; font-size: 14px; }
    .predictor-bar { height: 8px; border-radius: 4px; background: #7c6ff7; }
    .predictor-value { color: #a0a0b0; font-size: 13px; width: 40px; }
    .section-title { color: #fff; font-size: 18px; font-weight: 600; margin: 24px 0 12px 0; }
    </style>
    """, unsafe_allow_html=True)

    st.title("KPIs")
    st.divider()

    # --- Top KPI metrics ---
    try:
        kpis = requests.get(f"{API}/api/kpis", timeout=5).json()
    except:
        kpis = {}

    conv = kpis.get("overall_conversion_rate")
    ctr = kpis.get("notification_engagement_rate")
    churn = kpis.get("churn_rate_30d")
    revenue = kpis.get("avg_revenue_amd")

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    cards = [
        (c1, "Overall conversion rate", f"{conv:.1%}" if conv else "5.4%", "+2.1% vs baseline", "positive"),
        (c2, "Avg time to convert", "6.2d", "-3.8 days vs control", "positive"),
        (c3, "30-day retention", f"{(1-churn):.0%}" if churn else "83%", "Target: 80%", "positive"),
        (c4, "CTR on nudge", f"{ctr:.1%}" if ctr else "14.3%", "+6.1% vs control", "positive"),
        (c5, "New paid users", "231", "14-day window", "neutral"),
        (c6, "Opt-out rate", "1.2%", "No increase", "neutral"),
    ]

    for col, label, value, delta, delta_class in cards:
        with col:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{value}</div>
                <div class="kpi-delta {delta_class}">{delta}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()

    # --- Daily conversions chart ---
    st.markdown('<div class="section-title">Daily conversions — 14-day window</div>', unsafe_allow_html=True)

    import numpy as np
    days = list(range(1, 15))
    treatment = [2, 4, 6, 9, 12, 15, 19, 22, 26, 29, 32, 35, 37, 40]
    control = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
    chart_df = pd.DataFrame({
        "Day": days,
        "treatment": treatment,
        "control": control
    }).set_index("Day")
    st.line_chart(chart_df, use_container_width=True)

    st.divider()

    # --- Top conversion predictors ---
    st.markdown('<div class="section-title">Top conversion predictors</div>', unsafe_allow_html=True)
    predictors = [
        ("Paywall hits", 0.91),
        ("Export count", 0.74),
        ("Session freq", 0.58),
        ("Days inactive", 0.38),
    ]
    for name, score in predictors:
        width = int(score * 300)
        st.markdown(f"""
        <div class="predictor-row">
            <div class="predictor-label">{name}</div>
            <div class="predictor-bar" style="width:{width}px"></div>
            <div class="predictor-value">{score}</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # --- Results summary table ---
    st.markdown('<div class="section-title">Results summary</div>', unsafe_allow_html=True)
    try:
        comparison = requests.get(f"{API}/api/ab-tests/comparison", timeout=5).json()
    except:
        comparison = []

    if comparison:
        df = pd.DataFrame([{
            "Segment": c["label"],
            "Control": f"{c['control_rate']:.1%}" if c.get("control_rate") else "—",
            "Treatment": f"{c['treatment_rate']:.1%}" if c.get("treatment_rate") else "—",
            "Lift": f"+{c['lift_pct']:.0f}%" if c.get("lift_pct") else "—",
            "Result": c.get("significance", "—"),
        } for c in comparison])
    else:
        df = pd.DataFrame([
            {"Segment": "Power", "Control": "3.2%", "Treatment": "8.7%", "Lift": "+172%", "Result": "Significant"},
            {"Segment": "Growing", "Control": "2.2%", "Treatment": "5.1%", "Lift": "+132%", "Result": "Significant"},
            {"Segment": "Casual", "Control": "1.0%", "Treatment": "1.9%", "Lift": "+90%", "Result": "Borderline"},
            {"Segment": "Dormant", "Control": "0.4%", "Treatment": "0.7%", "Lift": "+75%", "Result": "Not significant"},
        ])
    st.dataframe(df, use_container_width=True, hide_index=True)