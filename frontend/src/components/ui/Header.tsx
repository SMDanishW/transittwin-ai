"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useDashboardStore } from "@/store/dashboardStore";

const NAV = [
  { href: "/dashboard/live", label: "Live" },
  { href: "/dashboard/simulation", label: "Simulation" },
  { href: "/dashboard/assistant", label: "AI Assistant" },
  { href: "/dashboard/system", label: "System" },
];

export default function Header() {
  const pathname = usePathname();
  const sseConnected = useDashboardStore((s) => s.sseConnected);
  const vehicleCount = useDashboardStore((s) => s.vehicles.length);

  return (
    <header className="flex items-center justify-between h-14 px-5 bg-gray-900 border-b border-gray-800 shrink-0">
      {/* Brand */}
      <div className="flex items-center gap-3">
        <span className="text-lg font-bold tracking-tight text-white">
          TransitTwin<span className="text-blue-400"> AI</span>
        </span>
        <span className="hidden sm:block text-xs text-gray-400 border border-gray-700 rounded px-2 py-0.5">
          HSL · Helsinki · Espoo · Vantaa
        </span>
      </div>

      {/* Nav */}
      <nav className="flex gap-1">
        {NAV.map(({ href, label }) => (
          <Link
            key={href}
            href={href}
            className={`px-3 py-1.5 rounded text-sm font-medium transition-colors ${
              pathname === href
                ? "bg-blue-600 text-white"
                : "text-gray-400 hover:text-white hover:bg-gray-800"
            }`}
          >
            {label}
          </Link>
        ))}
      </nav>

      {/* Live indicator */}
      <div className="flex items-center gap-2 text-xs text-gray-400">
        <span
          className={`w-2 h-2 rounded-full ${
            sseConnected ? "bg-green-400 animate-pulse" : "bg-red-500"
          }`}
        />
        {sseConnected ? (
          <span className="text-green-400">{vehicleCount} vehicles live</span>
        ) : (
          <span className="text-red-400">Connecting…</span>
        )}
      </div>
    </header>
  );
}
