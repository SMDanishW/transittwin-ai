"use client";
import dynamic from "next/dynamic";
import { useState } from "react";
import { api } from "@/lib/api";
import { useDashboardStore } from "@/store/dashboardStore";
import type { SimulationResult } from "@/types";

const DigitalTwinMap = dynamic(
  () => import("@/components/map/DigitalTwinMap"),
  { ssr: false, loading: () => <div className="flex-1 bg-gray-950 animate-pulse" /> }
);

const MODES = ["BUS", "TRAM", "RAIL", "METRO", "FERRY"];
const DISRUPTION_TYPES = [
  { value: "route_delay", label: "Route delay" },
  { value: "stop_closure", label: "Stop closure" },
  { value: "route_diversion", label: "Route diversion" },
];
const TIME_PERIODS = [
  { value: "morning_peak", label: "Morning peak (07–09)" },
  { value: "evening_peak", label: "Evening peak (16–18)" },
  { value: "off_peak", label: "Off-peak" },
  { value: "night", label: "Night" },
];

const IMPACT_STYLES: Record<string, string> = {
  low:      "bg-green-900  text-green-300  border-green-700",
  medium:   "bg-yellow-900 text-yellow-300 border-yellow-700",
  high:     "bg-orange-900 text-orange-300 border-orange-700",
  critical: "bg-red-900    text-red-300    border-red-700",
};

const RISK_COLOR: Record<string, string> = {
  low:    "text-green-400",
  medium: "text-yellow-400",
  high:   "text-red-400",
};

function ImpactScoreRing({ score }: { score: number }) {
  const r = 28;
  const circ = 2 * Math.PI * r;
  const fill = circ * (1 - score / 100);
  const color = score >= 75 ? "#ef4444" : score >= 50 ? "#f97316" : score >= 25 ? "#eab308" : "#22c55e";
  return (
    <svg width="72" height="72" className="rotate-[-90deg]">
      <circle cx="36" cy="36" r={r} stroke="#374151" strokeWidth="8" fill="none" />
      <circle
        cx="36" cy="36" r={r}
        stroke={color} strokeWidth="8" fill="none"
        strokeDasharray={circ}
        strokeDashoffset={fill}
        strokeLinecap="round"
        style={{ transition: "stroke-dashoffset 0.6s ease" }}
      />
      <text x="36" y="36" textAnchor="middle" dominantBaseline="central"
        fill="white" fontSize="14" fontWeight="bold"
        style={{ transform: "rotate(90deg)", transformOrigin: "36px 36px" }}>
        {score}
      </text>
    </svg>
  );
}

export default function SimulationPage() {
  const setSimulationResult = useDashboardStore((s) => s.setSimulationResult);
  const result = useDashboardStore((s) => s.simulationResult);

  const [routeId, setRouteId]           = useState("HSL:1007");
  const [stopId, setStopId]             = useState("HSL:1173432");
  const [mode, setMode]                 = useState("TRAM");
  const [disruptionType, setDisruptionType] = useState("route_delay");
  const [delayMinutes, setDelayMinutes] = useState(20);
  const [durationMinutes, setDurationMinutes] = useState(60);
  const [timePeriod, setTimePeriod]     = useState("morning_peak");
  const [loading, setLoading]           = useState(false);
  const [error, setError]               = useState<string | null>(null);

  async function handleRun(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}/api/simulation/run`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            simulation_type: disruptionType,
            route_id: routeId.trim(),
            stop_id: stopId.trim(),
            delay_minutes: delayMinutes,
            duration_minutes: durationMinutes,
            time_period: timePeriod,
          }),
        }
      );
      if (!res.ok) {
        const detail = await res.json().catch(() => ({}));
        throw new Error(detail?.detail ?? `Server error ${res.status}`);
      }
      const data: SimulationResult = await res.json();
      setSimulationResult(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      {/* Map */}
      <div className="flex-1 relative">
        <DigitalTwinMap />
      </div>

      {/* Right panel — controls + results */}
      <aside className="w-96 shrink-0 flex flex-col bg-gray-900 border-l border-gray-800 overflow-y-auto">

        {/* ── Controls ─────────────────────────────────────────── */}
        <div className="p-4 border-b border-gray-800">
          <h2 className="text-sm font-semibold text-white">Disruption Simulation</h2>
          <p className="text-xs text-gray-400 mt-0.5">Configure and run the impact model.</p>
        </div>

        <form onSubmit={handleRun} className="p-4 space-y-3 border-b border-gray-800">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs text-gray-400 mb-1">Mode</label>
              <select value={mode} onChange={(e) => setMode(e.target.value)}
                className="w-full bg-gray-800 border border-gray-700 rounded px-2 py-1.5 text-sm text-gray-200">
                {MODES.map((m) => <option key={m}>{m}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs text-gray-400 mb-1">Disruption type</label>
              <select value={disruptionType} onChange={(e) => setDisruptionType(e.target.value)}
                className="w-full bg-gray-800 border border-gray-700 rounded px-2 py-1.5 text-sm text-gray-200">
                {DISRUPTION_TYPES.map(({ value, label }) => <option key={value} value={value}>{label}</option>)}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-xs text-gray-400 mb-1">Route ID</label>
            <input type="text" value={routeId} onChange={(e) => setRouteId(e.target.value)}
              placeholder="HSL:1007"
              className="w-full bg-gray-800 border border-gray-700 rounded px-2 py-1.5 text-sm text-gray-200 placeholder-gray-600" />
          </div>

          <div>
            <label className="block text-xs text-gray-400 mb-1">Stop ID</label>
            <input type="text" value={stopId} onChange={(e) => setStopId(e.target.value)}
              placeholder="HSL:1173432"
              className="w-full bg-gray-800 border border-gray-700 rounded px-2 py-1.5 text-sm text-gray-200 placeholder-gray-600" />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs text-gray-400 mb-1">
                Delay: <span className="text-white">{delayMinutes} min</span>
              </label>
              <input type="range" min={5} max={120} step={5} value={delayMinutes}
                onChange={(e) => setDelayMinutes(Number(e.target.value))}
                className="w-full accent-blue-500" />
            </div>
            <div>
              <label className="block text-xs text-gray-400 mb-1">
                Duration: <span className="text-white">{durationMinutes} min</span>
              </label>
              <input type="range" min={10} max={480} step={10} value={durationMinutes}
                onChange={(e) => setDurationMinutes(Number(e.target.value))}
                className="w-full accent-blue-500" />
            </div>
          </div>

          <div>
            <label className="block text-xs text-gray-400 mb-1">Time period</label>
            <select value={timePeriod} onChange={(e) => setTimePeriod(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded px-2 py-1.5 text-sm text-gray-200">
              {TIME_PERIODS.map(({ value, label }) => <option key={value} value={value}>{label}</option>)}
            </select>
          </div>

          {error && <p className="text-xs text-red-400 bg-red-950 rounded px-2 py-1.5">{error}</p>}

          <button type="submit" disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-500 disabled:bg-gray-700 disabled:text-gray-500
                       text-white rounded py-2 text-sm font-semibold transition-colors">
            {loading ? "Running…" : "Run Simulation"}
          </button>
        </form>

        {/* ── Results ──────────────────────────────────────────── */}
        {result && (
          <div className="p-4 space-y-4">
            {/* Header row */}
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-gray-400">Route {result.route_name} · {result.stop_name}</p>
                <p className="text-xs text-gray-500 mt-0.5">{result.time_period.replace("_", " ")} · {result.delay_minutes} min delay</p>
              </div>
              <ImpactScoreRing score={result.impact_score} />
            </div>

            {/* Impact level badge */}
            <div className={`rounded-lg px-3 py-2 border text-center ${IMPACT_STYLES[result.impact_level]}`}>
              <span className="text-sm font-bold uppercase tracking-wider">{result.impact_level} impact</span>
            </div>

            {/* Key metrics */}
            <div className="grid grid-cols-2 gap-2 text-sm">
              {[
                ["Passengers affected", result.estimated_affected_passengers.toLocaleString()],
                ["Extra wait", `~${result.average_extra_wait_minutes} min`],
                ["Transfer risk", result.missed_transfer_risk],
                ["Confidence", result.confidence],
              ].map(([label, value]) => (
                <div key={label} className="bg-gray-800 rounded-lg p-2.5">
                  <p className="text-[10px] text-gray-400 uppercase tracking-wide">{label}</p>
                  <p className={`font-semibold mt-0.5 ${
                    label === "Transfer risk" ? RISK_COLOR[result.missed_transfer_risk] :
                    label === "Confidence"    ? RISK_COLOR[result.confidence] ?? "text-white" :
                    "text-white"
                  }`}>{value}</p>
                </div>
              ))}
            </div>

            {/* Affected stops */}
            <div>
              <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
                Nearby affected stops ({result.affected_stops.length})
              </h3>
              <ul className="space-y-1 max-h-36 overflow-y-auto">
                {result.affected_stops.map((s) => (
                  <li key={s.id} className="flex justify-between text-xs text-gray-300 bg-gray-800 rounded px-2 py-1.5">
                    <span>{s.name}</span>
                    <span className="text-gray-500">{s.distance_m} m</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Alternatives */}
            <div>
              <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
                Alternative routes
              </h3>
              <ul className="space-y-1">
                {result.alternative_routes.map((alt, i) => (
                  <li key={i} className="text-xs text-gray-300 flex gap-2 items-start">
                    <span className="text-green-400 mt-0.5">→</span>
                    <span>{alt}</span>
                  </li>
                ))}
              </ul>
            </div>

            <p className="text-[10px] text-gray-600 text-center">
              Computed {new Date(result.computed_at).toLocaleTimeString()} · Confidence: {result.confidence}
            </p>
          </div>
        )}
      </aside>
    </>
  );
}
