from langgraph.graph import StateGraph, START, END
from langchain_anthropic import ChatAnthropic
from pydantic import BaseModel
from typing import Optional
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# ============ STATE ============
class AgentState(BaseModel):
    task_id: str
    input_data: dict
    supervisor_reasoning: str = ""
    specialist_assignments: list = []
    memory_context: str = ""
    outputs: dict = {}
    approval_needed: bool = False
    final_output: Optional[dict] = None
    cost_total: float = 0.0
    timestamp: str = ""

# ============ LLM ============
llm = ChatAnthropic(
    model="claude-3-5-sonnet-20241022",
    temperature=0.3,  # Lower for governance
    max_tokens=2000
)

# ============ NODES ============

def supervisor_read(state: AgentState) -> AgentState:
    """Supervisor analyzes task and routes to specialists"""
    
    prompt = f"""
You are HelixOS Supervisor Agent. Analyze this incoming task:

Task: {json.dumps(state.input_data, indent=2)}

Context: {state.memory_context or "No prior context"}

Decide:
1. Which specialist agents to route to (finance, hr, sales, compliance, ops)?
2. What are the subtasks?
3. Does this need human approval?
4. Estimated cost?

Respond ONLY in JSON (no markdown):
{{
  "reasoning": "...",
  "assignments": [
    {{"agent_type": "finance", "task": "Process invoice", "priority": "high"}},
    {{"agent_type": "compliance", "task": "Check policies", "priority": "high"}}
  ],
  "needs_approval": false,
  "estimated_cost": 0.05
}}
"""
    
    try:
        response = llm.invoke(prompt)
        content = response.content.strip()
        
        # Try to parse JSON
        if content.startswith("{"):
            data = json.loads(content)
        else:
            # Extract JSON from response if wrapped
            import re
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match:
                data = json.loads(match.group())
            else:
                data = {
                    "reasoning": "Failed to parse response",
                    "assignments": [],
                    "needs_approval": True,
                    "estimated_cost": 0.0
                }
        
        state.supervisor_reasoning = data.get("reasoning", "")
        state.specialist_assignments = data.get("assignments", [])
        state.approval_needed = data.get("needs_approval", False)
        state.cost_total = data.get("estimated_cost", 0.0)
        
        logger.info(f"[Supervisor] Assigned {len(state.specialist_assignments)} tasks")
        
    except Exception as e:
        logger.error(f"[Supervisor] Error: {e}")
        state.approval_needed = True
    
    return state

def finance_agent(state: AgentState) -> AgentState:
    """Finance specialist processes financial tasks"""
    
    assignment = next(
        (a for a in state.specialist_assignments if a["agent_type"] == "finance"),
        None
    )
    
    if not assignment:
        return state
    
    task = assignment.get("task", "")
    priority = assignment.get("priority", "normal")
    
    prompt = f"""
You are Finance Agent. Execute this task:

Task: {task}
Priority: {priority}
Context: {state.memory_context}

Use tools: read_erp, write_erp, send_email, escalate_to_human

Execute step-by-step:
1. Read relevant data
2. Apply company policies
3. Flag for approval if needed

Respond in JSON:
{{
  "outcome": "success|failure|escalated",
  "actions": ["action1"],
  "amount": 0,
  "needs_approval": false,
  "message": "..."
}}
"""
    
    try:
        response = llm.invoke(prompt)
        result = json.loads(response.content)
        
        if "finance_results" not in state.outputs:
            state.outputs["finance_results"] = []
        state.outputs["finance_results"].append(result)
        
        logger.info(f"[Finance Agent] Completed: {task}")
        
    except Exception as e:
        logger.error(f"[Finance Agent] Error: {e}")
        state.outputs["finance_results"] = [{"outcome": "failure", "error": str(e)}]
    
    return state

def hr_agent(state: AgentState) -> AgentState:
    """HR specialist handles employee tasks"""
    
    assignment = next(
        (a for a in state.specialist_assignments if a["agent_type"] == "hr"),
        None
    )
    
    if not assignment:
        return state
    
    task = assignment.get("task", "")
    
    prompt = f"""
You are HR Agent. Execute this task:

Task: {task}
Context: {state.memory_context}

Respond in JSON:
{{
  "outcome": "success|failure",
  "message": "..."
}}
"""
    
    try:
        response = llm.invoke(prompt)
        result = json.loads(response.content)
        
        if "hr_results" not in state.outputs:
            state.outputs["hr_results"] = []
        state.outputs["hr_results"].append(result)
        
        logger.info(f"[HR Agent] Completed: {task}")
        
    except Exception as e:
        logger.error(f"[HR Agent] Error: {e}")
        state.outputs["hr_results"] = [{"outcome": "failure", "error": str(e)}]
    
    return state

def sales_agent(state: AgentState) -> AgentState:
    """Sales specialist handles lead management"""
    
    assignment = next(
        (a for a in state.specialist_assignments if a["agent_type"] == "sales"),
        None
    )
    
    if not assignment:
        return state
    
    task = assignment.get("task", "")
    
    prompt = f"""
You are Sales Agent. Execute this task:

Task: {task}
Context: {state.memory_context}

Respond in JSON:
{{
  "outcome": "success",
  "score": 0,
  "message": "..."
}}
"""
    
    try:
        response = llm.invoke(prompt)
        result = json.loads(response.content)
        
        if "sales_results" not in state.outputs:
            state.outputs["sales_results"] = []
        state.outputs["sales_results"].append(result)
        
        logger.info(f"[Sales Agent] Completed: {task}")
        
    except Exception as e:
        logger.error(f"[Sales Agent] Error: {e}")
        state.outputs["sales_results"] = [{"outcome": "failure", "error": str(e)}]
    
    return state

def compile_results(state: AgentState) -> AgentState:
    """Compile specialist results into final output"""
    
    state.final_output = {
        "task_id": state.task_id,
        "supervisor_reasoning": state.supervisor_reasoning,
        "specialist_results": state.outputs,
        "total_cost": state.cost_total,
        "needs_approval": state.approval_needed,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    logger.info(f"[Supervisor] Task {state.task_id} completed")
    
    return state

# ============ BUILD GRAPH ============

def initialize_supervisor():
    """Initialize LangGraph supervisor"""
    
    graph = StateGraph(AgentState)
    
    # Add nodes
    graph.add_node("supervisor_read", supervisor_read)
    graph.add_node("finance_agent", finance_agent)
    graph.add_node("hr_agent", hr_agent)
    graph.add_node("sales_agent", sales_agent)
    graph.add_node("compile_results", compile_results)
    
    # Add edges (parallel execution of specialist agents)
    graph.add_edge(START, "supervisor_read")
    graph.add_edge("supervisor_read", "finance_agent")
    graph.add_edge("supervisor_read", "hr_agent")
    graph.add_edge("supervisor_read", "sales_agent")
    graph.add_edge("finance_agent", "compile_results")
    graph.add_edge("hr_agent", "compile_results")
    graph.add_edge("sales_agent", "compile_results")
    graph.add_edge("compile_results", END)
    
    return graph.compile()

# Compile at module load
supervisor_graph = initialize_supervisor()