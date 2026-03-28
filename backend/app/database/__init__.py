from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

from app.database.base import Base

def init_db():
    from app.database import models
    Base.metadata.create_all(bind=engine)
    
    # Seed default organization if it doesn't exist
    db = SessionLocal()
    try:
        org_id = "org-demo"
        org = db.query(models.Organization).filter(models.Organization.id == org_id).first()
        if not org:
            org = models.Organization(
                id=org_id,
                name="Demo Organization",
                industry="Technology"
            )
            db.add(org)
            db.commit()
        
        # Seed default agents
        default_agents = [
            {
                "id": "agent-finance",
                "name": "Finance Oracle",
                "category": "finance",
                "description": "Elite financial analysis and ledger verification agent.",
                "system_prompt": "You are the Finance Oracle. You analyze transactions, verify ledger integrity, and provide fiscal insights.",
                "capabilities": ["audit", "forecasting", "reconciliation"]
            },
            {
                "id": "agent-hr",
                "name": "HR Specialist",
                "category": "hr",
                "description": "Corporate policy and employee relations specialist.",
                "system_prompt": "You are the HR Specialist. You manage company policies, onboarding workflows, and employee compliance.",
                "capabilities": ["onboarding", "policy_query", "compliance"]
            }
        ]
        
        for agent_data in default_agents:
            agent = db.query(models.Agent).filter(models.Agent.id == agent_data["id"]).first()
            if not agent:
                agent = models.Agent(
                    id=agent_data["id"],
                    org_id=org_id,
                    name=agent_data["name"],
                    category=agent_data["category"],
                    description=agent_data["description"],
                    system_prompt=agent_data["system_prompt"],
                    capabilities=agent_data["capabilities"],
                    status="ACTIVE"
                )
                db.add(agent)
        db.commit()
    finally:
        db.close()

