from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime
from app.orchestration.supervisor import supervisor_graph, AgentState

router = APIRouter()

class TaskCreate(BaseModel):
    workflow_id: str = "auto-detect"
    input_data: dict

class TaskResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[dict] = None

tasks_db = {}

@router.post("/")
async def create_and_execute_task(task: TaskCreate) -> TaskResponse:
    """Create task and execute via supervisor"""
    
    task_id = str(uuid.uuid4())
    
    # Create state
    state = AgentState(
        task_id=task_id,
        input_data=task.input_data,
        timestamp=datetime.utcnow().isoformat()
    )
    
    # Execute supervisor
    try:
        result = supervisor_graph.invoke(state)
        
        tasks_db[task_id] = {
            "status": "COMPLETED",
            "result": result.final_output,
            "created_at": datetime.utcnow().isoformat()
        }
        
        return TaskResponse(
            task_id=task_id,
            status="COMPLETED",
            result=result.final_output
        )
    
    except Exception as e:
        tasks_db[task_id] = {
            "status": "FAILED",
            "error": str(e),
            "created_at": datetime.utcnow().isoformat()
        }
        
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{task_id}")
async def get_task(task_id: str) -> TaskResponse:
    """Get task result"""
    
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks_db[task_id]
    return TaskResponse(
        task_id=task_id,
        status=task["status"],
        result=task.get("result")
    )