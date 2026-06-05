"use client";
import { useEffect, useRef } from "react";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { useShallow } from "zustand/react/shallow";
import {
  useDashboardStore,
  selectFilteredVehicles,
} from "@/store/dashboardStore";
import { useVehicleSSE } from "@/hooks/useVehicleSSE";
import { useAlertSSE } from "@/hooks/useAlertSSE";

// Helsinki city centre
const INITIAL_CENTER: [number, number] = [24.9384, 60.1699];
const INITIAL_ZOOM = 11;

// Free vector tile style — swap for a paid style in production
const MAP_STYLE = "https://tiles.openfreemap.org/styles/liberty";

const MODE_COLORS: Record<string, string> = {
  BUS: "#2563eb",
  TRAM: "#16a34a",
  METRO: "#f97316",
  RAIL: "#8b5cf6",
  FERRY: "#0ea5e9",
};

export default function DigitalTwinMap() {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const mapReadyRef = useRef(false);

  const vehicles         = useDashboardStore(useShallow(selectFilteredVehicles));
  const simulationResult = useDashboardStore((s) => s.simulationResult);

  // Start SSE streams — only once, mounted at top of tree
  useVehicleSSE();
  useAlertSSE();

  // ── Initialise map (runs once) ────────────────────────────────────────────
  useEffect(() => {
    if (mapRef.current || !containerRef.current) return;

    const map = new maplibregl.Map({
      container: containerRef.current,
      style: MAP_STYLE,
      center: INITIAL_CENTER,
      zoom: INITIAL_ZOOM,
      pitch: 45,
      bearing: -17.6,
      attributionControl: true,
    });

    map.addControl(new maplibregl.NavigationControl(), "top-left");
    map.addControl(
      new maplibregl.ScaleControl({ maxWidth: 100, unit: "metric" }),
      "bottom-left"
    );

    map.on("load", () => {
      // ── 3D building extrusions (digital-twin depth) ─────────────────────
      // OpenFreeMap liberty is OpenMapTiles-based; source = "openmaptiles",
      // source-layer = "building" with render_height / render_min_height fields.
      if (map.getSource("openmaptiles")) {
        map.addLayer({
          id: "3d-buildings",
          source: "openmaptiles",
          "source-layer": "building",
          type: "fill-extrusion",
          minzoom: 14,
          paint: {
            "fill-extrusion-color": [
              "interpolate", ["linear"],
              ["coalesce", ["get", "render_height"], 5],
              0,   "#0f172a",
              20,  "#1e293b",
              80,  "#1e3a5f",
              200, "#1d4ed8",
            ],
            "fill-extrusion-height": ["coalesce", ["get", "render_height"], 5],
            "fill-extrusion-base":   ["coalesce", ["get", "render_min_height"], 0],
            "fill-extrusion-opacity": 0.85,
          },
        });
      }

      // ── Vehicle source (GeoJSON with clustering) ────────────────────────
      map.addSource("vehicles", {
        type: "geojson",
        data: { type: "FeatureCollection", features: [] },
        cluster: true,
        clusterMaxZoom: 11,
        clusterRadius: 40,
      });

      // Cluster bubble
      map.addLayer({
        id: "vehicle-clusters",
        type: "circle",
        source: "vehicles",
        filter: ["has", "point_count"],
        paint: {
          "circle-color": "#2563eb",
          "circle-radius": [
            "step",
            ["get", "point_count"],
            14,
            20,
            18,
            100,
            24,
          ],
          "circle-opacity": 0.85,
          "circle-stroke-width": 2,
          "circle-stroke-color": "#1e3a8a",
        },
      });

      // Cluster count label
      map.addLayer({
        id: "vehicle-cluster-count",
        type: "symbol",
        source: "vehicles",
        filter: ["has", "point_count"],
        layout: {
          "text-field": "{point_count_abbreviated}",
          "text-font": ["Open Sans Bold", "Arial Unicode MS Bold"],
          "text-size": 12,
        },
        paint: { "text-color": "#ffffff" },
      });

      // Individual vehicle dot (shown when zoom >= 12 after clustering breaks)
      map.addLayer({
        id: "vehicle-points",
        type: "circle",
        source: "vehicles",
        filter: ["!", ["has", "point_count"]],
        paint: {
          "circle-color": [
            "match",
            ["get", "mode"],
            "TRAM", MODE_COLORS.TRAM,
            "METRO", MODE_COLORS.METRO,
            "RAIL", MODE_COLORS.RAIL,
            "FERRY", MODE_COLORS.FERRY,
            MODE_COLORS.BUS, // default
          ],
          "circle-radius": 6,
          "circle-stroke-width": 1.5,
          "circle-stroke-color": "#ffffff",
          "circle-opacity": 0.9,
        },
      });

      // Click on a single vehicle → popup
      map.on("click", "vehicle-points", (e) => {
        const props = e.features?.[0]?.properties;
        if (!props) return;
        const delay = props.delay != null
          ? `${props.delay > 0 ? "+" : ""}${Math.round(props.delay / 60)} min`
          : "—";
        new maplibregl.Popup({ closeButton: false, offset: 12 })
          .setLngLat(e.lngLat)
          .setHTML(
            `<div class="text-xs leading-5">
              <strong>${props.mode ?? "Vehicle"}</strong> · ${props.route_id ?? "—"}<br/>
              Delay: <span style="color:${props.delay > 60 ? "#ef4444" : "#22c55e"}">${delay}</span><br/>
              Status: ${props.current_status ?? "—"}
            </div>`
          )
          .addTo(map);
      });

      map.on("mouseenter", "vehicle-points", () => {
        map.getCanvas().style.cursor = "pointer";
      });
      map.on("mouseleave", "vehicle-points", () => {
        map.getCanvas().style.cursor = "";
      });

      // ── Affected-stops source (simulation overlay) ─────────────────────
      map.addSource("affected-stops", {
        type: "geojson",
        data: { type: "FeatureCollection", features: [] },
      });

      // Outer halo (pulsing effect via opacity — CSS animation not available
      // in WebGL so we use a larger semi-transparent circle)
      map.addLayer({
        id: "affected-stops-halo",
        type: "circle",
        source: "affected-stops",
        paint: {
          "circle-color": "#ef4444",
          "circle-radius": 18,
          "circle-opacity": 0.25,
          "circle-stroke-width": 0,
        },
      });

      // Inner dot
      map.addLayer({
        id: "affected-stops-dot",
        type: "circle",
        source: "affected-stops",
        paint: {
          "circle-color": "#ef4444",
          "circle-radius": 8,
          "circle-opacity": 0.9,
          "circle-stroke-width": 2,
          "circle-stroke-color": "#ffffff",
        },
      });

      // Stop name label
      map.addLayer({
        id: "affected-stops-label",
        type: "symbol",
        source: "affected-stops",
        layout: {
          "text-field": ["get", "name"],
          "text-font": ["Open Sans Bold", "Arial Unicode MS Bold"],
          "text-size": 11,
          "text-offset": [0, 1.5],
          "text-anchor": "top",
        },
        paint: {
          "text-color": "#fca5a5",
          "text-halo-color": "#111827",
          "text-halo-width": 1.5,
        },
      });

      mapReadyRef.current = true;
    });

    mapRef.current = map;
    return () => {
      mapReadyRef.current = false;
      map.remove();
      mapRef.current = null;
    };
  }, []);

  // ── Push vehicle data updates into the map source ─────────────────────────
  useEffect(() => {
    if (!mapReadyRef.current || !mapRef.current) return;
    const source = mapRef.current.getSource(
      "vehicles"
    ) as maplibregl.GeoJSONSource | undefined;
    if (!source) return;

    source.setData({
      type: "FeatureCollection",
      features: vehicles.map((v) => ({
        type: "Feature",
        geometry: { type: "Point", coordinates: [v.lon, v.lat] },
        properties: {
          id: v.id,
          route_id: v.route_id,
          mode: v.mode,
          delay: v.delay,
          bearing: v.bearing,
          current_status: v.current_status,
        },
      })),
    });
  }, [vehicles]);

  // ── Push simulation affected-stops into the overlay source ───────────────
  useEffect(() => {
    if (!mapReadyRef.current || !mapRef.current) return;
    const source = mapRef.current.getSource(
      "affected-stops"
    ) as maplibregl.GeoJSONSource | undefined;
    if (!source) return;

    if (!simulationResult) {
      source.setData({ type: "FeatureCollection", features: [] });
      return;
    }

    source.setData({
      type: "FeatureCollection",
      features: simulationResult.affected_stops.map((s) => ({
        type: "Feature",
        geometry: { type: "Point", coordinates: [s.lon, s.lat] },
        properties: { id: s.id, name: s.name, distance_m: s.distance_m },
      })),
    });

    // Fly to the disrupted stop
    const first = simulationResult.affected_stops[0];
    if (first) {
      mapRef.current.flyTo({
        center: [first.lon, first.lat],
        zoom: 13,
        speed: 1.2,
      });
    }
  }, [simulationResult]);

  return <div ref={containerRef} className="w-full h-full" />;
}
