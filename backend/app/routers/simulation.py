from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.simulation import SimulationRequest, SimulationResult
from app.services.simulation import SimulationEngine

router = APIRouter(prefix="/simulation", tags=["simulation"])


@router.post("/run", response_model=SimulationResult)
async def run_simulation(
    req: SimulationRequest,
    db: AsyncSession = Depends(get_db),
) -> SimulationResult:
    return await SimulationEngine().run(req, db)
