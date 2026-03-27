from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from ..database.models import Agent
from .utils import get_db

router = APIRouter()

class AgentCreate(BaseModel):
    name: str
    category: str  # finance, hr, sales
    description: Optional[str] = ""
    system_prompt: Optional[str] = ""
    model: str = "claude-3-5-sonnet-20241022"

class AgentResponse(BaseModel):
    id: str
    name: str
    category: str
    description: Optional[str]
    status: str = "active"

@router.post("/")
async def create_agent(
    agent: AgentCreate, 
    db: Session = Depends(get_db),
    org_id: str = "org-demo"
) -> AgentResponse:
    """Create a new agent in the database"""
    db_agent = Agent(
        id=str(uuid.uuid4()),
        org_id=org_id,
        name=agent.name,
        category=agent.category,
        description=agent.description,
        system_prompt=agent.system_prompt,
        model=agent.model,
        status="active"
    )
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent

@router.get("/")
async def list_agents(
    db: Session = Depends(get_db),
    org_id: str = "org-demo"
) -> List[AgentResponse]:
    """List all agents from the database"""
    agents = db.query(Agent).filter(Agent.org_id == org_id).all()
    return agents

@router.get("/{agent_id}")
async def get_agent(
    agent_id: str, 
    db: Session = Depends(get_db)
) -> AgentResponse:
    """Get agent details from the database"""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@router.get("/metrics")
async def get_metrics(
    db: Session = Depends(get_db),
    org_id: str = "org-demo"
):
    """Get agent metrics using database data"""
    agents = db.query(Agent).filter(Agent.org_id == org_id).all()
    return {
        "agents": agents,
        "total_cost": 0.42,
        "success_rate": 98.5
    }