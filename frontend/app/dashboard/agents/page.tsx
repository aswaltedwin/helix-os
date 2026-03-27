"use client";

import React from "react";
const { useEffect, useState } = React;

interface Agent {
  id: string;
  name: string;
  category: string;
  status: string;
  model: string;
}

export default function AgentsPage() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAgents = async () => {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/agents/`);
        const data = await response.json();
        setAgents(data);
      } catch (error) {
        console.error("Failed to fetch agents:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchAgents();
  }, []);

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-8">
        <h2 className="text-3xl font-bold">Agents</h2>
        <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition">
          + New Agent
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {loading ? (
          <p>Loading agents...</p>
        ) : agents.length > 0 ? (
          agents.map((agent: Agent) => (
            <div key={agent.id} className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">

              <div className="flex justify-between items-start mb-4">
                <div className="bg-blue-100 text-blue-700 p-3 rounded-lg text-2xl">
                  🤖
                </div>
                <span className="bg-green-100 text-green-800 px-2 py-1 rounded text-xs font-medium uppercase">
                  {agent.status}
                </span>
              </div>
              <h3 className="text-xl font-bold mb-1">{agent.name}</h3>
              <p className="text-sm text-gray-500 mb-4">{agent.category.toUpperCase()} Agent</p>
              <div className="text-xs text-gray-400 font-mono bg-gray-50 p-2 rounded">
                Model: {agent.model}
              </div>
            </div>
          ))
        ) : (
          <div className="col-span-full py-12 text-center bg-gray-50 rounded-xl border-2 border-dashed border-gray-200">
            <p className="text-gray-400">No agents found. Create your first autonomous agent!</p>
          </div>
        )}
      </div>
    </div>
  );
}
