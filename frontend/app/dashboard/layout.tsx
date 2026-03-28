import React from "react";
import Link from "next/link";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex h-screen">
      {/* Sidebar */}
      <aside className="w-64 bg-gray-900 text-white flex flex-col">
        <div className="p-6 border-b border-gray-700">
          <h1 className="text-2xl font-bold">HelixOS</h1>
          <p className="text-sm text-gray-400 mt-1">v0.1.0</p>
        </div>

        <nav className="flex-1 p-6 space-y-2" suppressHydrationWarning>
          <NavLink href="/dashboard" label="Dashboard" icon="📊" />
          <NavLink href="/dashboard/agents" label="Agents" icon="👥" />
          <NavLink href="/dashboard/workflows" label="Workflows" icon="⚙️" />
          <NavLink href="/dashboard/governance" label="Governance" icon="⚖️" />
        </nav>


        <div className="p-6 border-t border-gray-700 text-sm text-gray-400">
          <p>© 2026 HelixOS</p>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto bg-gray-50" suppressHydrationWarning>
        {children}
      </main>

    </div>
  );
}

function NavLink({ href, label, icon }: { href: string; label: string; icon: string }) {
  return (
    <Link
      href={href}
      className="block px-4 py-2 rounded-lg hover:bg-gray-800 transition"
      suppressHydrationWarning
    >
      {icon} {label}
    </Link>

  );
}
