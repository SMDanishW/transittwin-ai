import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Providers from "./providers";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "TransitTwin AI",
  description: "Live digital twin for HSL public transport — Helsinki, Espoo, Vantaa",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full">
      <body className={`${inter.className} h-full bg-gray-950 text-gray-100`}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
