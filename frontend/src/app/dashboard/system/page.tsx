"use client";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useDashboardStore } from "@/store/dashboardStore";

interface StatusCardProps {
  label: string;
  status: "ok" | "error" | "loading";
  detail?: string;
}

function StatusCard({ label, status, detail }: StatusCardProps) {
  const color =
    status === "ok"
      ? "text-green-400"
      : status === "error"
      ? "text-red-400"
      : "text-yellow-400";
  const dot =
    status === "ok"
      ? "bg-green-400"
      : status === "error"
      ? "bg-red-400"
      : "bg-yellow-400 animate-pulse";

  return (
    <div className="bg-gray-800 rounded-xl p-5 flex items-center gap-4">
      <span className={`w-3 h-3 rounded-full shrink-0 ${dot}`} />
      <div className="flex-1">
        <p className="text-sm font-medium text-white">{label}</p>
        {detail && (
          <p className={`text-xs mt-0.5 ${color}`}>{detail}</p>
        )}
      </div>
      <span className={`text-xs font-semibold ${color}`}>
        {status === "loading" ? "Checking…" : status.toUpperCase()}
      </span>
    </div>
  );
}

export default function SystemPage() {
  const { data, isError, isLoading, dataUpdatedAt } = useQuery({
    queryKey: ["health"],
    queryFn: api.getHealth,
    refetchInterval: 10_000,
  });

  const vehicleCount = useDashboardStore((s) => s.vehicles.length);
  const alertCount = useDashboardStore((s) => s.alerts.length);
  const sseConnected = useDashboardStore((s) => s.sseConnected);

  const lastUpdated = dataUpdatedAt
    ? new Date(dataUpdatedAt).toLocaleTimeString()
    : "—";

  return (
    <div className="flex-1 overflow-y-auto p-6">
      <div className="max-w-2xl mx-auto space-y-6">
        <div>
          <h1 className="text-lg font-semibold text-white">System Health</h1>
          <p className="text-xs text-gray-400 mt-1">
            Auto-refreshes every 10 seconds · Last check: {lastUpdated}
          </p>
        </div>

        <div className="space-y-3">
          <StatusCard
            label="Backend API"
            status={isLoading ? "loading" : isError ? "error" : "ok"}
            detail={isError ? "Cannot reach backend" : data?.status ?? "Healthy"}
          />
          <StatusCard
            label="SSE Stream (GTFS-RT)"
            status={sseConnected ? "ok" : "error"}
            detail={
              sseConnected
                ? `${vehicleCount} vehicles · ${alertCount} alerts`
                : "Stream disconnected"
            }
          />
          <StatusCard
            label="PostgreSQL + PostGIS"
            status={isLoading ? "loading" : isError ? "error" : "ok"}
            detail="Inferred from API health"
          />
          <StatusCard
            label="Redis Cache"
            status={sseConnected ? "ok" : "error"}
            detail="Inferred from SSE data freshness"
          />
          <StatusCard
            label="Digitransit API"
            status={isLoading ? "loading" : isError ? "error" : "ok"}
            detail="Stop/route seeding source"
          />
        </div>

        {/* Data snapshot */}
        <div className="bg-gray-800 rounded-xl p-5 space-y-3">
          <h2 className="text-sm font-semibold text-white">Live Data Snapshot</h2>
          <div className="grid grid-cols-2 gap-3 text-sm">
            {[
              ["Vehicles tracked", vehicleCount],
              ["Active alerts", alertCount],
              ["SSE stream", sseConnected ? "Connected" : "Disconnected"],
              ["Data source", "HSL GTFS-RT"],
              ["Polling (vehicles)", "every 5 s"],
              ["Polling (alerts)", "every 30 s"],
            ].map(([label, value]) => (
              <div key={label} className="flex justify-between">
                <span className="text-gray-400">{label}</span>
                <span className="text-gray-100 font-medium">{value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
