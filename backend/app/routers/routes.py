from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.route import Route
from app.schemas.route import RouteListResponse, RouteSchema

router = APIRouter(prefix="/routes", tags=["routes"])


@router.get("", response_model=RouteListResponse)
async def list_routes(
    mode: str | None = Query(None, description="Filter by mode (BUS, TRAM, RAIL, METRO, FERRY)"),
    limit: int = Query(200, le=1000),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
):
    q = select(Route)
    if mode:
        q = q.where(Route.mode == mode.upper())
    total_q = select(func.count()).select_from(q.subquery())
    total = (await db.execute(total_q)).scalar_one()
    rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
    return RouteListResponse(total=total, routes=[RouteSchema.model_validate(r) for r in rows])


@router.get("/{route_id}", response_model=RouteSchema)
async def get_route(route_id: str, db: AsyncSession = Depends(get_db)):
    row = await db.get(Route, route_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Route not found")
    return RouteSchema.model_validate(row)
