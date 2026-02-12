from app.mcp.tools import TOOLS
from app.utils.logger import get_logger

logger = get_logger(__name__)

class ExecutorAgent:
    """
    Executes the tool selected by the Planner.
    Safety: Only runs tools defined in the TOOLS whitelist.
    """
    
    def __init__(self):
        self.tools = TOOLS # Whitelist

    def execute(self, plan: dict):
        tool_name = plan.get("tool")
        if not tool_name:
            return {"error": "No tool selected"}

        logger.info(f"Executing tool: {tool_name}")
        
        if tool_name not in self.tools:
            return {"error": f"Tool '{tool_name}' is not allowed"}

        try:
            func = self.tools[tool_name]
            params = plan.get("parameters", {})
            
            # Simple parameter extraction
            # We assume the tool takes exactly one argument for this POC
            if isinstance(params, dict) and params:
                arg_val = list(params.values())[0]
            elif isinstance(params, list) and params:
                arg_val = params[0]
            elif isinstance(params, str):
                arg_val = params
            else:
                return {"error": "Missing parameters"}

            # Run the tool
            result = func(arg_val)
            
            return {
                "status": "success",
                "tool": tool_name,
                "data": result
            }

        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            return {"error": f"Execution error: {str(e)}"}
