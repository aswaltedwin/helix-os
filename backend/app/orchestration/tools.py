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

def verify_purchase_order(invoice_id: str, amount: float) -> str:
    """Verifies that an invoice matches a (simulated) Purchase Order."""
    # Simulation: POs only exist for amounts < $5,000
    if amount < 5000:
        return f"PO Match Confirmed: PO-#{invoice_id[:5]} matches amount ${amount}."
    else:
        return f"PO Variance Detected: No pre-approved PO found for ${amount}. Manual review required."

def detect_fraud_patterns(expression: str) -> str:
    """Heuristic-based fraud detection."""
    # Simulation: Large amounts or suspicious strings
    if "$" in expression and "10000" in expression:
        return "FRAUD ALERT: High-risk transaction amount detected (> $10k). Circuit breaker engaged."
    if "anonymous" in expression.lower():
        return "FRAUD ALERT: Suspicious vendor metadata detected ('anonymous')."
    return "Fraud Scan: No immediate high-risk patterns detected."

def fetch_financial_policies(policy_type: str) -> str:
    """Retrieves corporate financial policies."""
    policies = {
        "approval": "Level 1: <$500 Auto | Level 2: $500-$5k Manager | Level 3: >$5k CFO",
        "vendors": "Only pre-vetted vendors. New vendors require 48hr onboarding.",
        "compliance": "SOC2 Type II compliance required for all external data processors."
    }
    return policies.get(policy_type, "Policy not found.")

def check_leave_policy(employee_id: str) -> str:
    """Verifies employee leave balance against company policy."""
    # Simulation: Employee IDs starting with 'EMP-8' have issues
    if employee_id.startswith("EMP-8"):
        return f"Policy Alert: Employee {employee_id} has exceeded the 15-day annual leave limit. Request flagged for HR review."
    return f"Policy Match: Employee {employee_id} has 8 days of leave remaining. Within threshold."

def verify_team_coverage(date_str: str) -> str:
    """Checks for calendar conflicts on a given date."""
    # Simulation: Fridays are always tight
    if "friday" in date_str.lower():
        return f"Coverage Warning: 30% of the team is out on {date_str}. New leave requests may be denied."
    return f"Coverage OK: Sufficient team members available on {date_str}."

def generate_offer_letter(name: str, position: str, salary: float, task_id: str) -> str:
    """Generates a formal offer letter and saves it to a file."""
    content = f"""
## OFFICIAL OFFER OF EMPLOYMENT
**Candidate:** {name}
**Position:** {position}
**Annual Salary:** ${salary:,.2f}
**Benefits:** Full Health, 401k Match, HelixOS Equity
**Start Date:** TBD

Congratulations {name}! We are excited to have you join the team.
"""
    # Use existing save_report to persist it
    report_res = save_report("hr_offer", task_id, content)
    return f"Offer Letter Generated for {name}. {report_res}"

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
    elif tool_name == "verify_purchase_order":
        return verify_purchase_order(params.get("invoice_id", ""), float(params.get("amount", 0)))
    elif tool_name == "detect_fraud_patterns":
        return detect_fraud_patterns(params.get("expression", "") or str(params.get("data", "")))
    elif tool_name == "fetch_policies":
        return fetch_financial_policies(params.get("type", "approval"))
    elif tool_name == "check_leave_policy":
        return check_leave_policy(params.get("employee_id", "unknown"))
    elif tool_name == "verify_team_coverage":
        return verify_team_coverage(params.get("date", "unknown"))
    elif tool_name == "generate_offer_letter":
        return generate_offer_letter(
            params.get("name", "Candidate"),
            params.get("position", "Specialist"),
            float(params.get("salary", 0.0)),
            params.get("task_id", "unknown")
        )
    else:
        return f"Tool '{tool_name}' not found."