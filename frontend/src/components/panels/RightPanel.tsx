"use client";
import { useShallow } from "zustand/react/shallow";
import {
  useDashboardStore,
  selectVehicleCountByMode,
} from "@/store/dashboardStore";
import DisruptionList from "./DisruptionList";

const MODES = [
  { key: "BUS", label: "Bus", color: "bg-blue-600" },
  { key: "TRAM", label: "Tram", color: "bg-green-600" },
  { key: "METRO", label: "Metro", color: "bg-orange-500" },
  { key: "RAIL", label: "Rail", color: "bg-purple-600" },
  { key: "FERRY", label: "Ferry", color: "bg-sky-500" },
];

export default function RightPanel() {
  const counts = useDashboardStore(useShallow(selectVehicleCountByMode));
  const selectedMode = useDashboardStore((s) => s.selectedMode);
  const setSelectedMode = useDashboardStore((s) => s.setSelectedMode);
  const alerts = useDashboardStore((s) => s.alerts);

  return (
    <aside className="w-80 shrink-0 flex flex-col gap-0 bg-gray-900 border-l border-gray-800 overflow-y-auto">
      {/* Vehicle counts */}
      <section className="p-4 border-b border-gray-800">
        <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
          Live Vehicles
        </h2>
        <div className="grid grid-cols-2 gap-2">
          {MODES.map(({ key, label, color }) => (
            <button
              key={key}
              onClick={() =>
                setSelectedMode(selectedMode === key ? null : key)
              }
              className={`flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-all border ${
                selectedMode === key
                  ? "border-white/30 bg-gray-700"
                  : "border-gray-700 hover:border-gray-600 hover:bg-gray-800"
              }`}
            >
              <span className={`w-2.5 h-2.5 rounded-full shrink-0 ${color}`} />
              <span className="text-gray-200">{label}</span>
              <span className="ml-auto text-gray-400 text-xs tabular-nums">
                {counts[key] ?? 0}
              </span>
            </button>
          ))}
        </div>
        {selectedMode && (
          <button
            onClick={() => setSelectedMode(null)}
            className="mt-2 text-xs text-blue-400 hover:text-blue-300 w-full text-center"
          >
            ✕ Clear filter
          </button>
        )}
      </section>

      {/* Active disruptions */}
      <section className="p-4 flex-1">
        <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3 flex items-center justify-between">
          <span>Disruptions</span>
          {alerts.length > 0 && (
            <span className="bg-red-600 text-white text-[10px] px-1.5 py-0.5 rounded-full">
              {alerts.length}
            </span>
          )}
        </h2>
        <DisruptionList />
      </section>
    </aside>
  );
}
