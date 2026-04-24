"""A/B Tests page."""
import streamlit as st
import requests
import pandas as pd

def render(API):
    st.markdown("""
    <style>
    .test-card {
        background: #1e1e2e;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
        border: 1px solid #2e2e3e;
    }
    .test-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
    .test-title { color: #fff; font-size: 18px; font-weight: 600; }
    .badge-running { background: #1a4731; color: #4ade80; padding: 4px 12px; border-radius: 20px; font-size: 12px; }
    .badge-pending { background: #3a2e1a; color: #fbbf24; padding: 4px 12px; border-radius: 20px; font-size: 12px; }
    .stat-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; margin-bottom: 16px; }
    .stat-box { background: #13131f; border-radius: 8px; padding: 12px; text-align: center; }
    .stat-label { color: #a0a0b0; font-size: 11px; margin-bottom: 4px; }
    .stat-value { color: #fff; font-size: 20px; font-weight: 600; }
    .stat-value.lift { color: #4ade80; }
    .pvalue { color: #a0a0b0; font-size: 12px; margin-bottom: 12px; }
    .significant { color: #4ade80; }
    </style>
    """, unsafe_allow_html=True)

    st.title("A/B Tests")
    st.divider()

    # --- A/B Test cards ---
    try:
        tests = requests.get(f"{API}/api/ab-tests/summary", timeout=5).json()
    except:
        tests = []

    fallback = [
        {"segment_label": "Power users", "status": "running", "test_id": "1", "control_n": 620, "treatment_n": 620, "control_rate": 0.032, "treatment_rate": 0.087, "lift_pct": 172, "p_value": 0.0012, "significance": "Statistically significant", "duration_days": 14},
        {"segment_label": "Growing users", "status": "running", "test_id": "2", "control_n": 790, "treatment_n": 790, "control_rate": 0.022, "treatment_rate": 0.051, "lift_pct": 132, "p_value": 0.0031, "significance": "Statistically significant", "duration_days": 14},
        {"segment_label": "Casual users", "status": "pending", "test_id": "3", "control_n": 490, "treatment_n": 490, "control_rate": None, "treatment_rate": None, "lift_pct": None, "p_value": None, "significance": None, "duration_days": 14},
        {"segment_label": "Dormant users", "status": "pending", "test_id": "4", "control_n": 310, "treatment_n": 310, "control_rate": None, "treatment_rate": None, "lift_pct": None, "p_value": None, "significance": None, "duration_days": 14},
    ]
    display_tests = tests if tests else fallback

    for test in display_tests:
        status = test.get("status", "pending")
        badge = f'<span class="badge-running">Running</span>' if status == "running" else f'<span class="badge-pending">Pending</span>'

        ctrl = test.get("control_rate")
        treat = test.get("treatment_rate")
        lift = test.get("lift_pct")
        pval = test.get("p_value")
        sig = test.get("significance", "")

        ctrl_str = f"{ctrl:.1%}" if ctrl else "—"
        treat_str = f"{treat:.1%}" if treat else "—"
        lift_str = f"+{lift:.0f}%" if lift else "—"

        st.markdown(f"""
        <div class="test-card">
            <div class="test-header">
                <div class="test-title">{test['segment_label']}</div>
                {badge}
            </div>
            <div class="stat-grid">
                <div class="stat-box">
                    <div class="stat-label">Control users</div>
                    <div class="stat-value">{test.get('control_n', '—')}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Treatment users</div>
                    <div class="stat-value">{test.get('treatment_n', '—')}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Control conv.</div>
                    <div class="stat-value">{ctrl_str}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Treatment conv.</div>
                    <div class="stat-value">{treat_str}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Lift</div>
                    <div class="stat-value lift">{lift_str}</div>
                </div>
            </div>
            <div class="pvalue">
                {"p-value: " + str(pval) + " — <span class='significant'>" + sig + "</span> · " + str(test.get('duration_days', 14)) + "-day window" if pval else "Test not yet launched for this segment"}
            </div>
        </div>
        """, unsafe_allow_html=True)

        b1, b2, b3 = st.columns(3)
        with b1:
            if st.button("Launch", key=f"launch_{test['test_id']}"):
                try:
                    requests.post(f"{API}/api/campaigns/{test['test_id']}/launch", timeout=5)
                    st.rerun()
                except:
                    st.error("Could not reach API")
        with b2:
            st.button("Pause", key=f"pause_{test['test_id']}", disabled=True)
        with b3:
            if st.button("Reset", key=f"reset_{test['test_id']}"):
                try:
                    requests.delete(f"{API}/api/campaigns/{test['test_id']}/reset", timeout=5)
                    st.rerun()
                except:
                    st.error("Could not reach API")

    st.divider()

    # --- Results summary table ---
    st.subheader("Results summary")
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