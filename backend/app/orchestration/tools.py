import os
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

REPORTS_DIR = os.path.join(os.getcwd(), "agent_reports")

def ensure_reports_dir():
    if not os.path.exists(REPORTS_DIR):
        os.makedirs(REPORTS_DIR)
        logger.info(f"Created reports directory at {REPORTS_DIR}")

def save_report(category: str, task_id: str, content: str) -> str:
    """Saves a specialist report to a real file on disk."""
    ensure_reports_dir()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{category}_{task_id}_{timestamp}.md"
    filepath = os.path.join(REPORTS_DIR, filename)
    
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# HelixOS {category.upper()} Report\n")
            f.write(f"**Task ID:** {task_id}\n")
            f.write(f"**Timestamp:** {datetime.now().isoformat()}\n\n")
            f.write(content)
        
        logger.info(f"Report saved to {filepath}")
        return f"Successfully saved report to {filename}"
    except Exception as e:
        logger.error(f"Failed to save report: {e}")
        return f"Error saving report: {str(e)}"

def calculate_financials(expression: str) -> str:
    """Performs real-world math for financial tasks."""
    try:
        # Note: In production, use a safer math parser or restricted eval
        # For this prototype, we'll use a basic safe eval approach
        allowed_chars = "0123456789+-*/(). "
        if all(c in allowed_chars for c in expression):
            result = eval(expression)
            return f"Calculation result for '{expression}': {result}"
        else:
            return "Invalid characters in math expression."
    except Exception as e:
        return f"Calculation error: {str(e)}"

def run_agent_tool(tool_name: str, params: dict) -> str:
    """Dispatcher for agent tools."""
    if tool_name == "save_report":
        return save_report(
            params.get("category", "general"),
            params.get("task_id", "unknown"),
            params.get("content", "")
        )
    elif tool_name == "calculate_financials":
        return calculate_financials(params.get("expression", ""))
    else:
        return f"Tool '{tool_name}' not found."