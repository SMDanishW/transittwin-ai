import asyncio
import json

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from app.redis_client import get_redis

router = APIRouter(prefix="/sse", tags=["sse"])

_HEADERS = {
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no",
}


async def _vehicle_stream(request: Request, redis):
    """Push vehicle positions every 3 seconds until the client disconnects."""
    while True:
        if await request.is_disconnected():
            break
        raw = await redis.get("hsl:vehicles")
        payload = raw if raw else "[]"
        yield f"data: {payload}\n\n"
        await asyncio.sleep(3)


async def _alert_stream(request: Request, redis):
    """Push service alerts every 15 seconds until the client disconnects."""
    while True:
        if await request.is_disconnected():
            break
        raw = await redis.get("hsl:alerts")
        payload = raw if raw else "[]"
        yield f"data: {payload}\n\n"
        await asyncio.sleep(15)


@router.get("/vehicles")
async def sse_vehicles(request: Request, redis=Depends(get_redis)):
    return StreamingResponse(
        _vehicle_stream(request, redis),
        media_type="text/event-stream",
        headers=_HEADERS,
    )


@router.get("/alerts")
async def sse_alerts(request: Request, redis=Depends(get_redis)):
    return StreamingResponse(
        _alert_stream(request, redis),
        media_type="text/event-stream",
        headers=_HEADERS,
    )
