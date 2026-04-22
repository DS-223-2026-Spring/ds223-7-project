"""
Campaign Editor screen endpoints.

GET    /api/campaigns                   → all campaigns with active message
GET    /api/campaigns/{id}              → single campaign
PUT    /api/campaigns/{id}              → update channel / trigger
PUT    /api/campaigns/{id}/message      → update the active message body
POST   /api/campaigns/{id}/launch       → set status to 'running'
DELETE /api/campaigns/{id}/reset        → reset status back to 'draft'
GET    /api/global-params               → all global params
PUT    /api/global-params/{key}         → update a param value
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from db import get_db
from schemas.campaigns import (
    CampaignOut,
    CampaignUpdate,
    GlobalParamOut,
    GlobalParamUpdate,
    MessageTemplateOut,
    MessageUpdate,
)

router = APIRouter(prefix="/api", tags=["campaigns"])


# ── Helpers ──────────────────────────────────────────────────────────

def _build_campaign(row, msg_row=None) -> CampaignOut:
    """Convert a raw DB row into a CampaignOut schema."""
    active_msg = None
    if msg_row:
        active_msg = MessageTemplateOut(
            message_id=str(msg_row["message_id"]),
            source=msg_row["source"],
            body=msg_row["body"],
            body_rendered=msg_row.get("body_rendered"),
            is_active=msg_row["is_active"],
            created_at=msg_row["created_at"],
            updated_at=msg_row["updated_at"],
        )
    return CampaignOut(
        campaign_id=str(row["campaign_id"]),
        segment_name=row["segment_name"],
        segment_label=row["segment_label"],
        color_hex=row["color_hex"],
        channel=row["channel"],
        trigger_event=row["trigger_event"],
        status=row["status"],
        active_message=active_msg,
        created_at=row["created_at"],
        launched_at=row.get("launched_at"),
    )


_CAMPAIGNS_SQL = text("""
    SELECT
        c.campaign_id,
        s.name  AS segment_name,
        s.label AS segment_label,
        s.color_hex,
        c.channel,
        c.trigger_event,
        c.status,
        c.active_message_id,
        c.created_at,
        c.launched_at
    FROM campaigns c
    JOIN segments s ON s.segment_id = c.segment_id
    ORDER BY s.name
""")


# ── Campaign CRUD ────────────────────────────────────────────────────

@router.get("/campaigns", response_model=list[CampaignOut])
def list_campaigns(db: Session = Depends(get_db)):
    """All four campaign cards — one per segment — with their active
    message template attached."""
    try:
        rows = db.execute(_CAMPAIGNS_SQL).mappings().all()
        result = []
        for r in rows:
            msg_row = None
            if r.get("active_message_id"):
                msg_row = db.execute(
                    text("SELECT * FROM message_templates WHERE message_id = :mid"),
                    {"mid": r["active_message_id"]},
                ).mappings().first()
            result.append(_build_campaign(r, msg_row))
        return result
    except Exception:
        return []


@router.get("/campaigns/{campaign_id}", response_model=CampaignOut)
def get_campaign(campaign_id: str, db: Session = Depends(get_db)):
    """Single campaign by ID."""
    row = db.execute(
        text("""
            SELECT c.campaign_id, s.name AS segment_name,
                   s.label AS segment_label, s.color_hex,
                   c.channel, c.trigger_event, c.status,
                   c.active_message_id, c.created_at, c.launched_at
            FROM campaigns c
            JOIN segments s ON s.segment_id = c.segment_id
            WHERE c.campaign_id = :cid
        """),
        {"cid": campaign_id},
    ).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Campaign not found")

    msg_row = None
    if row.get("active_message_id"):
        msg_row = db.execute(
            text("SELECT * FROM message_templates WHERE message_id = :mid"),
            {"mid": row["active_message_id"]},
        ).mappings().first()
    return _build_campaign(row, msg_row)


@router.put("/campaigns/{campaign_id}", response_model=CampaignOut)
def update_campaign(
    campaign_id: str, payload: CampaignUpdate, db: Session = Depends(get_db)
):
    """Update a campaign's channel and/or trigger (Campaign Editor
    dropdowns)."""
    sets = []
    params: dict = {"cid": campaign_id}
    if payload.channel is not None:
        sets.append("channel = :channel")
        params["channel"] = payload.channel
    if payload.trigger_event is not None:
        sets.append("trigger_event = :trigger")
        params["trigger"] = payload.trigger_event

    if not sets:
        raise HTTPException(status_code=400, detail="Nothing to update")

    db.execute(
        text(f"UPDATE campaigns SET {', '.join(sets)} WHERE campaign_id = :cid"),
        params,
    )
    db.commit()
    return get_campaign(campaign_id, db)


@router.put("/campaigns/{campaign_id}/message", response_model=CampaignOut)
def update_message(
    campaign_id: str, payload: MessageUpdate, db: Session = Depends(get_db)
):
    """Update the active message body — this is what happens when the PM
    edits the textarea in the Campaign Editor.

    Sets source to 'user_edited' and updates the body.
    """
    # Find the active message for this campaign
    msg = db.execute(
        text("""
            SELECT message_id FROM message_templates
            WHERE campaign_id = :cid AND is_active = TRUE
        """),
        {"cid": campaign_id},
    ).mappings().first()

    if not msg:
        raise HTTPException(status_code=404, detail="No active message for campaign")

    db.execute(
        text("""
            UPDATE message_templates
            SET body = :body, source = 'user_edited'
            WHERE message_id = :mid
        """),
        {"body": payload.body, "mid": msg["message_id"]},
    )
    db.commit()
    return get_campaign(campaign_id, db)


@router.post("/campaigns/{campaign_id}/launch", response_model=CampaignOut)
def launch_campaign(campaign_id: str, db: Session = Depends(get_db)):
    """Set campaign status to 'running' and record launched_at.

    This is the 'Launch A/B test' button in the prototype.
    """
    db.execute(
        text("""
            UPDATE campaigns
            SET status = 'running', launched_at = now()
            WHERE campaign_id = :cid
        """),
        {"cid": campaign_id},
    )
    db.commit()
    return get_campaign(campaign_id, db)


@router.delete("/campaigns/{campaign_id}/reset", response_model=CampaignOut)
def reset_campaign(campaign_id: str, db: Session = Depends(get_db)):
    """Reset campaign back to 'draft' — the Reset button in the prototype."""
    db.execute(
        text("""
            UPDATE campaigns
            SET status = 'draft', launched_at = NULL
            WHERE campaign_id = :cid
        """),
        {"cid": campaign_id},
    )
    db.commit()
    return get_campaign(campaign_id, db)


# ── Global Params ────────────────────────────────────────────────────

@router.get("/global-params", response_model=list[GlobalParamOut])
def list_global_params(db: Session = Depends(get_db)):
    """All shared Campaign Editor params: pro_price_amd, dormant_discount,
    template_count."""
    try:
        rows = db.execute(
            text("SELECT key, value, description FROM global_params ORDER BY key")
        ).mappings().all()
        return [GlobalParamOut(**r) for r in rows]
    except Exception:
        return []


@router.put("/global-params/{key}", response_model=GlobalParamOut)
def update_global_param(
    key: str, payload: GlobalParamUpdate, db: Session = Depends(get_db)
):
    """Update one global param — e.g. changing the Pro price from 2900 to
    3500."""
    result = db.execute(
        text("""
            UPDATE global_params SET value = :val, updated_at = now()
            WHERE key = :key
            RETURNING key, value, description
        """),
        {"key": key, "val": payload.value},
    ).mappings().first()

    if not result:
        raise HTTPException(status_code=404, detail=f"Param '{key}' not found")

    db.commit()
    return GlobalParamOut(**result)
