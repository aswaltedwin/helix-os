"use client";

import React from "react";
const { useEffect, useState } = React;

interface TaskData {
  id: string;
  status: string;
  created_at: string;
  message: string | null;
  cost: number;
}

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
  const [tasks, setTasks] = useState<TaskData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [metricsRes, tasksRes] = await Promise.all([
          fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/agents/metrics`),
          fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/tasks/`)
        ]);
        
        const metricsData = await metricsRes.json();
        const tasksData = await tasksRes.json();
        
        setMetrics(metricsData);
        setTasks(tasksData);
      } catch (error) {
        console.error("Failed to fetch dashboard data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  if (loading)
    return (
      <div className="p-8 text-center text-gray-500">
        Loading HelixOS Dashboard...
      </div>
    );

  return (
    <div className="p-8">
      <h2 className="text-4xl font-bold mb-8">Dashboard Overview</h2>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <Card title="Active Agents" value={metrics?.agents?.length ?? 0} color="blue" />
        <Card title="Success Rate" value={`${metrics?.success_rate?.toFixed(1) ?? 0}%`} color="green" />
        <Card title="Total Cost" value={`$${metrics?.total_cost?.toFixed(2) ?? 0}`} color="purple" />
        <Card title="Recent Tasks" value={tasks.length} color="orange" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Agents Table */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-100 flex justify-between items-center">
            <h3 className="text-lg font-semibold text-gray-800">Operational Agents</h3>
            <span className="text-xs font-medium text-gray-400 uppercase tracking-wider">Live Status</span>
          </div>
          <table className="w-full text-sm">
            <thead className="bg-gray-50/50">
              <tr>
                <th className="text-left px-6 py-3 font-semibold text-gray-600">Name</th>
                <th className="text-left px-6 py-3 font-semibold text-gray-600">Category</th>
                <th className="text-left px-6 py-3 font-semibold text-gray-600">Status</th>
              </tr>
            </thead>
            <tbody>
              {metrics?.agents?.map((agent: any) => (
                <tr key={agent.id} className="border-t border-gray-100 hover:bg-gray-50/50 transition-colors">
                  <td className="px-6 py-4 font-medium text-gray-700">{agent.name}</td>
                  <td className="px-6 py-4 text-gray-500 capitalize">{agent.category}</td>
                  <td className="px-6 py-4">
                    <span className="bg-emerald-50 text-emerald-700 border border-emerald-100 px-2 py-1 rounded-full text-[10px] font-bold uppercase tracking-tight">
                      {agent.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Recent Tasks Section */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-100 flex justify-between items-center bg-gray-50/30">
            <h3 className="text-lg font-semibold text-gray-800">Recent Activity</h3>
            <span className="text-xs font-medium text-blue-500 hover:underline cursor-pointer">View All</span>
          </div>
          <div className="divide-y divide-gray-100 max-h-[400px] overflow-auto">
            {tasks.length > 0 ? (
              tasks.map((task: TaskData) => (
                <div key={task.id} className="p-4 hover:bg-gray-50 transition-colors group">

                  <div className="flex justify-between items-start mb-1">
                    <span className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">
                      Task {task.id.split('-')[1]}
                    </span>
                    <span className="text-[10px] text-gray-400 font-mono">
                      {new Date(task.created_at).toLocaleTimeString()}
                    </span>
                  </div>
                  <p className="text-sm font-medium text-gray-800 line-clamp-2 mb-2">
                    {task.message || "Initializing task execution..."}
                  </p>
                  <div className="flex justify-between items-center text-[10px]">
                    <span className={`px-2 py-0.5 rounded-full font-bold uppercase ${
                      task.status === 'COMPLETED' ? 'bg-blue-50 text-blue-600' : 'bg-amber-50 text-amber-600'
                    }`}>
                      {task.status}
                    </span>
                    <span className="font-semibold text-gray-500">Cost: ${task.cost.toFixed(3)}</span>
                  </div>
                </div>
              ))
            ) : (
              <div className="p-12 text-center">
                <p className="text-sm text-gray-400 italic">No recent task activity recorded.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function Card({ title, value, color }: { title: string; value: string | number; color: string }) {
  const colorClasses = {
    blue: "from-blue-500 to-blue-600 text-white shadow-blue-100",
    green: "from-emerald-500 to-emerald-600 text-white shadow-emerald-100",
    purple: "from-indigo-500 to-indigo-600 text-white shadow-indigo-100",
    orange: "from-orange-500 to-orange-600 text-white shadow-orange-100",
  };

  return (
    <div className={`bg-gradient-to-br ${colorClasses[color as keyof typeof colorClasses]} rounded-2xl p-6 shadow-lg transform transition hover:scale-[1.02]`}>
      <div className="text-xs font-bold uppercase tracking-wider opacity-80">{title}</div>
      <div className="text-3xl font-black mt-2 tracking-tight">{value}</div>
    </div>
  );
}

