"""Campaign results export (CSV with BOM / XLSX with bold header), org-scoped."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import Campaign, User
from app.services.export_service import (
    CSV_MEDIA_TYPE,
    XLSX_MEDIA_TYPE,
    export_csv,
    export_xlsx,
)

router = APIRouter(prefix="/api", tags=["export"])


@router.get("/campaigns/{campaign_id}/export")
def export_campaign_results(
    campaign_id: int,
    format: str = "csv",
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    campaign = db.get(Campaign, campaign_id)
    if campaign is None or campaign.org_id != user.org_id:
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
