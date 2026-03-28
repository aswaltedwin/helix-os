"use client";

import React from "react";
import { Users, Activity, FileText } from 'lucide-react';

const BLUEPRINTS = [
  {
    id: "wf-onboard",
    title: "Full Executive Onboarding",
    description: "Orchestrates HR (Contracts), Finance (Payroll), and Ops (Access).",
    agents: ["HR", "Finance", "Ops"],
    status: "Production Ready",
    color: "indigo"
  },
  {
    id: "wf-audit",
    title: "Fiscal Compliance Audit",
    description: "Deep-dive scan of ledger records against compliance policy.",
    agents: ["Finance", "Compliance"],
    status: "Active",
    color: "emerald"
  },
  {
    id: "wf-revenue",
    title: "Strategic Revenue Forecast",
    description: "Synthesizes sales pipe and historical fiscal performance.",
    agents: ["Sales", "Finance"],
    status: "Beta",
    color: "purple"
  }
];

export default function WorkflowsPage() {
  const [mounted, setMounted] = React.useState(false);

  React.useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return null;

  return (
    <div className="p-12 max-w-7xl mx-auto min-h-screen bg-slate-50/30">
      <div className="flex flex-col md:flex-row justify-between items-end mb-12 gap-6">
        <div>
          <span className="text-[10px] font-black text-indigo-500 uppercase tracking-[0.3em] mb-2 block">Enterprise Orchestration</span>
          <h2 className="text-4xl font-black text-slate-900 tracking-tight flex items-center gap-3">
            Strategic Blueprints
          </h2>
        </div>
        <button className="bg-indigo-600 hover:bg-indigo-700 text-white px-8 py-4 rounded-[24px] font-black transition-all active:scale-95 flex items-center gap-2 shadow-xl shadow-indigo-100 uppercase tracking-widest text-[11px]">
          <Activity size={16} strokeWidth={3} /> Design Custom Blueprint
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {BLUEPRINTS.map((bp) => (
          <div key={bp.id} className="group bg-white rounded-[40px] border border-slate-100 p-8 shadow-sm hover:shadow-2xl hover:shadow-indigo-100 hover:-translate-y-2 transition-all duration-500 relative overflow-hidden">
            <div className={`absolute top-0 right-0 p-8 opacity-5 group-hover:scale-125 transition-all duration-700`}>
              <Activity size={120} />
            </div>
            
            <div className="flex justify-between items-start mb-6">
              <div className={`p-4 rounded-3xl bg-${bp.color}-50 text-${bp.color}-600`}>
                {bp.id === "wf-onboard" && <Users size={24} />}
                {bp.id === "wf-audit" && <Activity size={24} />}
                {bp.id === "wf-revenue" && <Activity size={24} />}
              </div>
              <span className="text-[10px] font-black text-slate-300 uppercase tracking-[0.1em] border-b border-slate-100 pb-1">
                {bp.status}
              </span>
            </div>

            <h3 className="text-xl font-black text-slate-900 mb-3 group-hover:text-indigo-600 transition-colors uppercase tracking-tight">{bp.title}</h3>
            <p className="text-sm text-slate-500 font-medium leading-relaxed mb-8">
              {bp.description}
            </p>

            <div className="space-y-4">
               <div className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Active Swarm Chain</div>
               <div className="flex items-center gap-2">
                 {bp.agents.map((agent, i) => (
                   <React.Fragment key={agent}>
                     <div className="bg-slate-50 border border-slate-100 px-4 py-2 rounded-2xl text-[10px] font-bold text-slate-600 uppercase">
                       {agent}
                     </div>
                     {i < bp.agents.length - 1 && (
                       <Activity size={12} className="text-slate-200 rotate-90" />
                     )}
                   </React.Fragment>
                 ))}
               </div>
            </div>

            <button className="w-full mt-10 bg-slate-50 group-hover:bg-indigo-50 text-slate-400 group-hover:text-indigo-600 py-4 rounded-3xl text-[11px] font-black uppercase tracking-widest transition-all">
              Initialize Workflow
            </button>
          </div>
        ))}

        {/* Create Card */}
        <div className="border-4 border-dashed border-slate-100 rounded-[40px] flex flex-col items-center justify-center p-12 hover:border-indigo-100 hover:bg-indigo-50/20 transition-all group cursor-pointer">
           <div className="w-20 h-20 bg-slate-50 rounded-full flex items-center justify-center text-slate-300 group-hover:bg-indigo-100 group-hover:text-indigo-600 transition-all mb-6">
             <Activity size={32} />
           </div>
           <span className="text-sm font-black text-slate-300 group-hover:text-indigo-600 uppercase tracking-widest">New Deployment</span>
        </div>
      </div>

      <div className="mt-20 bg-slate-900 rounded-[48px] p-12 text-white relative overflow-hidden">
        <div className="absolute top-0 right-0 p-12 opacity-10">
           <Activity size={160} />
        </div>
        <div className="max-w-2xl relative z-10">
          <span className="text-indigo-400 text-[10px] font-black uppercase tracking-[0.4em] mb-4 block">Visual Swarm Orchestrator</span>
          <h2 className="text-3xl font-black mb-6 uppercase tracking-tight">The Helix Workflow Engine</h2>
          <p className="text-slate-400 font-medium leading-relaxed mb-8">
            HelixOS flows are autonomous directed acyclic graphs (DAGs). 
            Our engine dynamically routes intents between your specialists, 
            ensuring fiscal governance and policy compliance at every node.
          </p>
          <div className="bg-white/5 border border-white/10 p-4 rounded-3xl font-mono text-xs text-indigo-200">
             // Swarm Schema v0.2.1-stable <br/>
             dispatch_strategy: "autonomous_dag" <br/>
             governance_mode: "strategic_override" <br/>
             specialist_coordination: "enabled"
          </div>
        </div>
      </div>
    </div>
  );
}
