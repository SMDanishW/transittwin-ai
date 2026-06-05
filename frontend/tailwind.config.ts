import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        bus: "#2563eb",
        tram: "#16a34a",
        metro: "#f97316",
        rail: "#8b5cf6",
        ferry: "#0ea5e9",
      },
    },
  },
  plugins: [],
};

export default config;
