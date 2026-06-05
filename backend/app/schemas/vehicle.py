from pydantic import BaseModel


class VehicleSchema(BaseModel):
    id: str
    trip_id: str | None
    route_id: str | None
    lat: float
    lon: float
    bearing: float | None
    speed: float | None
    delay: int | None          # seconds; positive = late
    timestamp: int | None      # unix epoch
    mode: str | None           # BUS TRAM RAIL METRO FERRY
    current_status: str | None # IN_TRANSIT_TO STOPPED_AT INCOMING_AT


class VehicleListResponse(BaseModel):
    count: int
    vehicles: list[VehicleSchema]
