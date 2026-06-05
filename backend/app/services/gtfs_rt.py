import logging

import httpx
from google.transit import gtfs_realtime_pb2

from app.config import settings

logger = logging.getLogger(__name__)

_STATUS_MAP = {
    0: "INCOMING_AT",
    1: "STOPPED_AT",
    2: "IN_TRANSIT_TO",
}

_EFFECT_MAP = {
    1: "NO_SERVICE",
    2: "REDUCED_SERVICE",
    3: "SIGNIFICANT_DELAYS",
    4: "DETOUR",
    5: "ADDITIONAL_SERVICE",
    6: "MODIFIED_SERVICE",
    7: "OTHER_EFFECT",
    8: "UNKNOWN_EFFECT",
    9: "STOP_MOVED",
}


class GtfsRtService:
    def __init__(self) -> None:
        self._base = settings.GTFS_RT_BASE_URL

    async def _fetch_feed(self, path: str) -> gtfs_realtime_pb2.FeedMessage:
        url = f"{self._base}/{path}"
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(url)
            response.raise_for_status()
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.content)
        return feed

    async def fetch_vehicle_positions(self) -> list[dict]:
        feed = await self._fetch_feed("vehicle-positions/v2/hsl")
        vehicles = []
        for entity in feed.entity:
            if not entity.HasField("vehicle"):
                continue
            vp = entity.vehicle
            pos = vp.position
            trip = vp.trip if vp.HasField("trip") else None
            vehicles.append(
                {
                    "id": entity.id,
                    "trip_id": trip.trip_id if trip else None,
                    "route_id": (trip.route_id or None) if trip else None,
                    "lat": pos.latitude,
                    "lon": pos.longitude,
                    "bearing": pos.bearing if pos.bearing else None,
                    "speed": pos.speed if pos.speed else None,
                    "delay": vp.trip.schedule_relationship if trip else None,
                    "timestamp": vp.timestamp if vp.timestamp else None,
                    "mode": None,
                    "current_status": _STATUS_MAP.get(vp.current_status, None),
                }
            )
        logger.debug("Parsed %d vehicle positions", len(vehicles))
        return vehicles

    async def fetch_service_alerts(self) -> list[dict]:
        feed = await self._fetch_feed("service-alerts/v2/hsl")
        alerts = []
        for entity in feed.entity:
            if not entity.HasField("alert"):
                continue
            alert = entity.alert

            header = None
            if alert.header_text.translation:
                for t in alert.header_text.translation:
                    if t.language in ("en", ""):
                        header = t.text
                        break
                if header is None:
                    header = alert.header_text.translation[0].text

            description = None
            if alert.description_text.translation:
                for t in alert.description_text.translation:
                    if t.language in ("en", ""):
                        description = t.text
                        break
                if description is None:
                    description = alert.description_text.translation[0].text

            active_start = None
            active_end = None
            if alert.active_period:
                active_start = alert.active_period[0].start or None
                active_end = alert.active_period[0].end or None

            informed = []
            for ie in alert.informed_entity:
                informed.append(
                    {
                        "route_id": ie.route_id or None,
                        "stop_id": ie.stop_id or None,
                        "trip_id": ie.trip.trip_id if ie.HasField("trip") else None,
                    }
                )

            alerts.append(
                {
                    "id": entity.id,
                    "header": header,
                    "description": description,
                    "effect": _EFFECT_MAP.get(alert.effect, "UNKNOWN_EFFECT"),
                    "severity": None,
                    "active_start": active_start,
                    "active_end": active_end,
                    "informed_entities": informed,
                }
            )
        logger.debug("Parsed %d service alerts", len(alerts))
        return alerts

    async def fetch_trip_updates(self) -> list[dict]:
        feed = await self._fetch_feed("trip-updates/v2/hsl")
        updates = []
        for entity in feed.entity:
            if not entity.HasField("trip_update"):
                continue
            tu = entity.trip_update
            trip = tu.trip
            stop_updates = []
            for stu in tu.stop_time_update:
                stop_updates.append(
                    {
                        "stop_id": stu.stop_id or None,
                        "stop_sequence": stu.stop_sequence or None,
                        "arrival_delay": stu.arrival.delay if stu.HasField("arrival") else None,
                        "departure_delay": stu.departure.delay if stu.HasField("departure") else None,
                    }
                )
            updates.append(
                {
                    "id": entity.id,
                    "trip_id": trip.trip_id,
                    "route_id": trip.route_id,
                    "stop_time_updates": stop_updates,
                }
            )
        logger.debug("Parsed %d trip updates", len(updates))
        return updates
