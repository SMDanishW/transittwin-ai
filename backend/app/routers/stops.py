from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.stop import Stop
from app.schemas.stop import StopListResponse, StopSchema

router = APIRouter(prefix="/stops", tags=["stops"])


@router.get("", response_model=StopListResponse)
async def list_stops(
    mode: int | None = Query(None, description="Filter by vehicle type (0=tram,1=metro,2=rail,3=bus)"),
    limit: int = Query(500, le=2000),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
):
    q = select(Stop)
    if mode is not None:
        q = q.where(Stop.vehicle_type == mode)
    total_q = select(func.count()).select_from(q.subquery())
    total = (await db.execute(total_q)).scalar_one()
    rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
    return StopListResponse(total=total, stops=[StopSchema.model_validate(r) for r in rows])


@router.get("/{stop_id}", response_model=StopSchema)
async def get_stop(stop_id: str, db: AsyncSession = Depends(get_db)):
    row = await db.get(Stop, stop_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Stop not found")
    return StopSchema.model_validate(row)
