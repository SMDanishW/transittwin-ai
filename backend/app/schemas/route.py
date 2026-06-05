from pydantic import BaseModel


class RouteSchema(BaseModel):
    id: str
    short_name: str | None
    long_name: str | None
    mode: str | None
    color: str | None
    agency_name: str | None

    model_config = {"from_attributes": True}


class RouteListResponse(BaseModel):
    total: int
    routes: list[RouteSchema]
