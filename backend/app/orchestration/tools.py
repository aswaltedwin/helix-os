from typing import Callable, Dict, Any

class ToolRegistry:
    """Registry of tools available to agents"""
    
    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {
            "read_erp": {
                "description": "Read financial data from ERP system",
                "input_schema": {"module": str, "filters": dict}
            },
            "write_erp": {
                "description": "Write data to ERP system (requires approval for amounts > $1000)",
                "input_schema": {"module": str, "data": dict, "amount": float}
            },
            "read_crm": {
                "description": "Read customer data from CRM",
                "input_schema": {"entity_type": str, "id": str}
            },
            "write_crm": {
                "description": "Update CRM records",
                "input_schema": {"entity_type": str, "id": str, "data": dict}
            },
            "send_email": {
                "description": "Send email to recipient",
                "input_schema": {"to": str, "subject": str, "body": str}
            },
            "read_hrms": {
                "description": "Read HR data (employee info, leave balance, etc.)",
                "input_schema": {"module": str, "id": str}
            },
            "write_hrms": {
                "description": "Update HRMS records",
                "input_schema": {"module": str, "data": dict}
            },
            "escalate_to_human": {
                "description": "Escalate decision to human for approval",
                "input_schema": {"reason": str, "context": dict}
            }
        }
    
    def get_tool(self, name: str) -> Dict[str, Any]:
        """Get tool definition"""
        return self.tools.get(name, None)
    
    def list_tools(self) -> Dict[str, Dict[str, Any]]:
        """List all available tools"""
        return self.tools

tool_registry = ToolRegistry()