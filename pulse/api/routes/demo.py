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


def _render(body: str, param_map: dict) -> str:
    """Substitute {{placeholders}} with global_params values."""
    body = body.replace("{{price}}",          param_map.get("pro_price_amd", "2900"))
    body = body.replace("{{discount}}",       param_map.get("dormant_discount", "20"))
    body = body.replace("{{template_count}}", param_map.get("template_count", "120"))
    body = body.replace("{{export_count}}",   "47")
    body = body.replace("{{paywall_hits}}",   "23")
    return body


@router.get("/message/{segment_name}", response_model=DemoMessageOut,
            responses={200: {"description": "Both control and treatment messages + campaign status"}})
def get_demo_message(segment_name: str, db: Session = Depends(get_db)):
    """Return both control and treatment messages for the segment.

    If campaign is running  → frontend shows both side by side.
    If campaign is not running → frontend shows only the control message.
    Also returns a random assigned user (user_id + test_id) for attribution.
    """
    # Pick one random ab-assigned user (for test_id / attribution)
    assignment = db.execute(
        text("""
            SELECT aa.user_id, aa.test_id
            FROM ab_assignments aa
            JOIN ab_tests t ON t.test_id    = aa.test_id
            JOIN segments s ON s.segment_id = t.segment_id
            WHERE s.name = :seg
            ORDER BY random()
            LIMIT 1
        """),
        {"seg": segment_name},
    ).mappings().first()

    if not assignment:
        raise HTTPException(status_code=404,
                            detail=f"No A/B assignments found for segment '{segment_name}'")

    row = db.execute(
        text("""
            SELECT
                s.name   AS segment_name,
                s.label  AS segment_label,
                s.color_hex,
                c.status AS campaign_status,
                c.channel,
                c.trigger_event,
                COALESCE(ctrl.body,
                    'Upgrade to Pulse Pro and unlock all premium features for AMD 2,900/month.'
                )          AS control_body,
                treat.body AS treatment_body
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

    params_rows = db.execute(text("SELECT key, value FROM global_params")).mappings().all()
    param_map = {r["key"]: r["value"] for r in params_rows}

    return DemoMessageOut(
        segment_name=row["segment_name"],
        segment_label=row["segment_label"],
        color_hex=row["color_hex"],
        campaign_status=row["campaign_status"],
        channel=row["channel"],
        trigger_event=row["trigger_event"],
        control_body=_render(row["control_body"], param_map),
        treatment_body=_render(row["treatment_body"] or "", param_map),
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
