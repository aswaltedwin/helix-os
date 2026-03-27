from sqlalchemy import Column, String, JSON, Boolean, Float, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database.base import Base

class Organization(Base):
    __tablename__ = "organizations"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, index=True)
    industry = Column(String(100))
    data_residency = Column(String(50), default="IN")
    status = Column(String(20), default="ACTIVE")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    agents = relationship("Agent", back_populates="organization")
    workflows = relationship("Workflow", back_populates="organization")
    tasks = relationship("Task", back_populates="organization")

class Agent(Base):
    __tablename__ = "agents"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id = Column(String(36), ForeignKey("organizations.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(50), nullable=False)  # finance, hr, sales, compliance, ops
    description = Column(Text)
    system_prompt = Column(Text)
    model = Column(String(50), default="claude-3-5-sonnet-20241022")
    capabilities = Column(JSON, default=list)
    status = Column(String(20), default="ACTIVE")
    cost_per_call = Column(Float, default=0.01)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization", back_populates="agents")
    tasks = relationship("Task", back_populates="agent")

class Workflow(Base):
    __tablename__ = "workflows"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id = Column(String(36), ForeignKey("organizations.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    agent_graph = Column(JSON)
    auto_discovered = Column(Boolean, default=False)
    status = Column(String(20), default="ACTIVE")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization", back_populates="workflows")
    tasks = relationship("Task", back_populates="workflow")

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id = Column(String(36), ForeignKey("organizations.id"), nullable=False, index=True)
    workflow_id = Column(String(36), ForeignKey("workflows.id"), index=True)
    agent_id = Column(String(36), ForeignKey("agents.id"), index=True)
    input_data = Column(JSON)
    output_data = Column(JSON)
    status = Column(String(20), default="PENDING")
    cost_actual = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Relationships
    organization = relationship("Organization", back_populates="tasks")
    workflow = relationship("Workflow", back_populates="tasks")
    agent = relationship("Agent", back_populates="tasks")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id = Column(String(36), ForeignKey("organizations.id"), nullable=False, index=True)
    agent_id = Column(String(36), ForeignKey("agents.id"), index=True)
    task_id = Column(String(36), ForeignKey("tasks.id"), index=True)
    action = Column(String(100), nullable=False)
    input_data = Column(JSON)
    output_data = Column(JSON)
    watermark_hash = Column(String(256))
    cost = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)