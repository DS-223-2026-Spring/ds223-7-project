"""
User Demo screen endpoints.

GET  /api/demo/message/{segment_name}  → rendered upgrade message
POST /api/demo/respond                 → record user decision
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from db import get_db
from schemas.demo import DemoMessageOut, DemoResponse

router = APIRouter(prefix="/api/demo", tags=["demo"])


@router.get("/message/{segment_name}", response_model=DemoMessageOut)
def get_demo_message(segment_name: str, db: Session = Depends(get_db)):
    """Get the rendered upgrade message for a segment.

    This powers the phone mockup on the User Demo screen.
    It reads the active message template for the segment's campaign,
    then substitutes {{placeholders}} with global_params values.
    """
    # Fetch campaign + active message + segment info in one query
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
    # Dynamic user-level placeholders — use dummy values for now
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


@router.post("/respond")
def record_demo_response(payload: DemoResponse, db: Session = Depends(get_db)):
    """Record a user's upgrade / try-later decision from the Demo screen.

    Inserts a row into conversion_outcomes.  In the real product this
    would look up the user and test — for the demo we use a dummy user.
    """
    # For the demo, pick a random user from the segment
    user = db.execute(
        text("""
            SELECT u.user_id
            FROM users u
            JOIN user_segments us ON us.user_id = u.user_id AND us.expires_at IS NULL
            JOIN segments s      ON s.segment_id = us.segment_id
            WHERE s.name = :seg
            LIMIT 1
        """),
        {"seg": payload.segment_name},
    ).mappings().first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"No users found in segment '{payload.segment_name}'",
        )

    # Get the campaign for this segment
    campaign = db.execute(
        text("""
            SELECT c.campaign_id, c.active_message_id
            FROM campaigns c
            JOIN segments s ON s.segment_id = c.segment_id
            WHERE s.name = :seg
        """),
        {"seg": payload.segment_name},
    ).mappings().first()

    db.execute(
        text("""
            INSERT INTO conversion_outcomes
                (user_id, campaign_id, message_id, group_type, decision,
                 revenue_amd)
            VALUES
                (:uid, :cid, :mid, :grp, :dec,
                 CASE WHEN :dec = 'upgraded' THEN 2900 ELSE NULL END)
        """),
        {
            "uid": user["user_id"],
            "cid": campaign["campaign_id"] if campaign else None,
            "mid": campaign["active_message_id"] if campaign else None,
            "grp": payload.ab_group,
            "dec": payload.decision,
        },
    )
    db.commit()

    return {
        "status": "recorded",
        "decision": payload.decision,
        "segment": payload.segment_name,
    }
