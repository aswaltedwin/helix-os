import React from "react";
import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "HelixOS - Enterprise AI Workforce OS",
  description: "Multi-agent orchestration for autonomous enterprise automation",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="bg-gray-50" suppressHydrationWarning>
        {children}
      </body>
    </html>
  );
}