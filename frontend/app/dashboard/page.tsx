"use client";

import React from "react";
import Link from "next/link";
import { FileText, Activity } from 'lucide-react';

interface Task {
  id: string;
  status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED';
  input_data: any;
  input_objective?: string;
  executive_conclusion?: string;
  supervisor_reasoning?: string;
  specialist_results?: Record<string, any[]>;
  created_at: string;
  total_cost?: number;
  cost?: number; // fallback for legacy data
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
  const [metrics, setMetrics] = React.useState<MetricsData | null>(null);
  const [tasks, setTasks] = React.useState<Task[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [taskInput, setTaskInput] = React.useState("");
  const [isRunning, setIsRunning] = React.useState(false);
  const [errorMsg, setErrorMsg] = React.useState<string | null>(null);
  const [selectedTask, setSelectedTask] = React.useState<Task | null>(null);
  const [isHistoryOpen, setIsHistoryOpen] = React.useState(false);

  const fetchData = async () => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    try {
      const [metricsRes, tasksRes] = await Promise.all([
        fetch(`${apiUrl}/api/agents/metrics`),
        fetch(`${apiUrl}/api/tasks`)
      ]);
      
      if (metricsRes.ok && tasksRes.ok) {
        const metricsData = await metricsRes.json();
        const tasksData = await tasksRes.json();
        setMetrics(metricsData);
        setTasks(tasksData);
      } else {
        throw new Error("Backend response error");
      }

    } catch (error) {
      console.error("Dashboard Fetch Error:", error);
      setErrorMsg("Failed to synchronize with HelixOS backend. Verify the API is online.");
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleRunTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!taskInput.trim()) return;

    setIsRunning(true);
    setErrorMsg(null);
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    try {
      const res = await fetch(`${apiUrl}/api/tasks/execute`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ task: taskInput }),
      });
      if (res.ok) {
        setTaskInput("");
        fetchData();
      } else {
        const errorData = await res.json().catch(() => ({ detail: "Unknown server error" }));
        setErrorMsg(errorData.detail || "Task execution failed. Please check backend logs.");
      }
    } catch (error) {
      console.error("Task Execution Error:", error);
      setErrorMsg("Network error. Is the backend running?");
    } finally {
      setIsRunning(false);
    }
  };


  if (loading)
    return (
      <div className="p-8 text-center text-gray-500 animate-pulse">
        Initializing HelixOS Dashboard...
      </div>
    );

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <div className="flex justify-between items-center mb-12">
        <div>
          <h2 className="text-4xl font-black text-gray-900 tracking-tight">System Overview</h2>
          <p className="text-gray-500 mt-2 font-medium">Monitor and orchestrate your autonomous workforce.</p>
        </div>
      </div>

      {/* Task Driver */}
      <div className="mb-12">
        <label className="block text-xs font-black text-indigo-500 uppercase tracking-[0.2em] mb-4 text-center">Autonomous Workforce Controller</label>
        <div className="bg-white p-2 rounded-[32px] shadow-xl shadow-indigo-100/50 border border-indigo-50 flex items-center gap-2 group focus-within:ring-2 focus-within:ring-indigo-500 transition-all max-w-4xl mx-auto">
          <input
            type="text"
            placeholder="Type a goal for your agents... (e.g. Process the new invoice batch)"
            className="flex-1 bg-transparent border-none focus:ring-0 px-6 py-4 text-gray-800 placeholder:text-gray-400 font-medium"
            value={taskInput}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setTaskInput(e.target.value)}
            disabled={isRunning}
          />
          <button
            onClick={handleRunTask}
            disabled={isRunning || !taskInput.trim()}
            className="bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-200 text-white px-8 py-4 rounded-[24px] font-black transition-all active:scale-95 flex items-center gap-2 min-w-[160px] justify-center"
          >
            {isRunning ? (
              <>
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Processing...
              </>
            ) : (
              "Authorize Strategic Swarm"
            )}
          </button>
        </div>
        
        {/* Quick Start Examples */}
        <div className="mt-6 flex flex-wrap justify-center gap-3">
          {[
            "Analyze recent sales leads",
            "Verify all pending invoices",
            "Calculate monthly revenue forecast",
            "Audit HR compliance records"
          ].map((example) => (
            <button
              key={example}
              onClick={() => {
                setTaskInput(example);
                // Optionally auto-run here, but better to let user see it first
              }}
              className="text-[10px] font-bold text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 px-4 py-2 rounded-full border border-gray-100 transition-all uppercase tracking-tighter"
            >
              {example}
            </button>
          ))}
        </div>

        
        {errorMsg && (
          <div className="mt-4 p-4 bg-red-50 border border-red-100 rounded-2xl text-red-600 text-xs font-bold text-center animate-in slide-in-from-top-2 max-w-4xl mx-auto">
            ⚠️ {errorMsg}
          </div>
        )}
      </div>



      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
        <Card title="Active Agents" value={metrics?.agents?.length ?? 0} color="blue" />
        <Card title="Success Rate" value={`${metrics?.success_rate?.toFixed(1) ?? 0}%`} color="green" />
        <Card title="Compute Cost" value={`$${metrics?.total_cost?.toFixed(3) ?? 0}`} color="purple" />
        <Card title="Total Tasks" value={tasks.length} color="orange" />
      </div>


      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Agents Table */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-100 flex justify-between items-center bg-gray-50/10">
            <h3 className="text-lg font-semibold text-gray-800">Operational Agents</h3>
            <Link 
              href="/dashboard/agents" 
              className="text-[10px] font-black text-indigo-500 hover:text-indigo-700 bg-indigo-50 px-3 py-1 rounded-full uppercase tracking-widest transition-all"
            >
              Manage Specialists →
            </Link>
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
            <h3 className="text-lg font-semibold text-gray-800 focus:outline-none">Recent Activity</h3>
            <button 
              onClick={() => setIsHistoryOpen(true)}
              className="text-[10px] font-black text-indigo-500 hover:text-indigo-700 hover:underline px-3 py-1 bg-indigo-50 rounded-full transition-all uppercase tracking-widest"
            >
              View Full History
            </button>
          </div>

          <div className="divide-y divide-gray-100 max-h-[400px] overflow-auto">
            {tasks.length > 0 ? (
              tasks.slice(0, 5).map((task: Task) => (
                <div 
                  key={task.id} 
                  className="p-4 hover:bg-indigo-50/50 cursor-pointer transition-colors group relative"
                  onClick={() => setSelectedTask(task)}
                >
                  <div className="absolute inset-y-0 right-4 flex items-center opacity-0 group-hover:opacity-100 transition-opacity">
                    <div className="bg-indigo-600 text-white text-[10px] font-black px-4 py-2 rounded-full shadow-lg shadow-indigo-200">
                      OPEN REPORT →
                    </div>
                  </div>

                  <div className="flex justify-between items-start mb-1">
                    <span className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">
                      Task {task.id.split('-')[1]}
                    </span>
                    <span className="text-[10px] text-gray-400 font-mono pr-2">
                      {new Date(task.created_at).toLocaleTimeString()}
                    </span>
                  </div>
                  <p className="text-sm font-medium text-gray-800 line-clamp-2 mb-2 pr-24">
                    {task.input_objective || (typeof task.input_data === 'string' ? task.input_data : task.input_data?.description) || "Initializing task execution..."}
                  </p>
                  <div className="flex justify-between items-center text-[10px]">

                    <span className={`px-2 py-0.5 rounded-full font-bold uppercase ${
                      task.status === 'COMPLETED' ? 'bg-blue-50 text-blue-600' : 'bg-amber-50 text-amber-600'
                    }`}>
                      {task.status}
                    </span>
                    <span className="font-semibold text-gray-500 mr-2">Cost: ${task.total_cost?.toFixed(3) ?? 0}</span>
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

      {/* Task History Modal */}
      {isHistoryOpen && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-md z-[60] flex items-center justify-center p-4">
          <div className="bg-white rounded-[32px] shadow-2xl w-full max-w-5xl h-[80vh] overflow-hidden flex flex-col animate-in slide-in-from-bottom-8 duration-300">
            <div className="p-8 border-b border-gray-100 flex justify-between items-center bg-gray-50/50">
              <div>
                <span className="text-[10px] font-black text-indigo-500 uppercase tracking-widest">HelixOS Ledger</span>
                <h3 className="text-2xl font-black text-gray-900 mt-1 uppercase tracking-tight">Full Execution History</h3>
              </div>
              <button 
                onClick={() => setIsHistoryOpen(false)}
                className="bg-gray-100 hover:bg-gray-200 text-gray-500 hover:text-gray-900 transition-all p-3 rounded-full"
              >
                ✕ Close
              </button>
            </div>
            <div className="p-0 overflow-auto divide-y divide-gray-100">
              {tasks.map((task: Task) => (


                <div 
                  key={task.id} 
                  className="p-6 hover:bg-gray-50 cursor-pointer flex items-center justify-between group transition-colors"
                  onClick={() => {
                    setSelectedTask(task);
                    setIsHistoryOpen(false);
                  }}
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-4 mb-2">
                      <span className="text-xs font-black text-gray-400">#{task.id}</span>
                      <span className={`px-2 py-1 rounded text-[10px] font-black ${
                        task.status === 'COMPLETED' ? 'bg-blue-50 text-blue-600' : 'bg-amber-50 text-amber-600'
                      }`}>
                        {task.status}
                      </span>
                      <span className="text-xs text-gray-400 font-medium">{new Date(task.created_at).toLocaleString()}</span>
                    </div>
                    <p className="text-lg font-bold text-gray-800">{task.executive_conclusion || "Processing..."}</p>
                  </div>
                  <div className="text-right">
                    <div className="text-xs font-black text-indigo-600 mb-1 leading-none uppercase tracking-widest">${(task.total_cost || task.cost || 0).toFixed(4)}</div>

                    <div className="text-[10px] font-bold text-gray-300 uppercase">Compute Cost</div>
                    <div className="mt-3 opacity-0 group-hover:opacity-100 transition-opacity bg-indigo-600 text-white text-[10px] font-black px-4 py-2 rounded-full inline-block">
                      OPEN REPORT
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Task Detail Modal */}
      {selectedTask && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col animate-in zoom-in-95 duration-200">
            <div className="p-6 border-b border-gray-100 flex justify-between items-center bg-gray-50/50">
              <div>
                <span className="text-[10px] font-black text-indigo-500 uppercase tracking-widest">HelixOS Intelligence Engine</span>
                <h3 className="text-xl font-bold text-gray-900 mt-1">Orchestration Report</h3>
              </div>
              <button 
                onClick={() => setSelectedTask(null)}
                className="text-gray-400 hover:text-gray-900 transition-colors p-2"
              >
                ✕
              </button>
            </div>
            
            <div className="flex-1 overflow-auto p-8">
              {/* New Objective Section */}
              <div className="bg-slate-50 border border-slate-200 rounded-2xl p-6 mb-8">
                <h3 className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-3 flex items-center gap-2">
                  <FileText size={14} /> Original Objective
                </h3>
                <p className="text-lg font-bold text-slate-800 leading-tight">
                  {selectedTask.input_objective || (typeof selectedTask.input_data === 'string' ? selectedTask.input_data : (selectedTask.input_data?.task || selectedTask.input_data?.description)) || "No objective defined"}
                </p>
              </div>

              {/* Supervisor Section */}



              {/* Specialist Section */}
              <div>
                <h4 className="text-xs font-black text-gray-400 uppercase tracking-widest mb-6">Specialist Workforce Execution</h4>
                <div className="space-y-6">
                  {selectedTask.output?.specialist_results ? (
                    Object.entries(selectedTask.output.specialist_results).map(([agent, results]) => (
                      <div key={agent} className="border-l-4 border-indigo-500 pl-6 py-2">
                        <div className="flex items-center gap-2 mb-3">
                          <span className="text-[10px] font-black text-indigo-600 uppercase tracking-tighter bg-indigo-50 px-2 py-1 rounded">
                            {agent.replace("_results", "")} Agent
                          </span>
                          <span className="text-[10px] font-bold text-emerald-600 uppercase bg-emerald-50 px-2 py-1 rounded italic">Success</span>
                        </div>
                        {(results as any[]).map((res: any, i: number) => (

                          <div key={i} className="space-y-3 mb-4 last:mb-0">
                            <p className="text-sm font-semibold text-gray-800">{res.message}</p>
                            
                            {/* Tools/Actions Display */}
                            {res.actions && res.actions.length > 0 && (
                              <div className="flex flex-wrap gap-2 mt-2">
                                {res.actions.map((act: string, idx: number) => (
                                  <div key={idx} className="flex items-center gap-1.5 bg-indigo-50 text-indigo-700 border border-indigo-100 px-3 py-1 rounded-lg text-[9px] font-black uppercase tracking-tight">
                                    <span className="opacity-50">⚡</span> {act}
                                  </div>
                                ))}
                              </div>
                            )}

                            {res.amount && <p className="text-xs text-indigo-600 font-black">Transaction Value: ${res.amount}</p>}
                          </div>
                        ))}

                      </div>
                    ))
                  ) : (
                    <div className="text-center py-12 bg-gray-50 rounded-2xl border border-dashed border-gray-200">
                      <p className="text-sm text-gray-400 font-medium italic">Detailed execution logs are being initialized for this record.</p>
                    </div>
                  )}
                </div>
              </div>

              {/* New Executive Conclusion Section */}
              {selectedTask.executive_conclusion && (
                <div className="mt-10 bg-indigo-600 rounded-2xl p-8 shadow-xl shadow-indigo-200 relative overflow-hidden group">
                  <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:scale-110 transition-transform">
                    <Activity size={80} />
                  </div>
                  <h3 className="text-[10px] font-black text-indigo-100 uppercase tracking-widest mb-4 flex items-center gap-2">
                    Final Executive Conclusion
                  </h3>

                  <div className="text-xl font-bold text-white leading-relaxed relative z-10 whitespace-pre-wrap">
                    {selectedTask.executive_conclusion}
                  </div>

                </div>
              )}
            </div>


            <div className="p-6 border-t border-gray-100 bg-gray-50/30 flex justify-between items-center text-[10px] font-bold text-gray-400">
              <div className="flex gap-4">
                <span>Task ID: {selectedTask.id}</span>
                <span>Created: {new Date(selectedTask.created_at).toLocaleString()}</span>
              </div>
              <div className="text-indigo-600">Computation Cost: ${(selectedTask.total_cost || selectedTask.cost || 0).toFixed(4)}</div>
            </div>
          </div>
        </div>
      )}

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
