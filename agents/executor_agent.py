"""
Executor Agent (Safe Tool Runner)

Purpose
-------
Execute the Planner's JSON plan in a safe way.

What it does
------------
- Checks the requested tool exists in an allowlist (sandbox)
- Extracts the parameter value (example: "AI")
- Calls the corresponding tool function
- Returns rows (data) + row_count

What it will NOT do (safety)
----------------------------
- It will not run arbitrary SQL.
- It will not call tools outside the allowlist.
"""

from mcp.tools import TOOLS
from utils.logger import get_logger

logger = get_logger(__name__)

class ExecutorAgent:
    """Validates and executes a tool call plan."""
    
    def __init__(self):
        # Single source of truth for allowed tool calls
        self.tools = TOOLS
    
    def execute(self, plan):
        """
        Execute a plan produced by the PlannerAgent.

        Expected input:
          {"tool": "<tool_name>", "parameters": {"some_key": "some_value"}}
        """
        logger.info(f"Executing plan: {plan}")
        
        # Safety check 1: plan must include a tool name.
        if not plan or "tool" not in plan:
            logger.error("Plan is invalid - missing tool")
            return {"error": "Invalid plan - tool missing"}
        
        tool_name = plan.get("tool")
        parameters = plan.get("parameters", {})
        
        logger.info(f"Tool: {tool_name}, Parameters: {parameters}")
        
        # Safety check 2: tool must be in the allowlist.
        if tool_name not in self.tools:
            logger.error(f"Tool not found: {tool_name}")
            return {"error": f"Tool '{tool_name}' not allowed"}
        
        # Execute the tool
        try:
            logger.info(f"Calling tool: {tool_name}")
            '''TOOLS = {
            "get_employees_by_department": mcp_get_employees_by_department,
            "get_projects_by_status": mcp_get_projects_by_status,
            "get_issues_by_priority": mcp_get_issues_by_priority,
            }'''
            tool_func = self.tools[tool_name]
            
            # Extract parameter value (could be department, status, or priority)
            if isinstance(parameters, dict):
                param_value = list(parameters.values())[0] if parameters else None
            elif isinstance(parameters, list):
                param_value = parameters[0] if parameters else None
            else:
                 param_value = str(parameters)
            
            if param_value is None:
                logger.error("No parameter value provided")
                return {"error": "No parameter value in plan"}
            
            result = tool_func(param_value)
            
            # Check if result is valid
            if isinstance(result, list):
                logger.info(f"Tool executed successfully, got {len(result)} rows")
                
                return {
                    "status": "success",
                    "tool": tool_name,
                    "parameters": parameters,
                    "row_count": len(result),
                    "data": result
                }
            else:
                logger.error(f"Tool returned unexpected type: {type(result)}")
                return {
                    "status": "success",
                    "tool": tool_name,
                    "parameters": parameters,
                    "row_count": 1,
                    "data": [result]
                }
        
        except Exception as e:
            logger.error(f"Error executing tool: {str(e)}")
            return {
                "error": f"Error: {str(e)}"
            }

# Expose as a callable for the notebook
_executor_instance = ExecutorAgent()
executor_agent = _executor_instance.execute
