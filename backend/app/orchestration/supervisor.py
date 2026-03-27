from langgraph.graph import StateGraph, START, END
from langchain_anthropic import ChatAnthropic
from pydantic import BaseModel
from typing import Optional
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

from typing import Annotated, TypedDict, List, Dict, Any, Optional
import operator
from .tools import run_agent_tool


# ============ STATE ============
class AgentState(TypedDict):
    task_id: str
    input_data: dict
    supervisor_reasoning: str
    specialist_assignments: list
    memory_context: str
    outputs: Annotated[dict, operator.ior]  # Merges dictionaries via |=
    agent_configs: dict
    approval_needed: bool
    final_output: Optional[dict]
    cost_total: float
    timestamp: str



from app.config import settings

# ============ LLM ============
llm = ChatAnthropic(
    model="claude-3-5-sonnet-20241022",
    api_key=settings.ANTHROPIC_API_KEY,
    temperature=0.3,  # Lower for governance
    max_tokens=2000
)

IS_MOCK_MODE = settings.ANTHROPIC_API_KEY.startswith("sk-ant-api03") or not settings.ANTHROPIC_API_KEY



# ============ NODES ============
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.database.models import Agent

def load_agent_configs(state: AgentState) -> AgentState:
    """Load agent configurations from the database"""
    db = SessionLocal()
    try:
        agents = db.query(Agent).filter(Agent.org_id == "org-demo").all()
        agent_configs = {
            a.category: {
                "system_prompt": a.system_prompt,
                "description": a.description,
                "name": a.name
            }
            for a in agents
        }
        logger.info(f"[Supervisor] Loaded {len(agent_configs)} agent configurations.")
        return {"agent_configs": agent_configs}
    finally:
        db.close()



def supervisor_read(state: AgentState) -> AgentState:

    """Supervisor analyzes task and routes to specialists"""
    
    available_agents = "\n".join([
        f"- {cat}: {cfg['description']}" 
        for cat, cfg in state["agent_configs"].items()
    ])
    
    prompt = f"""
You are HelixOS Supervisor Agent. Analyze this incoming task:

Task: {json.dumps(state["input_data"], indent=2)}

Available Specialist Agents:
{available_agents or "No specialists defined. Escalating to human."}

Context: {state["memory_context"] or "No prior context"}


Decide:
1. Which specialist agents to route to? (Only use ones listed above)
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
        if IS_MOCK_MODE:
            # Simulated supervisor reasoning
            data = {
                "reasoning": "Simulated analysis: Routing to available specialists.",
                "assignments": [
                    {"agent_type": cat, "task": f"Mock task for {cat}", "priority": "normal"}
                    for cat in state["agent_configs"].keys()
                ][:2], # Limit to 2 for simplicity

                "needs_approval": False,
                "estimated_cost": 0.01
            }
        else:
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
        
        logger.info(f"[Supervisor] Reasoning: {data.get('reasoning', '')}")
        logger.info(f"[Supervisor] Assigned {len(data.get('assignments', []))} tasks")
        
        return {
            "supervisor_reasoning": data.get("reasoning", ""),
            "specialist_assignments": data.get("assignments", []),
            "approval_needed": data.get("needs_approval", False),
            "cost_total": data.get("estimated_cost", 0.0)
        }

        
    except Exception as e:
        logger.error(f"[Supervisor] Error: {e}")
        return {"approval_needed": True}


def finance_agent(state: AgentState) -> AgentState:
    """Finance specialist processes financial tasks"""
    
    assignment = next(
        (a for a in state["specialist_assignments"] if a["agent_type"] == "finance"),
        None
    )
    
    if not assignment:
        return {} # Return empty dict to signify no change
    
    task = assignment.get("task", "")
    priority = assignment.get("priority", "normal")
    
    config = state["agent_configs"].get("finance", {})
    system_prompt = config.get("system_prompt", "You are the Finance Agent.")
    
    prompt = f"""
{system_prompt}

Execute this task:
Task: {task}
Priority: {priority}
Context: {state["memory_context"]}

You have access to these TOOLS:
1. `save_report(category, content)`: Use this to save a permanent record of your findings.
2. `calculate_financials(expression)`: Use this for math (e.g. 5000 * 1.05).

Respond in JSON ONLY:
{{
  "outcome": "success" | "failure",
  "message": "Human-readable summary",
  "tool_call": {{ "name": "save_report" | "calculate_financials", "params": {{ ... }} }} | null,
  "data": {{ ... }}
}}
"""
    
    try:
        if IS_MOCK_MODE:
            tool_call = {"name": "save_report", "params": {"category": "finance", "content": f"Finance Audit for Task: {task}"}}
            result = {
                "outcome": "success",
                "message": f"Verified financials for task '{task}'. Generated report.",
                "tool_call": tool_call,
                "data": {"verified_amount": 5000}
            }
        else:
            response = llm.invoke(prompt)
            result = json.loads(response.content.strip())

        # Execute Tool if present
        actions_taken = []
        if result.get("tool_call"):
            tool_name = result["tool_call"]["name"]
            tool_params = result["tool_call"]["params"]
            if tool_name == "save_report":
                tool_params["task_id"] = state["task_id"]
                
            tool_result = run_agent_tool(tool_name, tool_params)
            actions_taken.append(f"{tool_name}: {tool_result}")
            logger.info(f"[Finance Agent] Tool {tool_name} returned: {tool_result}")

        result["actions"] = actions_taken
        logger.info(f"[Finance Agent] Completed: {task}")
        
        return {"outputs": {"finance_results": [result]}}
    except Exception as e:
        logger.error(f"[Finance Agent] Error: {e}")
        return {"outputs": {"finance_results": [{"outcome": "failure", "error": str(e)}]}}



def hr_agent(state: AgentState) -> AgentState:
    """HR specialist handles employee tasks"""
    
    assignment = next(
        (a for a in state["specialist_assignments"] if a["agent_type"] == "hr"),
        None
    )
    
    if not assignment:
        return {}
    
    task = assignment.get("task", "")
    
    config = state["agent_configs"].get("hr", {})
    system_prompt = config.get("system_prompt", "You are the HR Agent.")
    
    prompt = f"""
{system_prompt}

Execute this task:
Task: {task}
Context: {state["memory_context"]}

You have access to these TOOLS:
1. `save_report(category, content)`: Use this to save reports to disk.

Respond in JSON ONLY:
{{
  "outcome": "success" | "failure",
  "message": "Human-readable summary",
  "tool_call": {{ "name": "save_report", "params": {{ "category": "hr", "content": "..." }} }} | null,
  "data": {{ ... }}
}}
"""
    
    try:
        if IS_MOCK_MODE:
            tool_call = {"name": "save_report", "params": {"category": "hr", "content": f"HR Assessment for '{task}'"}}
            result = {
                "outcome": "success",
                "message": f"Completed HR task: {task}. Report archived.",
                "tool_call": tool_call,
                "data": {"status": "processed"}
            }
        else:
            response = llm.invoke(prompt)
            result = json.loads(response.content.strip())

        # Execute Tool if present
        actions_taken = []
        if result.get("tool_call"):
            tool_name = result["tool_call"]["name"]
            tool_params = result["tool_call"]["params"]
            if tool_name == "save_report":
                tool_params["task_id"] = state["task_id"]
            
            tool_result = run_agent_tool(tool_name, tool_params)
            actions_taken.append(f"{tool_name}: {tool_result}")

        result["actions"] = actions_taken
        logger.info(f"[HR Agent] Completed: {task}")
        
        return {"outputs": {"hr_results": [result]}}
    except Exception as e:
        logger.error(f"[HR Agent] Error: {e}")
        return {"outputs": {"hr_results": [{"outcome": "failure", "error": str(e)}]}}



def sales_agent(state: AgentState) -> AgentState:
    """Sales specialist handles lead management"""
    
    assignment = next(
        (a for a in state["specialist_assignments"] if a["agent_type"] == "sales"),
        None
    )
    
    if not assignment:
        return {}
    
    task = assignment.get("task", "")
    
    config = state["agent_configs"].get("sales", {})
    system_prompt = config.get("system_prompt", "You are the Sales Agent.")
    
    prompt = f"""
{system_prompt}

Execute this task:
Task: {task}
Context: {state["memory_context"]}

You have access to these TOOLS:
1. `save_report(category, content)`: Use this to save sales reports to disk.

Respond in JSON ONLY:
{{
  "outcome": "success" | "failure",
  "message": "Summary of sales engagement",
  "tool_call": {{ "name": "save_report", "params": {{ "category": "sales", "content": "..." }} }} | null,
  "data": {{ ... }}
}}
"""
    
    try:
        if IS_MOCK_MODE:
            tool_call = {"name": "save_report", "params": {"category": "sales", "content": f"Sales Analysis: {task}"}}
            result = {
                "outcome": "success",
                "message": f"Analyzed leads for '{task}'. Strategy documented.",
                "tool_call": tool_call,
                "data": {"leads_identified": 12}
            }
        else:
            response = llm.invoke(prompt)
            result = json.loads(response.content.strip())

        # Execute Tool if present
        actions_taken = []
        if result.get("tool_call"):
            tool_name = result["tool_call"]["name"]
            tool_params = result["tool_call"]["params"]
            if tool_name == "save_report":
                tool_params["task_id"] = state["task_id"]
            
            tool_result = run_agent_tool(tool_name, tool_params)
            actions_taken.append(f"{tool_name}: {tool_result}")

        result["actions"] = actions_taken
        logger.info(f"[Sales Agent] Completed: {task}")
        
        return {"outputs": {"sales_results": [result]}}
    except Exception as e:
        logger.error(f"[Sales Agent] Error: {e}")
        return {"outputs": {"sales_results": [{"outcome": "failure", "error": str(e)}]}}



def compile_results(state: AgentState) -> AgentState:
    """Compile specialist results into final output"""
    
    # Extract a primary message for the user
    primary_msg = "Task completed successfully."
    for category, results in state["outputs"].items():
        if results and isinstance(results, list):
            res = results[0]
            if isinstance(res, dict) and res.get("message"):
                primary_msg = res["message"]
                break

    final_output = {
        "task_id": state["task_id"],
        "message": primary_msg,
        "supervisor_reasoning": state["supervisor_reasoning"],
        "specialist_results": state["outputs"],
        "total_cost": state["cost_total"],
        "needs_approval": state["approval_needed"],
        "timestamp": datetime.utcnow().isoformat()
    }

    logger.info(f"[Supervisor] Task {state['task_id']} completed. Message: {primary_msg}")
    
    return {"final_output": final_output}


# ============ BUILD GRAPH ============

def initialize_supervisor():
    """Initialize LangGraph supervisor"""
    
    graph = StateGraph(AgentState)
    
    # Add nodes
    graph.add_node("load_agent_configs", load_agent_configs)
    graph.add_node("supervisor_read", supervisor_read)
    graph.add_node("finance_agent", finance_agent)
    graph.add_node("hr_agent", hr_agent)
    graph.add_node("sales_agent", sales_agent)
    graph.add_node("compile_results", compile_results)
    
    # Add edges
    graph.add_edge(START, "load_agent_configs")
    graph.add_edge("load_agent_configs", "supervisor_read")
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