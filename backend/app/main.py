import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

<<<<<<< HEAD
=======
from app.config import settings
>>>>>>> 3e2bbc2 (feat(deployment): add AWS EC2 CI/CD and production deployment infrastructure)
from app.database import AsyncSessionLocal, init_db
from app.redis_client import close_redis, get_redis
from app.routers import agent, alerts, routes, simulation, sse, stops, vehicles
from app.services.seeder import cache_route_modes, seed_routes, seed_stops

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="TransitTwin AI",
    description="Digital twin backend for HSL public transport — Helsinki, Espoo, Vantaa",
    version="0.1.0",
)

<<<<<<< HEAD
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
=======
_cors_origins = [o.strip() for o in settings.BACKEND_CORS_ORIGINS.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
>>>>>>> 3e2bbc2 (feat(deployment): add AWS EC2 CI/CD and production deployment infrastructure)
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stops.router, prefix="/api")
app.include_router(routes.router, prefix="/api")
app.include_router(vehicles.router, prefix="/api")
app.include_router(alerts.router, prefix="/api")
app.include_router(sse.router, prefix="/api")
app.include_router(simulation.router, prefix="/api")
app.include_router(agent.router, prefix="/api")


@app.on_event("startup")
async def startup() -> None:
    logger.info("Initialising database schema…")
    await init_db()

    try:
        logger.info("Seeding stops and routes from Digitransit…")
        redis = await get_redis()
        async with AsyncSessionLocal() as db:
            await seed_stops(db)
            await seed_routes(db)
            await cache_route_modes(db, redis)
        logger.info("Seeding complete")
    except Exception as exc:
        logger.warning(
            "Digitransit seeding skipped — backend still starts. "
            "Fix DIGITRANSIT_API_KEY and restart to seed. Error: %s", exc
        )

    logger.info("TransitTwin AI backend ready")


@app.on_event("shutdown")
async def shutdown() -> None:
    await close_redis()


@app.get("/health")
async def health():
    return {"status": "ok"}
