import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

_STOPS_QUERY = """
{
  stops {
    gtfsId
    name
    code
    vehicleType
    platformCode
    zoneId
    lat
    lon
  }
}
"""

_ROUTES_QUERY = """
{
  routes {
    gtfsId
    shortName
    longName
    mode
    color
    agency {
      name
    }
  }
}
"""


class DigitransitService:
    def __init__(self) -> None:
        self._headers = {
            "digitransit-subscription-key": settings.DIGITRANSIT_API_KEY,
            "Content-Type": "application/json",
        }

    async def _query(self, query: str) -> dict:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                settings.DIGITRANSIT_ROUTING_URL,
                json={"query": query},
                headers=self._headers,
            )
            response.raise_for_status()
            return response.json()

    async def get_stops(self) -> list[dict]:
        data = await self._query(_STOPS_QUERY)
        stops = data.get("data", {}).get("stops", []) or []
        result = []
        for s in stops:
            if s.get("lat") is None or s.get("lon") is None:
                continue
            result.append(
                {
                    "id": s["gtfsId"],
                    "name": s["name"],
                    "code": s.get("code"),
                    "vehicle_type": s.get("vehicleType"),
                    "platform_code": s.get("platformCode"),
                    "zone_id": s.get("zoneId"),
                    "lat": s["lat"],
                    "lon": s["lon"],
                }
            )
        logger.info("Fetched %d stops from Digitransit", len(result))
        return result

    async def get_routes(self) -> list[dict]:
        data = await self._query(_ROUTES_QUERY)
        routes = data.get("data", {}).get("routes", []) or []
        result = []
        for r in routes:
            result.append(
                {
                    "id": r["gtfsId"],
                    "short_name": r.get("shortName"),
                    "long_name": r.get("longName"),
                    "mode": r.get("mode"),
                    "color": r.get("color"),
                    "agency_name": (r.get("agency") or {}).get("name"),
                }
            )
        logger.info("Fetched %d routes from Digitransit", len(result))
        return result
