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
    status: str = "ACTIVE"


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
        status="ACTIVE"

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

@router.get("/metrics")
async def get_metrics(
    db: Session = Depends(get_db),
    org_id: str = "org-demo"
):
    """Get agent metrics using database data"""
    agents = db.query(Agent).filter(Agent.org_id == org_id).all()
    from sqlalchemy import func
    from ..database.models import Task
    
    # Calculate real totals
    total_tasks = db.query(Task).count()
    completed_tasks = db.query(Task).filter(Task.status == "COMPLETED").count()
    total_cost = db.query(func.sum(Task.cost_actual)).scalar() or 0.0
    
    success_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 100.0

    return {
        "agents": agents,
        "total_cost": float(total_cost),
        "success_rate": float(success_rate)
    }

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

@router.put("/{agent_id}")
async def update_agent(
    agent_id: str,
    agent_data: AgentCreate,
    db: Session = Depends(get_db)
) -> AgentResponse:
    """Update an existing agent"""
    db_agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not db_agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    db_agent.name = agent_data.name
    db_agent.category = agent_data.category
    db_agent.description = agent_data.description
    db_agent.system_prompt = agent_data.system_prompt
    db_agent.model = agent_data.model
    
    db.commit()
    db.refresh(db_agent)
    return db_agent