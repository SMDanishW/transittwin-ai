export interface Vehicle {
  id: string;
  trip_id: string | null;
  route_id: string | null;
  lat: number;
  lon: number;
  bearing: number | null;
  speed: number | null;
  delay: number | null;       // seconds; positive = late
  timestamp: number | null;   // unix epoch
  mode: string | null;        // BUS TRAM RAIL METRO FERRY
  current_status: string | null;
}

export interface AlertEntity {
  route_id: string | null;
  stop_id: string | null;
  trip_id: string | null;
}

export interface Alert {
  id: string;
  header: string | null;
  description: string | null;
  effect: string | null;
  severity: string | null;
  active_start: number | null;
  active_end: number | null;
  informed_entities: AlertEntity[];
}

export interface Stop {
  id: string;
  name: string;
  code: string | null;
  vehicle_type: number | null;
  lat: number;
  lon: number;
  zone_id: string | null;
}

export interface Route {
  id: string;
  short_name: string | null;
  long_name: string | null;
  mode: string | null;
  color: string | null;
  agency_name: string | null;
}

export interface AffectedStop {
  id: string;
  name: string;
  lat: number;
  lon: number;
  distance_m: number;
}

export interface SimulationResult {
  simulation_id: string;
  route_id: string;
  stop_id: string;
  stop_name: string | null;
  route_name: string | null;
  simulation_type: string;
  delay_minutes: number;
  duration_minutes: number;
  time_period: string;
  impact_level: "low" | "medium" | "high" | "critical";
  impact_score: number;
  affected_routes: string[];
  affected_stops: AffectedStop[];
  estimated_affected_passengers: number;
  average_extra_wait_minutes: number;
  missed_transfer_risk: "low" | "medium" | "high";
  alternative_routes: string[];
  confidence: "low" | "medium" | "high";
  computed_at: string;
}
