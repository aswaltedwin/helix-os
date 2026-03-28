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
from .memory import get_experience_summary, store_memory



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
            # Intelligent Mock Decomposition for Demo
            raw_task = (state["input_data"].get("task") or "").lower()
            
            assignments = []
            reasoning = "Strategic decomposition initiated."
            
            if "onboard" in raw_task or "new hire" in raw_task:
                reasoning = "Multi-agent onboarding workflow detected. Orchestrating HR and Fiscal setup."
                assignments = [
                    {"agent_type": "hr", "task": "Generate employment contract and verify policy alignment.", "priority": "high"},
                    {"agent_type": "finance", "task": "Initiate payroll record creation and hardware budget allocation.", "priority": "high"}
                ]
            elif "invoice" in raw_task or "payment" in raw_task:
                reasoning = "Financial audit workflow active."
                assignments = [
                    {"agent_type": "finance", "task": f"Analyze and verify: {raw_task}", "priority": "high"}
                ]
            else:
                # Default to a broad analysis
                # This block is removed as the new prompt handles general decomposition
                # For mock mode, we can simulate a general decomposition if no specific keyword is found
                reasoning = "General task analysis initiated. Decomposing into relevant specialist tasks."
                assignments = [
                    {"agent_type": "hr", "task": f"Review HR implications for: {raw_task}", "priority": "normal"},
                    {"agent_type": "finance", "task": f"Assess fiscal impact for: {raw_task}", "priority": "normal"}
                ]

            data = {
                "reasoning": reasoning,
                "assignments": assignments,
                "needs_approval": False,
                "estimated_cost": 0.02
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
    
    # 1. Experience Retrieval (Memory)
    experience = get_experience_summary("finance", task)
    
    # 2. Elite System Prompt (Oracle)
    oracle_prompt = """
You are HelixOS Finance Oracle — an elite financial operations specialist.
EXPERTISE: Invoice processing, PO matching, Fraud detection, and Compliance.
DECISION RULES:
- Always provide reasoning and a confidence score (0.0 - 1.0).
- Flag any transaction > $10,000 immediately.
- Use 'calculate_financials' for all math.
- Use 'verify_purchase_order' to check against policies.
- Use 'detect_fraud_patterns' for every high-value task.
"""
    
    prompt = f"""
{oracle_prompt}

{experience}

Execute this task:
Task: {task}
Priority: {priority}

Respond in JSON ONLY:
{{
  "outcome": "success" | "failure",
  "confidence": 0.95,
  "message": "Step-by-step reasoning",
  "tool_call": {{ "name": "save_report" | "calculate_financials" | "verify_purchase_order" | "detect_fraud_patterns", "params": {{ ... }} }} | null,
  "data": {{ "amount": 0, ... }}
}}
"""
    
    try:
        if IS_MOCK_MODE:
            result = {
                "outcome": "success",
                "confidence": 0.98,
                "message": f"Fiscal validation for objective '{task}' completed. Records verified.",
                "tool_call": {"name": "verify_purchase_order", "params": {"invoice_id": state["task_id"], "amount": 12000.0}},
                "data": {"verified_amount": 12000.0}
            }
        else:
            response = llm.invoke(prompt)
            content = response.content.strip()
            # Try to parse JSON
            if content.startswith("{"):
                result = json.loads(content)
            else:
                # Extract JSON from response if wrapped
                import re
                match = re.search(r'\{.*\}', content, re.DOTALL)
                if match:
                    result = json.loads(match.group())
                else:
                    result = {
                        "outcome": "failure",
                        "confidence": 0.0,
                        "message": "Failed to parse finance agent response.",
                        "tool_call": None,
                        "data": {}
                    }

        # 3. Tool Execution
        actions_taken = []
        if result.get("tool_call"):
            tool_name = result["tool_call"]["name"]
            tool_params = result["tool_call"]["params"]
            if tool_name == "save_report":
                tool_params["task_id"] = state["task_id"]
                
            tool_result = run_agent_tool(tool_name, tool_params)
            actions_taken.append(f"{tool_name}: {tool_result}")
            logger.info(f"[Finance Oracle] Tool {tool_name} returned: {tool_result}")

        # 4. Memory Storage
        store_memory("finance", task, result)

        # 5. Validation Guardrails
        if result.get("confidence", 0) < 0.9:
            actions_taken.append("GUARDRAIL: Low confidence decision. Escalating to supervisor.")
            result["outcome"] = "escalated"

        result["actions"] = actions_taken
        logger.info(f"[Finance Oracle] Decision Confidence: {result.get('confidence')}")
        
        return {"outputs": {"finance_results": [result]}}
    except Exception as e:
        logger.error(f"[Finance Oracle] Error: {e}")
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
    
    # 1. Experience Retrieval (Memory)
    experience = get_experience_summary("hr", task)
    
    # 2. Elite System Prompt (Specialist)
    hr_specialist_prompt = """
You are HelixOS HR Specialist — organizational compliance & talent operations expert.
EXPERTISE: Onboarding, Leave management, Payroll compliance, and Performance.
TOOLS:
- `check_leave_policy(employee_id)`: Check vacation/sick balances.
- `verify_team_coverage(date)`: Check for calendar conflicts.
- `generate_offer_letter(name, position, salary)`: Create official offer documents.
"""
    
    prompt = f"""
{hr_specialist_prompt}

{experience}

Execute this task:
Task: {task}

Respond in JSON ONLY:
{{
  "outcome": "success" | "failure",
  "message": "Human-readable summary of HR action",
  "tool_call": {{ "name": "check_leave_policy" | "verify_team_coverage" | "generate_offer_letter", "params": {{ ... }} }} | null,
  "data": {{ ... }}
}}
"""
    
    try:
        if IS_MOCK_MODE:
            result = {
                "outcome": "success",
                "message": f"Personnel compliance review for '{task}' finalized. Policy alignment confirmed.",
                "tool_call": {"name": "check_leave_policy", "params": {"employee_id": "EMP-811", "task_id": state["task_id"]}},
                "data": {"policy_status": "aligned"}
            }
        else:
            response = llm.invoke(prompt)
            content = response.content.strip()
            # Try to parse JSON
            if content.startswith("{"):
                result = json.loads(content)
            else:
                # Extract JSON from response if wrapped
                import re
                match = re.search(r'\{.*\}', content, re.DOTALL)
                if match:
                    result = json.loads(match.group())
                else:
                    result = {
                        "outcome": "failure",
                        "message": "Failed to parse HR agent response.",
                        "tool_call": None,
                        "data": {}
                    }

        # 3. Tool Execution
        actions_taken = []
        if result.get("tool_call"):
            tool_name = result["tool_call"]["name"]
            tool_params = result["tool_call"]["params"]
            tool_params["task_id"] = state["task_id"]
            
            tool_result = run_agent_tool(tool_name, tool_params)
            actions_taken.append(f"{tool_name}: {tool_result}")

        # 4. Memory Storage
        store_memory("hr", task, result)

        result["actions"] = actions_taken
        logger.info(f"[HR Specialist] Completed: {task}")
        
        return {"outputs": {"hr_results": [result]}}
    except Exception as e:
        logger.error(f"[HR Specialist] Error: {e}")
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
            tool_call = {"name": "save_report", "params": {"category": "sales", "content": f"Sales Strategic Analysis: {task}"}}
            result = {
                "outcome": "success",
                "message": f"Sales optimization strategy for '{task}' implemented. Lead acquisition active.",
                "tool_call": tool_call,
                "data": {"leads_identified": 12}
            }

        else:
            response = llm.invoke(prompt)
            content = response.content.strip()
            # Try to parse JSON
            if content.startswith("{"):
                result = json.loads(content)
            else:
                # Extract JSON from response if wrapped
                import re
                match = re.search(r'\{.*\}', content, re.DOTALL)
                if match:
                    result = json.loads(match.group())
                else:
                    result = {
                        "outcome": "failure",
                        "message": "Failed to parse sales agent response.",
                        "tool_call": None,
                        "data": {}
                    }

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
    """Compile specialist results into final output with executive summary"""
    
    specialist_conclusions = []
    for category, results in state["outputs"].items():
        if results and isinstance(results, list):
            for res in results:
                if isinstance(res, dict) and res.get("message"):
                    # Use a bullet point format for cleaner separation
                    prefix = category.replace("_results", "").upper()
                    specialist_conclusions.append(f"● **{prefix}**: {res['message']}")

    # Synthesize Executive Conclusion
    if specialist_conclusions:
        # Joining with double newlines for frontend splitting or better parsing
        executive_summary = "\n\n".join(specialist_conclusions)
    else:
        executive_summary = "Strategic execution complete. No anomalies detected within specialist domains."

    final_output = {
        "task_id": state["task_id"],
        "input_objective": state["input_data"].get("task") or state["input_data"].get("description", "No description provided"),
        "executive_conclusion": executive_summary,
        "supervisor_reasoning": state["supervisor_reasoning"],
        "specialist_results": state["outputs"],
        "total_cost": state["cost_total"],
        "needs_approval": state["approval_needed"],
        "timestamp": datetime.utcnow().isoformat()
    }

    logger.info(f"[Supervisor] Task {state['task_id']} concluded.")
    
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