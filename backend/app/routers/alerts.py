import json

from fastapi import APIRouter, Depends

from app.redis_client import get_redis
from app.schemas.alert import AlertListResponse, AlertSchema

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=AlertListResponse)
async def list_alerts(redis=Depends(get_redis)):
    raw = await redis.get("hsl:alerts")
    if not raw:
        return AlertListResponse(count=0, alerts=[])
    alerts = [AlertSchema(**a) for a in json.loads(raw)]
    return AlertListResponse(count=len(alerts), alerts=alerts)
