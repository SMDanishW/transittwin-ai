"""
LangChain StructuredTool wrappers bound to live db / redis sessions.

Each method fetches real data — no fabrication.  The `AgentTools.as_tools()`
method returns a list ready to hand to `llm.bind_tools()` and `ToolNode`.
"""

import json
import logging
from typing import Optional

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.simulation import SimulationRequest
from app.services.simulation import SimulationEngine

logger = logging.getLogger(__name__)


# ── Input schemas ──────────────────────────────────────────────────────────────

class GetActiveDisruptionsInput(BaseModel):
    limit: int = Field(10, ge=1, le=20, description="Max number of alerts to return (1–20)")


class GetVehicleSummaryInput(BaseModel):
    mode: Optional[str] = Field(
        None,
        description=(
            "Filter by transport mode: BUS, TRAM, METRO, RAIL, or FERRY. "
            "Omit to get a summary of all modes."
        ),
    )


class SimulateDisruptionInput(BaseModel):
    route_id: str = Field(..., description="HSL route ID, e.g. HSL:1007 or HSL:3001")
    stop_id: str = Field(..., description="HSL stop ID, e.g. HSL:1173432. Use find_stop to look one up.")
    delay_minutes: int = Field(20, ge=5, le=120, description="Delay in minutes (5–120)")
    duration_minutes: int = Field(60, ge=10, le=480, description="How long the disruption lasts, in minutes")
    time_period: str = Field(
        "morning_peak",
        description="morning_peak | evening_peak | off_peak | night",
    )
    simulation_type: str = Field(
        "route_delay",
        description="route_delay | stop_closure | route_diversion",
    )


class FindStopInput(BaseModel):
    name: str = Field(..., description="Partial or full stop name, e.g. 'Kamppi', 'Pasila', 'Rautatientori'")
    limit: int = Field(5, ge=1, le=20, description="Max results to return")


# ── Tool implementations ───────────────────────────────────────────────────────

class AgentTools:
    """Container for all agent tools.  One instance per request; holds the
    db session and redis connection for that request's lifetime."""

    def __init__(self, db: AsyncSession, redis) -> None:
        self._db = db
        self._redis = redis
        self._sim = SimulationEngine()

    # ── Tool 1: active disruptions ────────────────────────────────────────────

    async def get_active_disruptions(self, limit: int = 10) -> str:
        """Return the current HSL service alerts from the live GTFS-RT feed."""
        try:
            raw = await self._redis.get("hsl:alerts")
            if not raw:
                return "No active disruptions found in the live feed right now."
            alerts: list[dict] = json.loads(raw)[:limit]
            if not alerts:
                return "No active disruptions at this time."
            lines: list[str] = []
            for a in alerts:
                header   = a.get("header") or "Unnamed alert"
                effect   = a.get("effect") or "unknown effect"
                severity = a.get("severity") or "unknown"
                entities = a.get("informed_entities") or []
                routes   = [e["route_id"] for e in entities if e.get("route_id")]
                route_str = ", ".join(routes[:3]) if routes else "—"
                lines.append(
                    f"• [{severity.upper()}] {header} | "
                    f"Effect: {effect} | Routes: {route_str}"
                )
            return "\n".join(lines)
        except Exception as exc:
            logger.error("get_active_disruptions error: %s", exc)
            return f"Error fetching disruptions: {exc}"

    # ── Tool 2: vehicle summary ───────────────────────────────────────────────

    async def get_vehicle_summary(self, mode: Optional[str] = None) -> str:
        """Return real-time fleet counts, delay stats, and on-time performance."""
        try:
            raw = await self._redis.get("hsl:vehicles")
            if not raw:
                return (
                    "No live vehicle data available. "
                    "The GTFS-RT Arq worker may not be running."
                )
            vehicles: list[dict] = json.loads(raw)
            if mode:
                vehicles = [v for v in vehicles if v.get("mode") == mode.upper()]

            if not vehicles:
                return f"No vehicles found{f' for mode {mode.upper()}' if mode else ''}."

            total = len(vehicles)
            late  = sum(1 for v in vehicles if (v.get("delay") or 0) > 60)
            delays = [v["delay"] for v in vehicles if v.get("delay") is not None]
            avg_delay = round(sum(delays) / len(delays) / 60, 1) if delays else 0.0

            by_mode: dict[str, int] = {}
            for v in vehicles:
                m = v.get("mode") or "UNKNOWN"
                by_mode[m] = by_mode.get(m, 0) + 1

            mode_summary = ", ".join(
                f"{m}: {c}" for m, c in sorted(by_mode.items())
            )
            pct_late = round(late / total * 100) if total else 0
            return (
                f"Live fleet: {total} vehicles ({mode_summary})\n"
                f"Running late (>1 min): {late} ({pct_late}%)\n"
                f"Average delay: {avg_delay} min"
            )
        except Exception as exc:
            logger.error("get_vehicle_summary error: %s", exc)
            return f"Error fetching vehicle summary: {exc}"

    # ── Tool 3: disruption simulation ─────────────────────────────────────────

    async def simulate_disruption(
        self,
        route_id: str,
        stop_id: str,
        delay_minutes: int = 20,
        duration_minutes: int = 60,
        time_period: str = "morning_peak",
        simulation_type: str = "route_delay",
    ) -> str:
        """Run the PostGIS-backed impact simulation and return a readable summary."""
        try:
            req = SimulationRequest(
                simulation_type=simulation_type,
                route_id=route_id,
                stop_id=stop_id,
                delay_minutes=delay_minutes,
                duration_minutes=duration_minutes,
                time_period=time_period,
            )
            r = await self._sim.run(req, self._db)

            stops_preview = ", ".join(s.name for s in r.affected_stops[:3])
            if len(r.affected_stops) > 3:
                stops_preview += f" (+{len(r.affected_stops) - 3} more)"

            alts = "; ".join(r.alternative_routes[:2])

            return (
                f"Simulation result — {r.simulation_type} on {r.route_name} at {r.stop_name}\n"
                f"Impact level : {r.impact_level.upper()} (score {r.impact_score}/100)\n"
                f"Passengers affected : ~{r.estimated_affected_passengers:,}\n"
                f"Extra wait : ~{r.average_extra_wait_minutes} min  |  "
                f"Transfer risk: {r.missed_transfer_risk}\n"
                f"Nearby stops affected : {stops_preview or '—'}\n"
                f"Alternatives : {alts}\n"
                f"Confidence : {r.confidence}"
            )
        except Exception as exc:
            logger.error("simulate_disruption error: %s", exc)
            return f"Simulation error: {exc}"

    # ── Tool 4: stop lookup ───────────────────────────────────────────────────

    async def find_stop(self, name: str, limit: int = 5) -> str:
        """Search HSL stops by name; returns IDs needed for simulate_disruption."""
        try:
            rows = (
                await self._db.execute(
                    text(
                        "SELECT id, name, zone_id FROM stops "
                        "WHERE name ILIKE :q ORDER BY name LIMIT :lim"
                    ),
                    {"q": f"%{name}%", "lim": limit},
                )
            ).fetchall()
            if not rows:
                return f"No stops found matching '{name}'."
            lines = [
                f"• {row.id} — {row.name} (zone: {row.zone_id or '?'})"
                for row in rows
            ]
            return "\n".join(lines)
        except Exception as exc:
            logger.error("find_stop error: %s", exc)
            return f"Error searching stops: {exc}"

    # ── Build tool list ───────────────────────────────────────────────────────

    def as_tools(self) -> list:
        """Return LangChain StructuredTool objects bound to this instance."""
        return [
            StructuredTool.from_function(
                coroutine=self.get_active_disruptions,
                name="get_active_disruptions",
                description=(
                    "Fetch the current list of HSL service disruption alerts "
                    "from the live GTFS-RT feed. Call this first for any disruption question."
                ),
                args_schema=GetActiveDisruptionsInput,
            ),
            StructuredTool.from_function(
                coroutine=self.get_vehicle_summary,
                name="get_vehicle_summary",
                description=(
                    "Get real-time HSL fleet statistics: vehicle counts by mode, "
                    "how many are late, and average delay. Optionally filter by mode."
                ),
                args_schema=GetVehicleSummaryInput,
            ),
            StructuredTool.from_function(
                coroutine=self.simulate_disruption,
                name="simulate_disruption",
                description=(
                    "Run a disruption impact simulation on an HSL route. "
                    "Returns impact score, affected passengers, transfer risk, and alternatives. "
                    "Use find_stop first if you only have a stop name."
                ),
                args_schema=SimulateDisruptionInput,
            ),
            StructuredTool.from_function(
                coroutine=self.find_stop,
                name="find_stop",
                description=(
                    "Search HSL stops by partial name (e.g. 'Kamppi', 'Pasila'). "
                    "Returns stop IDs required by simulate_disruption."
                ),
                args_schema=FindStopInput,
            ),
        ]
