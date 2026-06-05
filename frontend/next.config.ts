import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Required for the multi-stage Docker build (copies only the minimal output)
  output: "standalone",
  // MapLibre GL JS must only run in the browser — no special webpack changes
  // needed as long as all map components carry the 'use client' directive.
};

export default nextConfig;
