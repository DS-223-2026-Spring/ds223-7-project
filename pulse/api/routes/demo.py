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
    """Get the rendered upgrade message for a segment.

    Powers the phone mockup on the User Demo screen.
    Substitutes {{placeholders}} with global_params values.
    """
    row = db.execute(
        text("""
            SELECT
                s.name  AS segment_name,
                s.label AS segment_label,
                s.color_hex,
                mt.body,
                c.channel,
                c.trigger_event
            FROM campaigns c
            JOIN segments s          ON s.segment_id  = c.segment_id
            JOIN message_templates mt ON mt.message_id = c.active_message_id
            WHERE s.name = :seg
        """),
        {"seg": segment_name},
    ).mappings().first()

    if not row:
        raise HTTPException(
            status_code=404,
            detail=f"No campaign found for segment '{segment_name}'",
        )

    # Render placeholders using global_params
    params_rows = db.execute(
        text("SELECT key, value FROM global_params")
    ).mappings().all()
    param_map = {r["key"]: r["value"] for r in params_rows}

    rendered = row["body"]
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
    )


@router.post("/respond", response_model=DemoRespondResult,
             responses={200: {"description": "Confirmation that the decision was recorded"}})
def record_demo_response(payload: DemoResponse, db: Session = Depends(get_db)):
    """Record a user's upgrade / try-later decision from the Demo screen.

    Picks a random assigned user from the segment's A/B test so that
    test_id and group_type are populated in conversion_outcomes — this
    lets POST /api/ab-tests/run-analysis count demo responses correctly.
    """
    # Pick a random ab-assigned user from this segment (gives us test_id + group_type)
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
        {"seg": payload.segment_name},
    ).mappings().first()

    if not assignment:
        raise HTTPException(
            status_code=404,
            detail=f"No A/B assignments found for segment '{payload.segment_name}'",
        )

    campaign = db.execute(
        text("""
            SELECT c.campaign_id, c.active_message_id
            FROM campaigns c
            JOIN segments s ON s.segment_id = c.segment_id
            WHERE s.name = :seg
        """),
        {"seg": payload.segment_name},
    ).mappings().first()

    actual_group = assignment["group_type"]

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
            "uid": assignment["user_id"],
            "tid": assignment["test_id"],
            "cid": campaign["campaign_id"] if campaign else None,
            "mid": campaign["active_message_id"] if campaign else None,
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
