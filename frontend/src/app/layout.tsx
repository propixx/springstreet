import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Market Insights Dashboard",
  description: "A student-built dashboard for OHLC data, portfolio analytics, and basic risk-return metrics."
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
