"use client";
import dynamic from "next/dynamic";
import RightPanel from "@/components/panels/RightPanel";

// MapLibre uses browser WebGL — must be loaded client-side only
const DigitalTwinMap = dynamic(
  () => import("@/components/map/DigitalTwinMap"),
  { ssr: false, loading: () => <div className="flex-1 bg-gray-950 animate-pulse" /> }
);

export default function LivePage() {
  return (
    <>
      {/* Map fills all remaining space */}
      <div className="flex-1 relative">
        <DigitalTwinMap />
      </div>

      {/* Right panel — vehicle stats + disruption list */}
      <RightPanel />
    </>
  );
}
