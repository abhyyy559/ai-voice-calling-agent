"""Campaign results export (CSV with BOM / XLSX with bold header)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Campaign
from app.services.export_service import (
    CSV_MEDIA_TYPE,
    XLSX_MEDIA_TYPE,
    export_csv,
    export_xlsx,
)

router = APIRouter(prefix="/api", tags=["export"])


@router.get("/campaigns/{campaign_id}/export")
def export_campaign_results(
    campaign_id: int, format: str = "csv", db: Session = Depends(get_db)
) -> Response:
    campaign = db.get(Campaign, campaign_id)
    if campaign is None:
        raise HTTPException(status_code=404, detail="campaign not found")
    slug = campaign.name.lower().replace(" ", "_")[:40] or f"campaign_{campaign_id}"
    if format == "csv":
        content = export_csv(db, campaign)
        return Response(
            content=content,
            media_type=CSV_MEDIA_TYPE,
            headers={"Content-Disposition": f'attachment; filename="{slug}.csv"'},
        )
    if format == "xlsx":
        content = export_xlsx(db, campaign)
        return Response(
            content=content,
            media_type=XLSX_MEDIA_TYPE,
            headers={"Content-Disposition": f'attachment; filename="{slug}.xlsx"'},
        )
    raise HTTPException(status_code=422, detail="format must be csv or xlsx")
