"use client";
import { useEffect } from "react";
import { api } from "@/lib/api";
import {
  useDashboardStore,
} from "@/store/dashboardStore";
import type { Vehicle } from "@/types";

export function useVehicleSSE() {
  const setVehicles = useDashboardStore((s) => s.setVehicles);
  const setSseConnected = useDashboardStore((s) => s.setSseConnected);

  useEffect(() => {
    const es = new EventSource(api.sseVehiclesUrl());

    es.onopen = () => setSseConnected(true);

    es.onmessage = (e) => {
      try {
        const vehicles: Vehicle[] = JSON.parse(e.data);
        setVehicles(vehicles);
      } catch {
        // malformed frame — skip silently
      }
    };

    es.onerror = () => setSseConnected(false);

    return () => {
      es.close();
      setSseConnected(false);
    };
  }, [setVehicles, setSseConnected]);
}
