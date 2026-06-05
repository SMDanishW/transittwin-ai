from pydantic import BaseModel


class AlertEntity(BaseModel):
    route_id: str | None
    stop_id: str | None
    trip_id: str | None


class AlertSchema(BaseModel):
    id: str
    header: str | None
    description: str | None
    effect: str | None
    severity: str | None
    active_start: int | None   # unix epoch
    active_end: int | None
    informed_entities: list[AlertEntity]


class AlertListResponse(BaseModel):
    count: int
    alerts: list[AlertSchema]
