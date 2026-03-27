"use client";

import React from "react";
const { useEffect, useState } = React;

interface MetricsData {
  agents: Array<{
    id: string;
    name: string;
    category: string;
    status: string;
  }>;
  total_cost: number;
  success_rate: number;
}

export default function DashboardPage() {
  const [metrics, setMetrics] = useState<MetricsData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/api/agents/metrics`
        );
        const data = await response.json();
        setMetrics(data);
      } catch (error) {
        console.error("Failed to fetch metrics:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, 5000);
    return () => clearInterval(interval);
  }, []);

  if (loading)
    return (
      <div className="p-8 text-center">
        <p className="text-gray-600">Loading...</p>
      </div>
    );

  return (
    <div className="p-8">
      <h2 className="text-4xl font-bold mb-8">Dashboard</h2>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <Card title="Active Agents" value={metrics?.agents?.length ?? 0} color="blue" />
        <Card title="Success Rate" value={`${metrics?.success_rate?.toFixed(1) ?? 0}%`} color="green" />
        <Card title="Total Cost" value={`$${metrics?.total_cost?.toFixed(2) ?? 0}`} color="purple" />
        <Card title="Tasks" value="0" color="orange" />
      </div>

      {/* Agents Table */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b">
          <h3 className="text-lg font-semibold">Agents</h3>
        </div>
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="text-left px-6 py-3 font-medium">Name</th>
              <th className="text-left px-6 py-3 font-medium">Category</th>
              <th className="text-left px-6 py-3 font-medium">Status</th>
            </tr>
          </thead>
          <tbody>
            {metrics?.agents?.map((agent: any) => (
              <tr key={agent.id} className="border-b hover:bg-gray-50">
                <td className="px-6 py-3">{agent.name}</td>
                <td className="px-6 py-3">{agent.category}</td>
                <td className="px-6 py-3">
                  <span className="bg-green-100 text-green-800 px-2 py-1 rounded text-xs font-medium">
                    {agent.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function Card({ title, value, color }: { title: string; value: string | number; color: string }) {
  const colorClasses = {
    blue: "from-blue-50 to-blue-100 text-blue-700",
    green: "from-green-50 to-green-100 text-green-700",
    purple: "from-purple-50 to-purple-100 text-purple-700",
    orange: "from-orange-50 to-orange-100 text-orange-700",
  };

  return (
    <div className={`bg-gradient-to-br ${colorClasses[color as keyof typeof colorClasses]} rounded-lg p-6 shadow`}>
      <div className="text-sm font-medium opacity-75">{title}</div>
      <div className="text-4xl font-bold mt-2">{value}</div>
    </div>
  );
}