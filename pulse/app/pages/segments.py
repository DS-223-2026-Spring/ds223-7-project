"""Segments page."""
import streamlit as st
import requests
import pandas as pd

def render(API):
    st.markdown("""
    <style>
    .metric-card {
        background: #1e1e2e;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        border: 1px solid #2e2e3e;
    }
    .metric-card h3 { color: #a0a0b0; font-size: 14px; margin: 0; }
    .metric-card h1 { color: #ffffff; font-size: 32px; margin: 8px 0 0 0; }
    .bar-row { display: flex; align-items: center; gap: 12px; margin: 8px 0; }
    .bar-label { color: #a0a0b0; width: 80px; font-size: 13px; }
    .bar-fill { height: 10px; border-radius: 5px; background: #7c6ff7; }
    .bar-value { color: #fff; font-size: 13px; width: 40px; }
    .section-title { color: #fff; font-size: 18px; font-weight: 600; margin: 24px 0 12px 0; }
    </style>
    """, unsafe_allow_html=True)

    st.title("Segments")

    # --- Segment count cards ---
    try:
        counts = requests.get(f"{API}/api/segments/counts", timeout=5).json()
    except:
        counts = []

    if counts:
        cols = st.columns(len(counts))
        for i, seg in enumerate(counts):
            with cols[i]:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>{seg['segment_name']} users</h3>
                    <h1>{seg['user_count']:,}</h1>
                </div>
                """, unsafe_allow_html=True)
    else:
        c = st.columns(4)
        for col, name, val in zip(c, ["Power", "Growing", "Casual", "Dormant"], ["1,240", "1,580", "980", "620"]):
            with col:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>{name} users</h3>
                    <h1>{val}</h1>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Behavioral bar charts ---
    try:
        avgs = requests.get(f"{API}/api/segments/behavioral-averages", timeout=5).json()
    except:
        avgs = []

    col1, col2 = st.columns(2)

    segments = avgs if avgs else [
        {"segment_name": "Power", "avg_exports": 9.2, "avg_paywall_hits": 7.4},
        {"segment_name": "Growing", "avg_exports": 4.8, "avg_paywall_hits": 3.1},
        {"segment_name": "Casual", "avg_exports": 1.4, "avg_paywall_hits": 0.9},
        {"segment_name": "Dormant", "avg_exports": 0.2, "avg_paywall_hits": 0.1},
    ]

    max_exports = max(s.get("avg_exports", 0) for s in segments) or 1
    max_paywall = max(s.get("avg_paywall_hits", 0) for s in segments) or 1

    with col1:
        st.markdown('<div class="section-title">Exports per week</div>', unsafe_allow_html=True)
        bars = ""
        for s in segments:
            val = s.get("avg_exports", 0)
            width = int((val / max_exports) * 200)
            bars += f"""
            <div class="bar-row">
                <div class="bar-label">{s['segment_name']}</div>
                <div class="bar-fill" style="width:{width}px"></div>
                <div class="bar-value">{val}</div>
            </div>"""
        st.markdown(bars, unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="section-title">Paywall hits per week</div>', unsafe_allow_html=True)
        bars = ""
        for s in segments:
            val = s.get("avg_paywall_hits", 0)
            width = int((val / max_paywall) * 200)
            bars += f"""
            <div class="bar-row">
                <div class="bar-label">{s['segment_name']}</div>
                <div class="bar-fill" style="width:{width}px; background:#f7a35c"></div>
                <div class="bar-value">{val}</div>
            </div>"""
        st.markdown(bars, unsafe_allow_html=True)

    st.divider()

    # --- Segment breakdown table ---
    st.markdown('<div class="section-title">Segment breakdown</div>', unsafe_allow_html=True)
    if avgs:
        df = pd.DataFrame([{
            "Segment": s["segment_name"],
            "Users": s.get("user_count", "—"),
            "Avg sessions/wk": s.get("avg_sessions_per_week", "—"),
            "Avg exports/wk": s.get("avg_exports", "—"),
            "Avg paywall hits/wk": s.get("avg_paywall_hits", "—"),
        } for s in avgs])
    else:
        df = pd.DataFrame([
            {"Segment": "Power", "Users": 1240, "Avg sessions/wk": 12.4, "Avg exports/wk": 9.2, "Avg paywall hits/wk": 7.4},
            {"Segment": "Growing", "Users": 1580, "Avg sessions/wk": 6.1, "Avg exports/wk": 4.8, "Avg paywall hits/wk": 3.1},
            {"Segment": "Casual", "Users": 980, "Avg sessions/wk": 2.3, "Avg exports/wk": 1.4, "Avg paywall hits/wk": 0.9},
            {"Segment": "Dormant", "Users": 620, "Avg sessions/wk": 0.4, "Avg exports/wk": 0.2, "Avg paywall hits/wk": 0.1},
        ])
    st.dataframe(df, use_container_width=True, hide_index=True)