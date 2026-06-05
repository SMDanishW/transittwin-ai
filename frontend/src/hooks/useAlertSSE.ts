"use client";
import { useEffect } from "react";
import { api } from "@/lib/api";
import { useDashboardStore } from "@/store/dashboardStore";
import type { Alert } from "@/types";

export function useAlertSSE() {
  const setAlerts = useDashboardStore((s) => s.setAlerts);

  useEffect(() => {
    const es = new EventSource(api.sseAlertsUrl());

    es.onmessage = (e) => {
      try {
        const alerts: Alert[] = JSON.parse(e.data);
        setAlerts(alerts);
      } catch {
        // malformed frame — skip silently
      }
    };

    return () => es.close();
  }, [setAlerts]);
}
