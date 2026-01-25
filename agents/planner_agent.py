"""
Planner Agent (Natural Language -> Tool Plan)

Purpose
-------
Convert a user's English question into a small JSON "plan" that the system can
execute safely.

Example
-------
User says:
  "Fetch employee details where department is AI"

Planner returns:
  {
    "tool": "get_employees_by_department",
    "parameters": {"department": "AI"},
    "reasoning": "..."
  }

Important safety note
---------------------
This agent does NOT touch the database.
It ONLY decides which *pre-approved tool* to call and with what parameter.
"""

import json
import re
from agents.llm_provider import LLMProvider
from utils.logger import get_logger

logger = get_logger(__name__)

class PlannerAgent:
    """Uses an LLM to select the best tool + parameter(s)."""
    
    def __init__(self, llm_provider="ollama", model="mistral"):
        self.llm = LLMProvider(provider=llm_provider, model=model)
        self.available_tools = self._get_tool_definitions()
    
    def _get_tool_definitions(self):
        """
        Define the "menu" of tools the LLM is allowed to choose from.

        The LLM sees these descriptions, then must output EXACT tool names.
        """
        return {
            "get_employees_by_department": {
                "description": "Fetch employees from a specific department (e.g., AI, Backend, Frontend, DevOps, Data Science)",
                "parameters": ["department"]
            },
            "get_projects_by_status": {
                "description": "Fetch projects with a specific status (e.g., Completed, In Progress, On Hold)",
                "parameters": ["status"]
            },
            "get_issues_by_priority": {
                "description": "Fetch issues with a specific priority level (e.g., High, Medium, Low)",
                "parameters": ["priority"]
            }
        }
    
    def plan(self, user_query):
        """
        Create a plan for the user's query.

        Output format:
          - tool: one of the allowed tools (string)
          - parameters: dict of required values (example: {"department": "AI"})
          - reasoning: short text (optional; for debugging / transparency)
        """
        logger.info(f"Planner analyzing: {user_query}")
        
        # Build a prompt that forces the model to output JSON.
        tools_desc = json.dumps(self.available_tools, indent=2)
        
        prompt = f"""You are a query planner.
Available tools:
{tools_desc}

Query: "{user_query}"

Task: Select the tool that best matches the query. Extract the parameter.

Respond only with this JSON format:
{{
  "tool": "EXACT_TOOL_NAME",
  "parameters": {{ "param": "value" }},
  "reasoning": "reason"
}}
"""  
        try:
            response = self.llm.generate(prompt)
            logger.info(f"LLM Response: {response[:200]}...")
            
            # Extract JSON using regex
            match = re.search(r'\{.*\}', response, re.DOTALL)
            if not match:
                logger.warning(f"No JSON found in response. Attempting fallback strategy.")
                # Fallback: simple keyword matching (makes demo reliable even if LLM output is messy)
                plan = {}
                q_lower = user_query.lower()
                
                if "department" in q_lower:
                    plan["tool"] = "get_employees_by_department"
                    # Extract department from common values (AI/Backend/etc.)
                    for dept in ["ai", "backend", "frontend", "devops", "data science"]:
                        if dept in q_lower:
                            plan["parameters"] = {"department": dept.upper() if dept == "ai" else dept.capitalize()}
                            break
                    if "parameters" not in plan:
                        plan["parameters"] = {"department": "AI"}  # default
                    
                elif "project" in q_lower:
                    plan["tool"] = "get_projects_by_status"
                    for status in ["completed", "in progress", "on hold"]:
                        if status in q_lower:
                            plan["parameters"] = {"status": status.title()}
                            break
                    if "parameters" not in plan:
                        plan["parameters"] = {"status": "In Progress"}  # default
                    
                elif "issue" in q_lower or "priority" in q_lower:
                    plan["tool"] = "get_issues_by_priority"
                    for prio in ["critical", "high", "medium", "low"]:
                        if prio in q_lower:
                            plan["parameters"] = {"priority": prio.capitalize()}
                            break
                    if "parameters" not in plan:
                        plan["parameters"] = {"priority": "High"}  # default
                
                if not plan:
                     return {"error": "Could not understand query"}
                
                plan["reasoning"] = "Fallback strategy used due to LLM parsing failure"
                logger.info(f"✅ Fallback Plan: {plan}")
                return plan
            
            json_str = match.group(0)
            plan = json.loads(json_str)
            
            # Validate tool name
            if plan.get("tool") not in self.available_tools:
                # If the model returns an invalid tool name, we correct it using keywords.
                if "department" in user_query.lower():
                    plan["tool"] = "get_employees_by_department"
                elif "project" in user_query.lower():
                    plan["tool"] = "get_projects_by_status"
                elif "issue" in user_query.lower():
                    plan["tool"] = "get_issues_by_priority"
            
            logger.info(f"✅ Plan: {plan}")
            return plan
        except Exception as e:
            logger.error(f"Planning failed: {e}")
            return {"error": str(e)}

# Expose as a callable for the notebook
_planner_instance = PlannerAgent()
planner_agent = _planner_instance.plan
