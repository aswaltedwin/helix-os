from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import uuid

router = APIRouter()

class AgentCreate(BaseModel):
    name: str
    category: str  # finance, hr, sales
    system_prompt: str
    model: str = "claude-3-5-sonnet-20241022"

class AgentResponse(BaseModel):
    id: str
    name: str
    category: str
    status: str = "active"

# TODO: Implement DB integration (Day 3)
agents_db = {}

@router.post("/")
async def create_agent(agent: AgentCreate) -> AgentResponse:
    """Create a new agent"""
    agent_id = str(uuid.uuid4())
    agent_dict = {**agent.dict(), "id": agent_id, "status": "active"}
    agents_db[agent_id] = agent_dict
    return agent_dict

@router.get("/")
async def list_agents() -> List[AgentResponse]:
    """List all agents"""
    return list(agents_db.values())

@router.get("/{agent_id}")
async def get_agent(agent_id: str) -> AgentResponse:
    """Get agent details"""
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agents_db[agent_id]

@router.get("/metrics")
async def get_metrics():
    """Get agent metrics (stub)"""
    return {
        "agents": list(agents_db.values()),
        "total_cost": 0.42,
        "success_rate": 98.5
    }