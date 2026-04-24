"""User Demo page."""
import streamlit as st
import requests

def render(API):
    st.markdown("""
    <style>
    .phone-mockup {
        background: #1e1e2e;
        border-radius: 24px;
        padding: 24px;
        border: 2px solid #2e2e3e;
        max-width: 320px;
        margin: 0 auto;
    }
    .phone-header {
        color: #a0a0b0;
        font-size: 11px;
        text-align: center;
        margin-bottom: 16px;
    }
    .phone-app-title {
        color: #fff;
        font-size: 16px;
        font-weight: 600;
        margin-bottom: 4px;
    }
    .phone-subtitle { color: #a0a0b0; font-size: 12px; margin-bottom: 16px; }
    .upgrade-banner {
        background: linear-gradient(135deg, #7c6ff7, #a855f7);
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        margin-top: 12px;
    }
    .upgrade-title { color: #fff; font-size: 14px; font-weight: 600; margin-bottom: 4px; }
    .upgrade-body { color: #e0d0ff; font-size: 12px; margin-bottom: 12px; }
    .counter-card {
        background: #1e1e2e;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        border: 1px solid #2e2e3e;
    }
    .counter-label { color: #a0a0b0; font-size: 13px; margin-bottom: 8px; }
    .counter-value { color: #fff; font-size: 36px; font-weight: 700; }
    .log-entry { color: #a0a0b0; font-size: 13px; padding: 6px 0; border-bottom: 1px solid #2e2e3e; }
    </style>
    """, unsafe_allow_html=True)

    st.title("User Demo")
    st.caption("live")
    st.divider()

    # --- Session state ---
    if "upgraded" not in st.session_state:
        st.session_state.upgraded = 0
    if "try_later" not in st.session_state:
        st.session_state.try_later = 0
    if "log" not in st.session_state:
        st.session_state.log = []

    # --- Controls ---
    col1, col2 = st.columns(2)
    with col1:
        segment = st.selectbox(
            "Simulated segment",
            ["power", "growing", "casual", "dormant"],
            format_func=lambda x: x.capitalize() + " user"
        )
    with col2:
        ab_group = st.selectbox(
            "A/B group",
            ["treatment", "control"],
            format_func=lambda x: "Treatment (targeted)" if x == "treatment" else "Control (generic)"
        )

    st.divider()

    # --- Counters ---
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div class="counter-card">
            <div class="counter-label">Upgraded</div>
            <div class="counter-value">{st.session_state.upgraded}</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="counter-card">
            <div class="counter-label">Try Later</div>
            <div class="counter-value">{st.session_state.try_later}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()

    # --- Phone mockup ---
    left, center, right = st.columns([1, 2, 1])
    with center:
        st.markdown('<div class="section-title">Live user preview</div>', unsafe_allow_html=True)

        try:
            msg = requests.get(f"{API}/api/demo/message/{segment}", timeout=5).json()
            rendered_body = msg.get("rendered_body", "")
        except:
            rendered_body = "Could not load message from backend."

        st.markdown(f"""
        <div class="phone-mockup">
            <div class="phone-header">9:41 ▲▲▲ ■■■</div>
            <div class="phone-app-title">Armat</div>
            <div class="phone-subtitle">New poem · Draft</div>
            <div style="color:#a0a0b0; font-size:11px; margin-bottom:12px;">
                Bold · Italic · Thesaurus ✦ · Rhyme ✦ · Meter ✦
            </div>
            <div style="color:#e0e0f0; font-size:12px; font-style:italic; margin-bottom:12px;">
                Անապատի լռության մեջ<br>
                Բառերը թռչում են անձայն,<br>
                Հայոց լեզվի հոգու ծայրին<br>
                Ամեն տող — մի նոր կյանք
            </div>
            <div style="color:#a0a0b0; font-size:11px; margin-bottom:12px;">47 words · 4 lines</div>
            <div class="upgrade-banner">
                <div class="upgrade-title">Unlock your full potential</div>
                <div class="upgrade-body">{rendered_body}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        b1, b2 = st.columns(2)
        with b1:
            if st.button("⬆️ Upgrade", use_container_width=True, key="upgrade_btn"):
                try:
                    requests.post(f"{API}/api/demo/respond", json={
                        "segment_name": segment,
                        "ab_group": ab_group,
                        "decision": "upgraded"
                    }, timeout=5)
                except:
                    pass
                st.session_state.upgraded += 1
                st.session_state.log.append(f"✅ Upgraded — {segment} ({ab_group})")
                st.rerun()
        with b2:
            if st.button("⏩ Try later", use_container_width=True, key="try_later_btn"):
                try:
                    requests.post(f"{API}/api/demo/respond", json={
                        "segment_name": segment,
                        "ab_group": ab_group,
                        "decision": "try_later"
                    }, timeout=5)
                except:
                    pass
                st.session_state.try_later += 1
                st.session_state.log.append(f"⏩ Try later — {segment} ({ab_group})")
                st.rerun()

    st.divider()

    # --- Response log ---
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("Response log — backend events")
    with col2:
        if st.button("Clear log"):
            st.session_state.log = []
            st.rerun()

    if st.session_state.log:
        for entry in reversed(st.session_state.log):
            st.markdown(f'<div class="log-entry">{entry}</div>', unsafe_allow_html=True)
    else:
        st.info("No responses yet. Tap 'Show upgrade message' on the phone →")