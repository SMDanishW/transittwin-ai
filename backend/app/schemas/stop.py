from pydantic import BaseModel


class StopSchema(BaseModel):
    id: str
    name: str
    code: str | None
    vehicle_type: int | None
    platform_code: str | None
    zone_id: str | None
    lat: float
    lon: float

    model_config = {"from_attributes": True}


class StopListResponse(BaseModel):
    total: int
    stops: list[StopSchema]
