import json
import logging

from arq import cron
from arq.connections import RedisSettings

from app.config import settings
from app.services.gtfs_rt import GtfsRtService

logger = logging.getLogger(__name__)


def _infer_mode(route_id: str | None, route_modes: dict) -> str | None:
    """Return transport mode for a route ID.

    Priority:
    1. Look up in the DB-seeded cache (hsl:route_modes).
    2. Fall back to pattern matching on the HSL route ID format.

    HSL ID patterns (strip optional 'HSL:' prefix, uppercase):
      Metro : contains 'M'                  31M1, 31M2
      Ferry : exactly '1019'                Suomenlinna
      Tram  : leading digits 1001–1012      tram lines 1–12
      Rail  : leading digits 3001–3030      commuter rail 3001A/D/E/F/I/K/L/P/U/Z
      Bus   : everything else

    NOTE: HSL commuter rail route IDs have a letter suffix (e.g. "3001A")
    so we extract the *leading digit run* rather than testing isdigit().
    """
    if not route_id:
        return None
    cached = route_modes.get(route_id)
    if cached:
        return cached

    code = route_id.removeprefix("HSL:").upper()

    # Metro: 31M1 / 31M2 — must check before digit extraction (code is not pure digits)
    if "M" in code:
        return "METRO"

    # Ferry
    if code == "1019":
        return "FERRY"

    # Extract the leading numeric prefix — handles "3001A" → 3001, "1007" → 1007, "550" → 550
    i = 0
    while i < len(code) and code[i].isdigit():
        i += 1
    if i > 0:
        n = int(code[:i])
        if 1001 <= n <= 1012:   # tram lines 1–12
            return "TRAM"
        if 3001 <= n <= 3030:   # commuter rail (4-digit 3xxx + optional letter)
            return "RAIL"

    return "BUS"


async def poll_vehicles(ctx: dict) -> None:
    try:
        service = GtfsRtService()
        vehicles = await service.fetch_vehicle_positions()

        # Enrich with mode from the route→mode cache built during startup seeding
        raw_modes = await ctx["redis"].get("hsl:route_modes")
        route_modes: dict = json.loads(raw_modes) if raw_modes else {}
        for v in vehicles:
            v["mode"] = _infer_mode(v.get("route_id"), route_modes)

        await ctx["redis"].set("hsl:vehicles", json.dumps(vehicles), ex=30)

        # Log mode distribution once per poll so missing modes are visible
        from collections import Counter
        dist = Counter(v.get("mode") or "null" for v in vehicles)
        logger.info("Vehicles stored: %d | modes: %s", len(vehicles), dict(dist))
    except Exception:
        logger.exception("poll_vehicles failed")


async def poll_alerts(ctx: dict) -> None:
    try:
        service = GtfsRtService()
        alerts = await service.fetch_service_alerts()
        await ctx["redis"].set("hsl:alerts", json.dumps(alerts), ex=120)
        logger.debug("Stored %d alerts", len(alerts))
    except Exception:
        logger.exception("poll_alerts failed")


async def poll_trip_updates(ctx: dict) -> None:
    try:
        service = GtfsRtService()
        updates = await service.fetch_trip_updates()
        await ctx["redis"].set("hsl:trip_updates", json.dumps(updates), ex=30)
        logger.debug("Stored %d trip updates", len(updates))
    except Exception:
        logger.exception("poll_trip_updates failed")


class WorkerSettings:
    functions = [poll_vehicles, poll_alerts, poll_trip_updates]
    cron_jobs = [
        # every 5 seconds
        cron(poll_vehicles, second={0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55}),
        # every 30 seconds
        cron(poll_alerts, second={0, 30}),
        # every 10 seconds
        cron(poll_trip_updates, second={0, 10, 20, 30, 40, 50}),
    ]
    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)
    max_jobs = 10
    job_timeout = 10
