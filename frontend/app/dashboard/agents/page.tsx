"use client";

import React from "react";
import { Users, Activity, FileText } from 'lucide-react';

interface Agent {
  id: string;
  name: string;
  category: string;
  description: string;
  system_prompt: string;
  status: string;
  capabilities: string[];
}

export default function AgentsManagementPage() {
  const [agents, setAgents] = React.useState<Agent[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [isModalOpen, setIsModalOpen] = React.useState(false);
  const [newAgent, setNewAgent] = React.useState({
    name: "",
    category: "finance",
    description: "",
    system_prompt: "",
    model: "claude-3-5-sonnet-20241022"
  });
  const [error, setError] = React.useState<string | null>(null);

  const fetchAgents = async () => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    try {
      const res = await fetch(`${apiUrl}/api/agents`);
      if (res.ok) {
        const data = await res.json();
        setAgents(data);
      }
    } catch (err) {
      console.error("Failed to fetch agents:", err);
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    fetchAgents();
  }, []);

  const handleCreateAgent = async (e: React.FormEvent) => {
    e.preventDefault();
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    try {
      const res = await fetch(`${apiUrl}/api/agents/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newAgent)
      });
      if (res.ok) {
        setIsModalOpen(false);
        setNewAgent({ name: "", category: "finance", description: "", system_prompt: "", model: "claude-3-5-sonnet-20241022" });
        fetchAgents();
      } else {
        setError("Failed to create agent. Verify network connectivity.");
      }
    } catch (err) {
      setError("Network error. Is the backend online?");
    }
  };

  const handleDeleteAgent = async (id: string) => {
    if (!confirm("Are you sure you want to decommission this specialist?")) return;
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    try {
      const res = await fetch(`${apiUrl}/api/agents/${id}`, { method: "DELETE" });
      if (res.ok) {
        fetchAgents();
      }
    } catch (err) {
      console.error("Delete failed:", err);
    }
  };

  if (loading) return <div className="p-12 text-center text-gray-400 animate-pulse font-black uppercase tracking-[0.3em]">Synchronizing Workforce...</div>;

  return (
    <div className="p-12 max-w-7xl mx-auto min-h-screen bg-slate-50/20">
      <div className="flex flex-col md:flex-row justify-between items-end mb-12 gap-6">
        <div>
          <span className="text-[10px] font-black text-indigo-500 uppercase tracking-[0.3em] mb-2 block">Specialist Management</span>
          <h2 className="text-4xl font-black text-slate-900 tracking-tight flex items-center gap-3">
            Autonomous Workforce
          </h2>
        </div>
        <button 
          onClick={() => setIsModalOpen(true)}
          className="bg-indigo-600 hover:bg-indigo-700 text-white px-8 py-4 rounded-[24px] font-black transition-all active:scale-95 flex items-center gap-2 shadow-xl shadow-indigo-100 uppercase tracking-widest text-[11px]"
        >
          <Activity size={16} strokeWidth={3} /> Authorize New Specialist
        </button>
      </div>

      <div className="grid grid-cols-1 gap-6">
        {agents.map((agent: Agent) => (
          <div key={agent.id} className="group bg-white rounded-[32px] border border-slate-100 p-8 shadow-sm hover:shadow-xl transition-all flex flex-col md:flex-row items-start md:items-center justify-between gap-8 relative overflow-hidden">
            <div className={`absolute left-0 top-0 bottom-0 w-2 bg-${agent.category === 'finance' ? 'emerald' : agent.category === 'hr' ? 'blue' : 'purple'}-500/20`} />
            
            <div className="flex items-center gap-6 relative z-10">
              <div className={`p-5 rounded-3xl bg-slate-50 text-slate-400 group-hover:bg-indigo-50 group-hover:text-indigo-600 transition-all`}>
                {agent.category === 'finance' ? <Activity size={28} /> : <Users size={28} />}
              </div>
              <div>
                <div className="flex items-center gap-3 mb-1">
                   <h3 className="text-xl font-black text-slate-900 uppercase tracking-tight">{agent.name}</h3>
                   <span className="text-[10px] font-black bg-slate-50 text-slate-400 px-2 py-1 rounded uppercase tracking-widest border border-slate-100">{agent.category}</span>
                </div>
                <p className="text-sm text-slate-500 font-medium max-w-md">{agent.description || "No description provided for this specialist."}</p>
              </div>
            </div>

            <div className="flex items-center gap-12 relative z-10 w-full md:w-auto justify-between md:justify-end border-t md:border-t-0 border-slate-50 pt-6 md:pt-0">
               <div className="flex gap-2">
                 {agent.capabilities?.map((cap: string) => (
                   <span key={cap} className="text-[9px] font-black text-indigo-400 border border-indigo-50 px-2 py-1 rounded-lg uppercase tracking-widest">{cap}</span>
                 ))}
               </div>
               
               <div className="flex items-center gap-3">
                 <button className="p-3 text-slate-300 hover:text-indigo-600 hover:bg-indigo-50 rounded-2xl transition-all">
                    <Activity size={18} />
                 </button>
                 <button 
                   onClick={() => handleDeleteAgent(agent.id)}
                   className="p-3 text-slate-300 hover:text-red-600 hover:bg-red-50 rounded-2xl transition-all"
                 >
                    <Activity size={18} />
                 </button>
               </div>
            </div>
          </div>
        ))}
      </div>

      {/* Create Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-md z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-[48px] shadow-2xl w-full max-w-2xl overflow-hidden animate-in zoom-in-95 duration-200">
            <div className="p-10 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
              <div>
                 <span className="text-[10px] font-black text-indigo-500 uppercase tracking-[0.3em] mb-2 block">Personnel Authorization</span>
                 <h2 className="text-3xl font-black text-slate-900 uppercase tracking-tight">New Specialist</h2>
              </div>
              <button 
                onClick={() => setIsModalOpen(false)}
                className="text-slate-400 hover:text-slate-900 transition-colors p-4 bg-white rounded-full shadow-sm hover:shadow-md"
              >✕</button>
            </div>
            
            <form onSubmit={handleCreateAgent} className="p-10 space-y-8">
               <div className="grid grid-cols-2 gap-8">
                  <div className="space-y-4">
                    <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest pl-2">Specialist Name</label>
                    <input 
                      type="text" 
                      required
                      placeholder="e.g. Sales Oracle"
                      className="w-full bg-slate-50 border-none rounded-3xl px-6 py-4 text-sm font-bold placeholder:text-slate-300 focus:ring-2 focus:ring-indigo-500 transition-all shadow-inner"
                      value={newAgent.name}
                      onChange={(e: React.ChangeEvent<HTMLInputElement>) => setNewAgent({...newAgent, name: e.target.value})}
                    />
                  </div>
                  <div className="space-y-4">
                    <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest pl-2">Core Category</label>
                    <select 
                      className="w-full bg-slate-50 border-none rounded-3xl px-6 py-4 text-sm font-bold focus:ring-2 focus:ring-indigo-500 transition-all shadow-inner"
                      value={newAgent.category}
                      onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setNewAgent({...newAgent, category: e.target.value})}
                    >
                      <option value="finance">Finance</option>
                      <option value="hr">Human Resources</option>
                      <option value="sales">Sales</option>
                      <option value="ops">Operations</option>
                    </select>
                  </div>
               </div>

               <div className="space-y-4">
                  <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest pl-2">System Persona / Prompt</label>
                  <textarea 
                    required
                    rows={4}
                    placeholder="Enter the specialist's core directive and behavioral guardrails..."
                    className="w-full bg-slate-50 border-none rounded-[32px] px-8 py-6 text-sm font-medium leading-relaxed placeholder:text-slate-300 focus:ring-2 focus:ring-indigo-500 transition-all shadow-inner"
                    value={newAgent.system_prompt}
                    onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setNewAgent({...newAgent, system_prompt: e.target.value})}
                  />
               </div>

               {error && <p className="text-[10px] font-black text-red-500 uppercase tracking-widest text-center">⚠️ {error}</p>}

               <div className="flex gap-4 pt-4">
                  <button 
                    type="button"
                    onClick={() => setIsModalOpen(false)}
                    className="flex-1 bg-slate-100 hover:bg-slate-200 text-slate-500 py-5 rounded-[24px] font-black uppercase tracking-widest text-[11px] transition-all"
                  >Cancel</button>
                  <button 
                    type="submit"
                    className="flex-[2] bg-indigo-600 hover:bg-indigo-700 text-white py-5 rounded-[24px] font-black uppercase tracking-widest text-[11px] shadow-xl shadow-indigo-100 transition-all active:scale-95"
                  >Authorize Specialist</button>
               </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
