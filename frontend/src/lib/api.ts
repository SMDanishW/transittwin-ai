const API_BASE =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export const api = {
  async getStops(vehicleType?: number) {
    const qs = vehicleType !== undefined
      ? `?mode=${vehicleType}&limit=2000`
      : "?limit=2000";
    const res = await fetch(`${API_BASE}/api/stops${qs}`);
    if (!res.ok) throw new Error("Failed to fetch stops");
    return res.json();
  },

  async getRoutes(mode?: string) {
    const qs = mode ? `?mode=${mode}&limit=500` : "?limit=500";
    const res = await fetch(`${API_BASE}/api/routes${qs}`);
    if (!res.ok) throw new Error("Failed to fetch routes");
    return res.json();
  },

  async getVehicles() {
    const res = await fetch(`${API_BASE}/api/vehicles`);
    if (!res.ok) throw new Error("Failed to fetch vehicles");
    return res.json();
  },

  async getAlerts() {
    const res = await fetch(`${API_BASE}/api/alerts`);
    if (!res.ok) throw new Error("Failed to fetch alerts");
    return res.json();
  },

  async getHealth() {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error("API unhealthy");
    return res.json();
  },

  sseVehiclesUrl: () => `${API_BASE}/api/sse/vehicles`,
  sseAlertsUrl: () => `${API_BASE}/api/sse/alerts`,
};
