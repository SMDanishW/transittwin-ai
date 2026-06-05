from pydantic import BaseModel, Field


class SimulationRequest(BaseModel):
    simulation_type: str = Field("route_delay", description="route_delay | stop_closure | route_diversion")
    route_id: str = Field(..., description="HSL route ID e.g. HSL:1007")
    stop_id: str = Field(..., description="HSL stop ID e.g. HSL:1173432")
    delay_minutes: int = Field(20, ge=5, le=120)
    duration_minutes: int = Field(60, ge=10, le=480)
    time_period: str = Field("morning_peak", description="morning_peak | evening_peak | off_peak | night")


class AffectedStop(BaseModel):
    id: str
    name: str
    lat: float
    lon: float
    distance_m: int


class SimulationResult(BaseModel):
    simulation_id: str
    route_id: str
    stop_id: str
    stop_name: str | None
    route_name: str | None
    simulation_type: str
    delay_minutes: int
    duration_minutes: int
    time_period: str
    impact_level: str           # low | medium | high | critical
    impact_score: int           # 0-100
    affected_routes: list[str]
    affected_stops: list[AffectedStop]
    estimated_affected_passengers: int
    average_extra_wait_minutes: float
    missed_transfer_risk: str   # low | medium | high
    alternative_routes: list[str]
    confidence: str             # low | medium | high
    computed_at: str
