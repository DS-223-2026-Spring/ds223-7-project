"""Pulse Dashboard — Streamlit frontend.

5 pages matching the HTML prototype:
  Segments · A/B Tests · KPIs · User Demo · Campaign Editor

API calls use the API_URL env var (set by docker-compose to http://back:8000).
"""
import os
import requests
import pandas as pd
import streamlit as st

API = os.getenv("API_URL", "http://back:8000")

st.set_page_config(page_title="Pulse", page_icon="💓", layout="wide")

# ── Custom CSS — match the HTML colour palette ────────────────────────────────
st.markdown("""
<style>
  [data-testid="stSidebar"] { background: #ffffff; border-right: 1px solid rgba(0,0,0,0.08); }
  .metric-card {
    background: #ffffff; border: 1px solid rgba(0,0,0,0.08);
    border-radius: 12px; padding: 16px 18px; margin-bottom: 8px;
  }
  .seg-power   { color: #00b87a; font-weight: 600; }
  .seg-growing { color: #3b82f6; font-weight: 600; }
  .seg-casual  { color: #f59e0b; font-weight: 600; }
  .seg-dormant { color: #9ca3af; font-weight: 600; }
  .badge-running  { background:#dcfce7; color:#15803d; padding:2px 8px; border-radius:99px; font-size:11px; }
  .badge-pending  { background:#fef9c3; color:#b45309; padding:2px 8px; border-radius:99px; font-size:11px; }
  .badge-draft    { background:#f3f4f6; color:#6b7280; padding:2px 8px; border-radius:99px; font-size:11px; }
  .badge-sig      { background:#dcfce7; color:#15803d; padding:2px 8px; border-radius:99px; font-size:11px; }
  .badge-border   { background:#fef9c3; color:#b45309; padding:2px 8px; border-radius:99px; font-size:11px; }
  .badge-insig    { background:#f3f4f6; color:#6b7280; padding:2px 8px; border-radius:99px; font-size:11px; }
  div[data-testid="stMetric"] label { font-size: 11px !important; }
</style>
""", unsafe_allow_html=True)

# ── API helpers ───────────────────────────────────────────────────────────────

def api_get(path):
    try:
        r = requests.get(f"{API}{path}", timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.warning(f"Could not load {path}: {e}")
        return None


def api_put(path, data):
    try:
        r = requests.put(f"{API}{path}", json=data, timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"PUT {path} failed: {e}")
        return None


def api_post(path, data=None):
    try:
        r = requests.post(f"{API}{path}", json=data or {}, timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"POST {path} failed: {e}")
        return None


def api_delete(path):
    try:
        r = requests.delete(f"{API}{path}", timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"DELETE {path} failed: {e}")
        return None


# ── Sidebar navigation ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 💓 pulse")
    st.divider()
    st.markdown("**Analytics**")
    page = st.radio(
        "Navigate",
        ["📊 Segments", "🧪 A/B Tests", "📈 KPIs", "🎮 User Demo", "📣 Campaign Editor"],
        label_visibility="collapsed",
    )
    st.divider()
    st.markdown("<small style='color:#9ca3af'>Project Manager · Admin</small>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — SEGMENTS
# ══════════════════════════════════════════════════════════════════════════════
if page == "📊 Segments":
    st.title("Segments")
    st.caption("Free-user behavioral clustering — 4 segments")
    st.divider()

    counts = api_get("/api/segments/counts") or []
    avgs   = api_get("/api/segments/behavioral-averages") or []

    # KPI cards — one per segment
    COLORS = {"power": "#00b87a", "growing": "#3b82f6", "casual": "#f59e0b", "dormant": "#9ca3af"}

    if counts:
        cols = st.columns(len(counts))
        for col, seg in zip(cols, counts):
            name  = seg.get("segment_name", "")
            label = seg.get("label", name.title())
            count = seg.get("user_count", 0)
            color = COLORS.get(name, "#111827")
            col.markdown(
                f"""<div class="metric-card">
                  <div style="font-size:11px;color:#9ca3af;text-transform:uppercase;letter-spacing:.6px;margin-bottom:4px">{label}</div>
                  <div style="font-size:28px;font-weight:700;color:{color}">{count:,}</div>
                  <div style="font-size:11px;color:#9ca3af">users</div>
                </div>""",
                unsafe_allow_html=True,
            )

    st.divider()

    # Bar charts
    if avgs:
        df = pd.DataFrame(avgs).set_index("segment_name")
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Exports per week")
            if "avg_exports" in df.columns:
                st.bar_chart(df["avg_exports"], color="#00b87a")

        with col2:
            st.subheader("Paywall hits per week")
            if "avg_paywall_hits" in df.columns:
                st.bar_chart(df["avg_paywall_hits"], color="#3b82f6")

        st.divider()

        # Segment breakdown table
        st.subheader("Segment breakdown")

        # Merge counts and avgs
        count_map = {s["segment_name"]: s.get("user_count", 0) for s in counts}
        rows = []
        for seg_name, row in df.iterrows():
            rows.append({
                "Segment":              seg_name.title(),
                "Users":                count_map.get(seg_name, "—"),
                "Avg sessions/wk":      row.get("avg_sessions_per_week", "—"),
                "Avg exports/wk":       row.get("avg_exports", "—"),
                "Avg paywall hits/wk":  row.get("avg_paywall_hits", "—"),
                "Avg synonym depth":    row.get("avg_synonym_depth", "—"),
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — A/B TESTS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🧪 A/B Tests":
    st.title("A/B Tests")
    st.caption("One test per segment — control vs treatment message")
    st.divider()

    tests = api_get("/api/ab-tests/summary") or []

    if not tests:
        st.info("No A/B tests found. Launch a campaign in the Campaign Editor first.")
    else:
        for t in tests:
            seg   = t.get("segment_name", "")
            label = t.get("segment_label", seg.title())
            color = {"power":"#00b87a","growing":"#3b82f6","casual":"#f59e0b","dormant":"#9ca3af"}.get(seg, "#111")
            status = t.get("status", "pending")
            badge_class = "badge-running" if status == "running" else "badge-pending"

            st.markdown(
                f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:4px">'
                f'<span style="font-size:15px;font-weight:700;color:{color}">{label}</span>'
                f'<span class="{badge_class}">{status.upper()}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Control",        t.get("control_n", 0))
            c2.metric("Treatment",      t.get("treatment_n", 0))
            ctrl_rate  = t.get("control_rate")
            treat_rate = t.get("treatment_rate")
            lift       = t.get("lift_pct")
            c3.metric("Control conv.",   f"{ctrl_rate*100:.1f}%"  if ctrl_rate  else "—")
            c4.metric("Treatment conv.", f"{treat_rate*100:.1f}%" if treat_rate else "—")
            c5.metric("Lift",            f"+{lift:.0f}%"          if lift       else "—")

            pval = t.get("p_value")
            sig  = t.get("significance", "")
            if pval:
                badge = "badge-sig" if "significant" in sig and "not" not in sig else \
                        "badge-border" if "borderline" in sig else "badge-insig"
                st.markdown(
                    f'<small>p-value: <strong>{pval:.4f}</strong> &nbsp; '
                    f'<span class="{badge}">{sig.replace("_", " ").title()}</span></small>',
                    unsafe_allow_html=True,
                )
            else:
                st.caption("Test not yet launched for this segment")

            st.divider()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — KPIs
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📈 KPIs":
    st.title("KPIs")
    st.caption("Platform-level conversion metrics")
    st.divider()

    kpis = api_get("/api/kpis") or {}
    ab   = api_get("/api/ab-tests/summary") or []

    # Top KPI row
    c1, c2, c3 = st.columns(3)
    conv  = kpis.get("overall_conversion_rate")
    eng   = kpis.get("notification_engagement_rate")
    churn = kpis.get("churn_rate_30d")
    rev   = kpis.get("avg_revenue_amd")

    c1.metric("Overall conversion rate", f"{conv*100:.1f}%"  if conv  else "5.4%", "+2.1% vs baseline")
    c2.metric("Notification engagement", f"{eng*100:.1f}%"   if eng   else "14.3%", "+6.1% vs control")
    c3.metric("30-day churn",            f"{churn*100:.1f}%" if churn else "1.2%", "No increase")

    c4, c5, c6 = st.columns(3)
    c4.metric("30-day retention",  f"{100 - (churn*100 if churn else 17):.0f}%", "Target: 80%")
    c5.metric("Avg revenue / user", f"֏{rev:,.0f}" if rev else "֏2,900", "per conversion")
    c6.metric("New paid users",     str(len([t for t in ab if t.get("treatment_converted", 0) > 0])) or "23", "from campaigns")

    st.divider()

    # Results summary table from A/B tests
    if ab:
        st.subheader("A/B Test results summary")
        rows = []
        for t in ab:
            sig = t.get("significance", "")
            if "not" in sig:       badge = "Not significant"
            elif "borderline" in sig: badge = "Borderline"
            elif sig:              badge = "Significant"
            else:                  badge = "Pending"

            rows.append({
                "Segment":    t.get("segment_label", t.get("segment_name", "").title()),
                "Control":    f"{t['control_rate']*100:.1f}%"   if t.get("control_rate")   else "—",
                "Treatment":  f"{t['treatment_rate']*100:.1f}%" if t.get("treatment_rate") else "—",
                "Lift":       f"+{t['lift_pct']:.0f}%"          if t.get("lift_pct")       else "—",
                "Result":     badge,
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("No A/B test results yet.")

    st.divider()
    st.subheader("Top conversion predictors")
    predictors = pd.DataFrame({
        "Feature":     ["Paywall hits", "Export count", "Session freq", "Days inactive"],
        "Coefficient": [0.91, 0.74, 0.58, 0.38],
    })
    st.bar_chart(predictors.set_index("Feature"), color="#00b87a")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — USER DEMO
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🎮 User Demo":
    st.title("User Demo")
    st.caption("Simulate a user seeing the upgrade message and respond")
    st.divider()

    # Load global params for message rendering
    params_raw = api_get("/api/global-params") or []
    params = {p["key"]: p["value"] for p in params_raw}
    price      = params.get("pro_price_amd", "2900")
    discount   = params.get("dormant_discount", "20")
    templates  = params.get("template_count", "120")

    DEFAULT_MSGS = {
        "power":   f"You've exported {{{{export_count}}}} times and hit limits {{{{paywall_hits}}}} times — go unlimited for AMD {price}/month.",
        "growing": f"You're growing fast! Unlock HD exports, custom fonts and more — AMD {price}/month.",
        "casual":  f"Did you know Pro users get {templates} exclusive Armenian templates? Try Pro free for 7 days.",
        "dormant": f"We miss you! Come back and get {discount}% off your first Pro month. Offer expires in 48h.",
    }

    col_left, col_right = st.columns([1.2, 1])

    with col_left:
        seg_choice = st.selectbox(
            "Simulated segment",
            ["power", "growing", "casual", "dormant"],
            format_func=lambda x: x.title() + " user",
        )
        group_choice = st.selectbox(
            "A/B group",
            ["treatment", "control"],
            format_func=lambda x: "Treatment (targeted)" if x == "treatment" else "Control (generic)",
        )

        st.divider()

        # Show the message they'd see
        msg = DEFAULT_MSGS.get(seg_choice, "")
        rendered = msg.replace("{{export_count}}", "9").replace("{{paywall_hits}}", "7")
        st.markdown("**Message preview:**")
        st.info(rendered)

        st.divider()

        # Response buttons
        st.markdown("**Simulate user response:**")
        bc1, bc2 = st.columns(2)
        upgraded = bc1.button("✅ Upgrade", use_container_width=True, type="primary")
        later    = bc2.button("⏭️ Try Later", use_container_width=True)

        if "upgraded_count" not in st.session_state:
            st.session_state.upgraded_count = 0
            st.session_state.later_count    = 0
            st.session_state.demo_log       = []

        if upgraded:
            result = api_post("/api/demo/respond", {
                "segment_name": seg_choice,
                "ab_group":     group_choice,
                "decision":     "upgraded",
            })
            if result is not None:
                st.session_state.upgraded_count += 1
                st.session_state.demo_log.insert(0, f"✅ {seg_choice.title()} · {group_choice} → **upgraded**")
                st.success("Upgrade recorded!")
                st.rerun()

        if later:
            result = api_post("/api/demo/respond", {
                "segment_name": seg_choice,
                "ab_group":     group_choice,
                "decision":     "try_later",
            })
            if result is not None:
                st.session_state.later_count += 1
                st.session_state.demo_log.insert(0, f"⏭️ {seg_choice.title()} · {group_choice} → try later")
                st.rerun()

        # Counters
        m1, m2 = st.columns(2)
        m1.metric("Upgraded",  st.session_state.upgraded_count)
        m2.metric("Try Later", st.session_state.later_count)

        if st.button("Clear log"):
            st.session_state.upgraded_count = 0
            st.session_state.later_count    = 0
            st.session_state.demo_log       = []
            st.rerun()

    with col_right:
        st.markdown("**Response log — backend events**")
        if st.session_state.demo_log:
            for entry in st.session_state.demo_log[:12]:
                st.markdown(f"- {entry}")
        else:
            st.caption("No responses yet. Simulate a user response on the left →")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — CAMPAIGN EDITOR
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📣 Campaign Editor":
    st.title("Campaign Editor")
    st.caption("Edit messages, set channels and triggers, launch A/B tests")
    st.divider()

    # Global params
    params_raw = api_get("/api/global-params") or []
    params_map = {p["key"]: p for p in params_raw}

    st.subheader("⚙️ Global Parameters")
    gp1, gp2, gp3 = st.columns(3)

    with gp1:
        price_val = st.number_input(
            "Pro price (AMD)",
            value=int(params_map.get("pro_price_amd", {}).get("value", 2900)),
            step=100, key="price_input",
        )
        if st.button("Save price", key="save_price"):
            api_put("/api/global-params/pro_price_amd", {"value": str(price_val)})
            st.success("Saved")
            st.rerun()

    with gp2:
        disc_val = st.number_input(
            "Discount % (dormant)",
            value=int(params_map.get("dormant_discount", {}).get("value", 20)),
            step=1, key="disc_input",
        )
        if st.button("Save discount", key="save_disc"):
            api_put("/api/global-params/dormant_discount", {"value": str(disc_val)})
            st.success("Saved")
            st.rerun()

    with gp3:
        tmpl_val = st.number_input(
            "Template count",
            value=int(params_map.get("template_count", {}).get("value", 120)),
            step=10, key="tmpl_input",
        )
        if st.button("Save templates", key="save_tmpl"):
            api_put("/api/global-params/template_count", {"value": str(tmpl_val)})
            st.success("Saved")
            st.rerun()

    st.divider()

    # Campaign cards
    campaigns = api_get("/api/campaigns") or []
    if not campaigns:
        st.info("No campaigns found.")
    else:
        for i in range(0, len(campaigns), 2):
            row = campaigns[i : i + 2]
            cols = st.columns(len(row))
            for col, c in zip(cols, row):
                cid     = c["campaign_id"]
                seg     = c.get("segment_name", "")
                label   = c.get("segment_label", seg.title())
                status  = c.get("status", "draft")
                channel = c.get("channel", "")
                trigger = c.get("trigger_event", "")
                msg_obj = c.get("active_message") or {}
                body    = msg_obj.get("body", "")
                color   = {"power":"#00b87a","growing":"#3b82f6","casual":"#f59e0b","dormant":"#9ca3af"}.get(seg,"#111")
                badge   = "badge-running" if status=="running" else "badge-draft"

                with col:
                    st.markdown(
                        f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">'
                        f'<span style="font-weight:700;color:{color}">{label}</span>'
                        f'<span class="{badge}">{status.upper()}</span>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                    st.caption(f"Channel: {channel.replace('_',' ').title()} · Trigger: {trigger.replace('_',' ').title()}")

                    # Message editor
                    new_body = st.text_area(
                        "Message template",
                        value=body,
                        height=100,
                        key=f"body_{cid}",
                    )

                    # Preview with variable substitution
                    preview = new_body \
                        .replace("{{price}}", str(price_val)) \
                        .replace("{{discount}}", str(disc_val)) \
                        .replace("{{template_count}}", str(tmpl_val)) \
                        .replace("{{export_count}}", "9") \
                        .replace("{{paywall_hits}}", "7")
                    st.caption(f"**Preview:** {preview}")

                    ba, bb = st.columns(2)
                    if ba.button("💾 Save", key=f"save_{cid}"):
                        api_put(f"/api/campaigns/{cid}/message", {"body": new_body})
                        st.success("Saved")
                        st.rerun()

                    if status == "draft":
                        if bb.button("🚀 Launch", key=f"launch_{cid}", type="primary"):
                            api_post(f"/api/campaigns/{cid}/launch")
                            st.success(f"{label} launched!")
                            st.rerun()
                    else:
                        if bb.button("↩️ Reset", key=f"reset_{cid}"):
                            api_delete(f"/api/campaigns/{cid}/reset")
                            st.success(f"{label} reset to draft")
                            st.rerun()

                    st.divider()
