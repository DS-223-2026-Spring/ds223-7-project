"""Campaign Editor page."""
import streamlit as st
import requests

def render(API):
    st.markdown("""
    <style>
    .campaign-card {
        background: #1e1e2e;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
        border: 1px solid #2e2e3e;
    }
    .campaign-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
    .campaign-title { color: #fff; font-size: 18px; font-weight: 600; }
    .badge-running { background: #1a4731; color: #4ade80; padding: 4px 12px; border-radius: 20px; font-size: 12px; }
    .badge-pending { background: #3a2e1a; color: #fbbf24; padding: 4px 12px; border-radius: 20px; font-size: 12px; }
    .badge-draft { background: #2e2e3a; color: #a0a0b0; padding: 4px 12px; border-radius: 20px; font-size: 12px; }
    .param-card {
        background: #1e1e2e;
        border-radius: 12px;
        padding: 16px;
        border: 1px solid #2e2e3e;
        margin-bottom: 24px;
    }
    .section-title { color: #fff; font-size: 18px; font-weight: 600; margin: 0 0 16px 0; }
    .preview-box {
        background: #13131f;
        border-radius: 8px;
        padding: 12px;
        color: #a0a0b0;
        font-size: 13px;
        margin: 8px 0;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("Campaign Editor")
    st.divider()

    # --- Global Params ---
    st.markdown('<div class="section-title">Global Parameters</div>', unsafe_allow_html=True)
    try:
        params = requests.get(f"{API}/api/global-params", timeout=5).json()
    except:
        params = []

    param_map = {p["key"]: p["value"] for p in params} if params else {
        "pro_price_amd": "2900",
        "dormant_discount": "20",
        "template_count": "120"
    }

    with st.container(border=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            new_price = st.text_input("Pro price (AMD)", value=param_map.get("pro_price_amd", "2900"))
            if st.button("Save", key="save_price"):
                try:
                    requests.put(f"{API}/api/global-params/pro_price_amd",
                                json={"value": new_price}, timeout=5)
                    st.success("Saved!")
                except:
                    st.error("Could not reach API")
        with col2:
            new_discount = st.text_input("Discount % (dormant)", value=param_map.get("dormant_discount", "20"))
            if st.button("Save", key="save_discount"):
                try:
                    requests.put(f"{API}/api/global-params/dormant_discount",
                                json={"value": new_discount}, timeout=5)
                    st.success("Saved!")
                except:
                    st.error("Could not reach API")
        with col3:
            new_templates = st.text_input("Template count", value=param_map.get("template_count", "120"))
            if st.button("Save", key="save_templates"):
                try:
                    requests.put(f"{API}/api/global-params/template_count",
                                json={"value": new_templates}, timeout=5)
                    st.success("Saved!")
                except:
                    st.error("Could not reach API")

    st.divider()

    # --- Campaign cards ---
    try:
        campaigns = requests.get(f"{API}/api/campaigns", timeout=5).json()
    except:
        campaigns = []

    fallback = [
        {"campaign_id": "1", "segment_label": "Power users", "status": "pending",
         "channel": "in_app_popup", "trigger_event": "on_paywall_hit",
         "active_message": {"body": "You've exported {{export_count}} times and hit limits {{paywall_hits}} times — go unlimited for AMD {{price}}/month.", "body_rendered": "You've exported 9 times and hit limits 7 times — go unlimited for AMD 2,900/month."}},
        {"campaign_id": "2", "segment_label": "Growing users", "status": "pending",
         "channel": "in_app_popup", "trigger_event": "on_paywall_hit",
         "active_message": {"body": "You're growing fast! Unlock HD exports, custom fonts and more — AMD {{price}}/month.", "body_rendered": "You're growing fast! Unlock HD exports, custom fonts and more — AMD 2,900/month."}},
        {"campaign_id": "3", "segment_label": "Casual users", "status": "pending",
         "channel": "in_app_popup", "trigger_event": "on_paywall_hit",
         "active_message": {"body": "Did you know Pro users get {{template_count}} exclusive Armenian templates? Try Pro free for 7 days.", "body_rendered": "Did you know Pro users get 120 exclusive Armenian templates? Try Pro free for 7 days."}},
        {"campaign_id": "4", "segment_label": "Dormant users", "status": "pending",
         "channel": "email", "trigger_event": "on_app_open",
         "active_message": {"body": "We miss you! Come back and get {{discount}}% off your first Pro month. Offer expires in 48h.", "body_rendered": "We miss you! Come back and get 20% off your first Pro month. Offer expires in 48h."}},
    ]
    display_campaigns = campaigns if campaigns else fallback

    channel_options = ["in_app_popup", "push_notification", "email"]