"use client";
import { useDashboardStore } from "@/store/dashboardStore";

const EFFECT_STYLES: Record<string, string> = {
  NO_SERVICE: "bg-red-900 text-red-300",
  SIGNIFICANT_DELAYS: "bg-orange-900 text-orange-300",
  REDUCED_SERVICE: "bg-yellow-900 text-yellow-300",
  DETOUR: "bg-blue-900 text-blue-300",
};

const EFFECT_LABEL: Record<string, string> = {
  NO_SERVICE: "No service",
  SIGNIFICANT_DELAYS: "Major delays",
  REDUCED_SERVICE: "Reduced",
  DETOUR: "Detour",
  MODIFIED_SERVICE: "Modified",
  ADDITIONAL_SERVICE: "Extra service",
  OTHER_EFFECT: "Other",
  UNKNOWN_EFFECT: "Unknown",
};

export default function DisruptionList() {
  const alerts = useDashboardStore((s) => s.alerts);

  if (alerts.length === 0) {
    return (
      <p className="text-xs text-gray-500 py-3 text-center">
        No active disruptions
      </p>
    );
  }

  return (
    <ul className="space-y-2">
      {alerts.slice(0, 10).map((a) => {
        const badgeClass =
          EFFECT_STYLES[a.effect ?? ""] ?? "bg-gray-800 text-gray-400";
        const routes = [
          ...new Set(a.informed_entities.map((e) => e.route_id).filter(Boolean)),
        ].slice(0, 4);

        return (
          <li
            key={a.id}
            className="bg-gray-800 rounded-lg p-3 space-y-1"
          >
            <div className="flex items-start justify-between gap-2">
              <p className="text-sm text-gray-100 leading-snug line-clamp-2">
                {a.header ?? "Service disruption"}
              </p>
              <span
                className={`shrink-0 text-[10px] font-semibold px-1.5 py-0.5 rounded ${badgeClass}`}
              >
                {EFFECT_LABEL[a.effect ?? ""] ?? a.effect}
              </span>
            </div>
            {routes.length > 0 && (
              <div className="flex flex-wrap gap-1 mt-1">
                {routes.map((r) => (
                  <span
                    key={r}
                    className="text-[10px] bg-gray-700 text-gray-300 px-1.5 py-0.5 rounded"
                  >
                    {r}
                  </span>
                ))}
              </div>
            )}
          </li>
        );
      })}
    </ul>
  );
}
