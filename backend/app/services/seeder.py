import json
import logging

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.route import Route
from app.models.stop import Stop
from app.services.digitransit import DigitransitService
from app.services.mock_seed_data import MOCK_ROUTES, MOCK_STOPS

logger = logging.getLogger(__name__)


def _stop_rows(stops: list[dict]) -> list[dict]:
    return [
        {
            "id": s["id"],
            "name": s["name"],
            "code": s["code"],
            "vehicle_type": s["vehicle_type"],
            "platform_code": s["platform_code"],
            "zone_id": s["zone_id"],
            "lat": s["lat"],
            "lon": s["lon"],
            "geom": f"SRID=4326;POINT({s['lon']} {s['lat']})",
        }
        for s in stops
    ]


def _route_rows(routes: list[dict]) -> list[dict]:
    return [
        {
            "id": r["id"],
            "short_name": r["short_name"],
            "long_name": r["long_name"],
            "mode": r["mode"],
            "color": r["color"],
            "agency_name": r["agency_name"],
        }
        for r in routes
    ]


async def seed_stops(db: AsyncSession) -> None:
    if (await db.execute(select(Stop).limit(1))).first() is not None:
        logger.info("Stops already seeded — skipping")
        return

    if settings.USE_MOCK_SEED:
        logger.info("USE_MOCK_SEED=true — using local fixture stops")
        stops = MOCK_STOPS
    else:
        stops = await DigitransitService().get_stops()

    rows = _stop_rows(stops)
    if rows:
        await db.execute(insert(Stop).values(rows).on_conflict_do_nothing(index_elements=["id"]))
        await db.commit()
        logger.info("Seeded %d stops", len(rows))


async def seed_routes(db: AsyncSession) -> None:
    if (await db.execute(select(Route).limit(1))).first() is not None:
        logger.info("Routes already seeded — skipping")
        return

    if settings.USE_MOCK_SEED:
        logger.info("USE_MOCK_SEED=true — using local fixture routes")
        routes = MOCK_ROUTES
    else:
        routes = await DigitransitService().get_routes()

    rows = _route_rows(routes)
    if rows:
        await db.execute(insert(Route).values(rows).on_conflict_do_nothing(index_elements=["id"]))
        await db.commit()
        logger.info("Seeded %d routes", len(rows))


async def cache_route_modes(db: AsyncSession, redis) -> None:
    """Build a {route_id: mode} dict in Redis so the Arq worker can enrich vehicles."""
    rows = (await db.execute(select(Route.id, Route.mode))).all()
    mapping = {row.id: row.mode for row in rows if row.mode}
    await redis.set("hsl:route_modes", json.dumps(mapping), ex=86400)
    logger.info("Cached %d route→mode mappings in Redis", len(mapping))
