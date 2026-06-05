import json

from fastapi import APIRouter, Depends

from app.redis_client import get_redis
from app.schemas.vehicle import VehicleListResponse, VehicleSchema

router = APIRouter(prefix="/vehicles", tags=["vehicles"])


@router.get("", response_model=VehicleListResponse)
async def list_vehicles(redis=Depends(get_redis)):
    raw = await redis.get("hsl:vehicles")
    if not raw:
        return VehicleListResponse(count=0, vehicles=[])
    vehicles = [VehicleSchema(**v) for v in json.loads(raw)]
    return VehicleListResponse(count=len(vehicles), vehicles=vehicles)
