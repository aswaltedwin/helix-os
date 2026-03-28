"use client";

import React from "react";
import Link from "next/link";

export default function Home() {
  const [mounted, setMounted] = React.useState(false);

  React.useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <div className="min-h-screen bg-blue-900 flex items-center justify-center" suppressHydrationWarning>
        <div className="text-white text-4xl font-black">HelixOS</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 to-blue-700 flex items-center justify-center" suppressHydrationWarning>
      <div className="text-center text-white max-w-2xl mx-auto px-6">
        <h1 className="text-5xl font-bold mb-4">HelixOS</h1>
        <p className="text-2xl mb-8 opacity-90">
          Enterprise OS for Autonomous AI Workforces
        </p>

        <p className="text-lg mb-12 opacity-75">
          Auto-discover. Auto-deploy. Auto-improve. Governed. Compliant. Auditable.
        </p>

        <div className="space-y-4">
          <Link
            href="/dashboard"
            className="inline-block bg-white text-blue-900 px-8 py-3 rounded-lg font-semibold hover:bg-blue-50 transition"
          >
            Launch Dashboard
          </Link>

          <p className="text-sm opacity-75">v0.1.0 | Open Source | MIT License</p>
        </div>
      </div>
    </div>
  );
}