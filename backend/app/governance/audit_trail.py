import hashlib
import json
from datetime import datetime

class DigitalWatermark:
    """Create tamper-proof watermarks for agent outputs"""
    
    @staticmethod
    def generate(agent_id: str, input_data: str, output: str) -> dict:
        """Generate watermark"""
        
        timestamp = datetime.utcnow().isoformat()
        
        input_hash = hashlib.sha256(input_data.encode()).hexdigest()
        output_hash = hashlib.sha256(output.encode()).hexdigest()
        
        watermark = {
            "agent_id": agent_id,
            "timestamp": timestamp,
            "input_hash": input_hash,
            "output_hash": output_hash,
            "version": "1.0"
        }
        
        return watermark

def log_execution(agent_id: str, task_id: str, input_data: dict, output: dict, cost: float) -> dict:
    """Log agent execution with watermark"""
    
    output_str = json.dumps(output)
    input_str = json.dumps(input_data)
    
    watermark = DigitalWatermark.generate(agent_id, input_str, output_str)
    
    audit_record = {
        "agent_id": agent_id,
        "task_id": task_id,
        "input_data": input_data,
        "output_data": output,
        "watermark_hash": watermark["output_hash"],
        "cost": cost,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # TODO: Save to database (Day 3)
    
    return audit_record