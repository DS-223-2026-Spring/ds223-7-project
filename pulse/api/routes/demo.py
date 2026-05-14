"""
User Demo screen endpoints.

GET  /api/demo/message/{segment_name}  → rendered upgrade message
POST /api/demo/respond                 → record user decision
GET  /api/demo/stats                   → live response counts per segment
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import get_db
from schema import DemoMessageOut, DemoResponse, DemoRespondResult

router = APIRouter(prefix="/api/demo", tags=["demo"])


# ── GET /api/demo/stats ──────────────────────────────────────────────────────

@router.get("/stats", response_model=list[dict])
def get_demo_stats(db: Session = Depends(get_db)):
    """Live response counts from conversion_outcomes, grouped by segment + decision."""
    try:
        rows = db.execute(text("""
            SELECT
                s.name          AS segment_name,
                co.decision     AS response,
                COUNT(*)        AS count
            FROM conversion_outcomes co
            JOIN users u        ON u.user_id    = co.user_id
            JOIN user_segments us ON us.user_id = u.user_id AND us.expires_at IS NULL
            JOIN segments s     ON s.segment_id = us.segment_id
            GROUP BY s.name, co.decision
            ORDER BY s.name, co.decision
        """)).mappings().all()
        return [{"segment_name": r["segment_name"], "response": r["response"], "count": int(r["count"])} for r in rows]
    except Exception:
        return []


@router.get("/message/{segment_name}", response_model=DemoMessageOut,
            responses={200: {"description": "Rendered upgrade message for the segment"}})
def get_demo_message(segment_name: str, db: Session = Depends(get_db)):
    """Get the rendered upgrade message for a randomly assigned user in this segment.

    Picks a random user from ab_assignments so control users see the
    generic baseline message and treatment users see the campaign message.
    """
    # Pick a random ab-assigned user to simulate realistic group distribution
    assignment = db.execute(
        text("""
            SELECT aa.user_id, aa.test_id, aa.group_type
            FROM ab_assignments aa
            JOIN ab_tests t  ON t.test_id    = aa.test_id
            JOIN segments s  ON s.segment_id = t.segment_id
            WHERE s.name = :seg
            ORDER BY random()
            LIMIT 1
        """),
        {"seg": segment_name},
    ).mappings().first()

    if not assignment:
        raise HTTPException(status_code=404,
                            detail=f"No A/B assignments found for segment '{segment_name}'")

    group = assignment["group_type"]  # 'control' or 'treatment'

    # Fetch campaign + both message bodies
    row = db.execute(
        text("""
            SELECT
                s.name        AS segment_name,
                s.label       AS segment_label,
                s.color_hex,
                c.channel,
                c.trigger_event,
                ctrl.body     AS control_body,
                treat.body    AS treatment_body
            FROM campaigns c
            JOIN segments s ON s.segment_id = c.segment_id
            LEFT JOIN message_templates ctrl  ON ctrl.message_id  = c.control_message_id
            LEFT JOIN message_templates treat ON treat.message_id = c.active_message_id
            WHERE s.name = :seg
        """),
        {"seg": segment_name},
    ).mappings().first()

    if not row:
        raise HTTPException(status_code=404,
                            detail=f"No campaign found for segment '{segment_name}'")

    # Choose the correct message body based on group
    body = row["control_body"] if group == "control" else row["treatment_body"]
    if not body:
        body = "Upgrade to Pulse Pro and unlock all premium features for AMD 2,900/month."

    # Render placeholders using global_params
    params_rows = db.execute(text("SELECT key, value FROM global_params")).mappings().all()
    param_map = {r["key"]: r["value"] for r in params_rows}

    rendered = body
    rendered = rendered.replace("{{price}}", param_map.get("pro_price_amd", "2900"))
    rendered = rendered.replace("{{discount}}", param_map.get("dormant_discount", "20"))
    rendered = rendered.replace("{{template_count}}", param_map.get("template_count", "120"))
    rendered = rendered.replace("{{export_count}}", "47")
    rendered = rendered.replace("{{paywall_hits}}", "23")

    return DemoMessageOut(
        segment_name=row["segment_name"],
        segment_label=row["segment_label"],
        color_hex=row["color_hex"],
        rendered_body=rendered,
        channel=row["channel"],
        trigger_event=row["trigger_event"],
        ab_group=group,
        user_id=str(assignment["user_id"]),
        test_id=str(assignment["test_id"]),
    )


@router.post("/respond", response_model=DemoRespondResult,
             responses={200: {"description": "Confirmation that the decision was recorded"}})
def record_demo_response(payload: DemoResponse, db: Session = Depends(get_db)):
    """Record a user's upgrade / try-later decision from the Demo screen.

    Uses the user_id, test_id and ab_group returned by GET /api/demo/message
    so control and treatment responses are correctly attributed.
    """
    campaign = db.execute(
        text("""
            SELECT c.campaign_id,
                   CASE WHEN :grp = 'control' THEN c.control_message_id
                        ELSE c.active_message_id END AS message_id
            FROM campaigns c
            JOIN segments s ON s.segment_id = c.segment_id
            WHERE s.name = :seg
        """),
        {"seg": payload.segment_name, "grp": payload.ab_group},
    ).mappings().first()

    actual_group = payload.ab_group

    db.execute(
        text("""
            INSERT INTO conversion_outcomes
                (user_id, test_id, campaign_id, message_id, group_type, decision,
                 revenue_amd)
            VALUES
                (:uid, :tid, :cid, :mid, CAST(:grp AS ab_group),
                 CAST(:dec AS upgrade_decision),
                 CASE WHEN :dec = 'upgraded' THEN 2900 ELSE NULL END)
        """),
        {
            "uid": payload.user_id,
            "tid": payload.test_id,
            "cid": campaign["campaign_id"] if campaign else None,
            "mid": campaign["message_id"] if campaign else None,
            "grp": actual_group,
            "dec": payload.decision,
        },
    )
    db.commit()

    return {
        "status": "recorded",
        "decision": payload.decision,
        "ab_group": actual_group,
        "segment": payload.segment_name,
    }
