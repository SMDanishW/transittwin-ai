"use client";
import { create } from "zustand";
import type { Vehicle, Alert, SimulationResult } from "@/types";

interface DashboardState {
  vehicles: Vehicle[];
  alerts: Alert[];
  selectedMode: string | null;
  sseConnected: boolean;
  simulationResult: SimulationResult | null;

  setVehicles: (v: Vehicle[]) => void;
  setAlerts: (a: Alert[]) => void;
  setSelectedMode: (mode: string | null) => void;
  setSseConnected: (v: boolean) => void;
  setSimulationResult: (r: SimulationResult | null) => void;
}

export const useDashboardStore = create<DashboardState>((set) => ({
  vehicles: [],
  alerts: [],
  selectedMode: null,
  sseConnected: false,
  simulationResult: null,

  setVehicles: (vehicles) => set({ vehicles }),
  setAlerts: (alerts) => set({ alerts }),
  setSelectedMode: (selectedMode) => set({ selectedMode }),
  setSseConnected: (sseConnected) => set({ sseConnected }),
  setSimulationResult: (simulationResult) => set({ simulationResult }),
}));

// Derived selectors (stable references — call inside components)
export const selectFilteredVehicles = (state: DashboardState) =>
  state.selectedMode
    ? state.vehicles.filter((v) => v.mode === state.selectedMode)
    : state.vehicles;

export const selectVehicleCountByMode = (state: DashboardState) => {
  const counts: Record<string, number> = {};
  for (const v of state.vehicles) {
    const m = v.mode ?? "UNKNOWN";
    counts[m] = (counts[m] ?? 0) + 1;
  }
  return counts;
};
