from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import json
import time
import logging

from ..orchestration.supervisor import supervisor_graph
from ..database.models import Task
from .utils import get_db

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/execute")
async def execute_task(
    task_input: dict,
    db: Session = Depends(get_db),
    org_id: str = "org-demo"
):
    """
    Execute a task through the supervisor agent.
    """
    try:
        # Invoke supervisor graph
        result = supervisor_graph.invoke(
            {
                "task_id": f"task-{int(time.time())}",
                "input_data": task_input,
                "supervisor_reasoning": "",
                "specialist_assignments": [],
                "memory_context": "",
                "outputs": {},
                "approval_needed": False,
                "final_output": None,
                "cost_total": 0.0,
            }
        )
        
        # Log to database
        db_task = Task(
            id=result["task_id"],
            org_id=org_id,
            input_data=task_input,
            output_data=result["final_output"],
            status="COMPLETED",
            cost_actual=result["cost_total"]
        )
        db.add(db_task)
        db.commit()
        
        # Extract a human-readable message from result
        final_msg = "Task completed successfully."
        if result["final_output"] and "specialist_results" in result["final_output"]:
            # Try to get the first message from any specialist result
            results = result["final_output"]["specialist_results"]
            for category in results:
                if results[category] and isinstance(results[category], list):
                    first_res = results[category][0]
                    if isinstance(first_res, dict) and "message" in first_res:
                        final_msg = first_res["message"]
                        break
        
        return {
            "task_id": result["task_id"],
            "status": "completed",
            "message": final_msg,
            "output": result["final_output"],
            "cost": result["cost_total"],
            "reasoning": result["supervisor_reasoning"]
        }
        
    except Exception as e:
        logger.error(f"Task execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def list_tasks(
    db: Session = Depends(get_db),
    limit: int = 10
):
    """List recent tasks"""
    tasks = db.query(Task).order_by(Task.created_at.desc()).limit(limit).all()
    return [
        {
            "id": t.id,
            "status": t.status,
            "created_at": t.created_at,
            "message": t.output_data.get("message") if t.output_data else None,
            "output": t.output_data,
            "cost": t.cost_actual
        }

        for t in tasks
    ]