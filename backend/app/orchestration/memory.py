import json
import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

MEMORY_FILE = os.path.join(os.getcwd(), "agent_memory.json")

def ensure_memory_file():
    if not os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
        logger.info(f"Created memory file at {MEMORY_FILE}")

def store_memory(agent_type: str, task: str, decision: dict, outcome: str = "success"):
    """Stores a task-decision pair for future retrieval."""
    ensure_memory_file()
    
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            memories = json.load(f)
        
        memory_entry = {
            "agent_type": agent_type,
            "task": task,
            "decision": decision,
            "outcome": outcome,
            "timestamp": datetime.now().isoformat()
        }
        
        memories.append(memory_entry)
        
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(memories, f, indent=2)
            
        logger.info(f"Stored memory for {agent_type} task: {task[:50]}...")
    except Exception as e:
        logger.error(f"Failed to store memory: {e}")

def retrieve_memories(agent_type: str, query: str, limit: int = 3) -> List[Dict[str, Any]]:
    """Retrieves similar past decisions (simple keyword match for now)."""
    ensure_memory_file()
    
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            memories = json.load(f)
        
        # Simple match: filter by agent_type and query keywords in task description
        query_words = query.lower().split()
        matches = []
        
        relevant_memories = [m for m in memories if m["agent_type"] == agent_type]
        
        for m in relevant_memories:
            task_lower = m["task"].lower()
            match_score = sum(1 for word in query_words if word in task_lower)
            if match_score > 0:
                matches.append((match_score, m))
        
        # Sort by match score (highest first)
        matches.sort(key=lambda x: x[0], reverse=True)
        return [m[1] for m in matches[:limit]]
        
    except Exception as e:
        logger.error(f"Failed to retrieve memories: {e}")
        return []

def get_experience_summary(agent_type: str, task: str) -> str:
    """Formats retrieved memories as a string for LLM context."""
    pasts = retrieve_memories(agent_type, task)
    if not pasts:
        return "No prior experience found for this type of task."
    
    summary = "EXPERIENCE LEDGER (Past Decisions):\n"
    for i, p in enumerate(pasts):
        summary += f"{i+1}. Task: {p['task']}\n   Decision: {p['decision'].get('message', 'No message')}\n   Outcome: {p['outcome']}\n"
    return summary