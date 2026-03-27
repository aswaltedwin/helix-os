"use client";

import React from "react";



interface Agent {

  id: string;
  name: string;
  category: string;
  description: string;
  status: string;
}

export default function AgentsPage() {
  const [agents, setAgents] = React.useState<Agent[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [isModalOpen, setIsModalOpen] = React.useState(false);
  const [editingId, setEditingId] = React.useState<string | null>(null);
  const [newAgent, setNewAgent] = React.useState({
    name: "",
    category: "finance",
    description: "",
    system_prompt: "You are a helpful specialist agent for HelixOS.",
    model: "claude-3-5-sonnet-20241022"
  });

  const getApiUrl = () => process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const fetchAgents = async () => {
    const apiUrl = getApiUrl();
    try {
      const res = await fetch(`${apiUrl}/api/agents/`);
      if (!res.ok) throw new Error(`Fetch failed: ${res.status}`);
      const data = await res.json();
      setAgents(data);
    } catch (err) {
      console.error("Agents Fetch Error:", err);
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    fetchAgents();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const apiUrl = getApiUrl();
    const method = editingId ? "PUT" : "POST";
    const path = editingId ? `/api/agents/${editingId}` : "/api/agents/";
    
    try {
      const res = await fetch(`${apiUrl}${path}`, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newAgent),
      });
      if (res.ok) {
        setIsModalOpen(false);
        setEditingId(null);
        setNewAgent({ name: "", category: "finance", description: "", system_prompt: "You are a helpful specialist agent for HelixOS.", model: "claude-3-5-sonnet-20241022" });
        fetchAgents();
      } else {
        const errorData = await res.json().catch(() => ({ detail: "Unknown error" }));
        console.error("Agent Operation Error:", errorData);
      }
    } catch (err) {
      console.error("Agent Operation Network Error:", err);
    }
  };

  const openEditModal = (agent: any) => {
    setEditingId(agent.id);
    setNewAgent({
      name: agent.name,
      category: agent.category,
      description: agent.description || "",
      system_prompt: agent.system_prompt || "You are a helpful specialist agent for HelixOS.",
      model: agent.model || "claude-3-5-sonnet-20241022"
    });
    setIsModalOpen(true);
  };

  if (loading) return <div className="p-8 text-center animate-pulse text-gray-400">Loading Agents...</div>;

  return (
    <div className="p-8 min-h-full bg-gray-50/50">
      <div className="flex justify-between items-center mb-12">
        <div>
          <h2 className="text-4xl font-black text-gray-900 tracking-tight">Agent Workforce</h2>
          <p className="text-gray-500 mt-2 font-medium">Manage and deploy your autonomous specialist agents.</p>
        </div>
        <button
          onClick={() => {
            setEditingId(null);
            setNewAgent({ name: "", category: "finance", description: "", system_prompt: "You are a helpful specialist agent for HelixOS.", model: "claude-3-5-sonnet-20241022" });
            setIsModalOpen(true);
          }}
          className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-2xl font-bold shadow-lg shadow-indigo-100 transition-all hover:scale-105 active:scale-95 flex items-center gap-2"
        >
          <span className="text-xl">+</span> Build New Agent
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {agents.map((agent: any) => (
          <div
            key={agent.id}
            className="group bg-white rounded-3xl p-6 shadow-sm border border-gray-100 hover:shadow-xl hover:shadow-indigo-50/50 transition-all duration-300 transform hover:-translate-y-1"
          >
            <div className="flex justify-between items-start mb-4">
              <div className={`p-3 rounded-2xl bg-indigo-50 text-indigo-600 group-hover:bg-indigo-600 group-hover:text-white transition-colors`}>
                {agent.category === 'finance' ? '💰' : agent.category === 'hr' ? '👥' : agent.category === 'sales' ? '📈' : '🛠️'}
              </div>
              <span className="bg-emerald-50 text-emerald-600 text-[10px] font-bold px-2 py-1 rounded-full uppercase tracking-widest border border-emerald-100">
                {agent.status}
              </span>
            </div>
            <h3 className="text-xl font-bold text-gray-800 mb-2">{agent.name}</h3>
            <p className="text-sm text-gray-500 line-clamp-2 mb-6 font-medium">
              {agent.description || "No description provided for this specialist."}
            </p>
            <div className="flex justify-between items-center pt-6 border-t border-gray-50">
              <span className="text-xs font-bold text-gray-400 uppercase tracking-tighter">{agent.category} specialist</span>
              <button 
                onClick={() => openEditModal(agent)}
                className="text-indigo-600 text-sm font-bold hover:underline"
              >
                Configure →
              </button>
            </div>
          </div>
        ))}
        {agents.length === 0 && (
           <div className="col-span-full py-20 text-center border-2 border-dashed border-gray-200 rounded-[32px] bg-gray-50/50">
             <div className="text-4xl mb-4 opacity-20">🤖</div>
             <p className="text-gray-400 font-medium">No agents active in the current workforce.</p>
           </div>
        )}
      </div>

      {/* Agent Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-gray-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-in fade-in duration-200">
          <div className="bg-white rounded-[32px] w-full max-w-lg shadow-2xl overflow-hidden animate-in slide-in-from-bottom-8 duration-300 max-h-[90vh] flex flex-col">
            <div className="p-8 border-b border-gray-100 flex justify-between items-center bg-gray-50/50">
              <h3 className="text-2xl font-black text-gray-900">{editingId ? "Configure specialist" : "New Specialist"}</h3>
              <button onClick={() => setIsModalOpen(false)} className="text-gray-400 hover:text-gray-600 text-2xl font-light">×</button>
            </div>
            <form onSubmit={handleSubmit} className="p-8 space-y-6 overflow-y-auto">
              <div>
                <label className="block text-xs font-black text-gray-400 uppercase tracking-widest mb-2">Agent Name</label>
                <input
                  required
                  type="text"
                  placeholder="e.g. Finance Oracle"
                  className="w-full bg-gray-50 border-none rounded-2xl p-4 text-gray-800 focus:ring-2 focus:ring-indigo-500 font-medium"
                  value={newAgent.name}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setNewAgent({ ...newAgent, name: e.target.value })}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-black text-gray-400 uppercase tracking-widest mb-2">Category</label>
                  <select
                    className="w-full bg-gray-50 border-none rounded-2xl p-4 text-gray-800 focus:ring-2 focus:ring-indigo-500 font-medium"
                    value={newAgent.category}
                    onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setNewAgent({ ...newAgent, category: e.target.value })}
                  >
                    <option value="finance">Finance</option>
                    <option value="hr">HR</option>
                    <option value="sales">Sales</option>
                    <option value="ops">Ops</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-black text-gray-400 uppercase tracking-widest mb-2">Primary Model</label>
                  <div className="w-full bg-gray-50 border-none rounded-2xl p-4 text-gray-400 font-medium cursor-not-allowed">Claude 3.5</div>
                </div>
              </div>
              <div>
                <label className="block text-xs font-black text-gray-400 uppercase tracking-widest mb-2">Description</label>
                <textarea
                  rows={2}
                  placeholder="What does this agent do?"
                  className="w-full bg-gray-50 border-none rounded-2xl p-4 text-gray-800 focus:ring-2 focus:ring-indigo-500 font-medium"
                  value={newAgent.description}
                  onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setNewAgent({ ...newAgent, description: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-xs font-black text-gray-400 uppercase tracking-widest mb-2">System Prompt</label>
                <textarea
                  rows={4}
                  placeholder="Detailed instructions for the agent..."
                  className="w-full bg-gray-50 border-none rounded-2xl p-4 text-gray-800 focus:ring-2 focus:ring-indigo-500 font-mono text-xs"
                  value={newAgent.system_prompt}
                  onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setNewAgent({ ...newAgent, system_prompt: e.target.value })}
                />
              </div>
              <button
                type="submit"
                className="w-full bg-indigo-600 hover:bg-indigo-700 text-white py-4 rounded-2xl font-black text-lg shadow-xl shadow-indigo-100 transition-all active:scale-95"
              >
                {editingId ? "Update Agent" : "Assemble Agent"}
              </button>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}
