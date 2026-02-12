import json
import re
from app.agents.llm_provider import LLMProvider
from app.utils.logger import get_logger

logger = get_logger(__name__)

class PlannerAgent:
    """
    Analyzes the user's query and selects the right tool.
    Output: JSON with 'tool' and 'parameters'.
    """
    
    def __init__(self, llm: LLMProvider):
        self.llm = llm
        
        # Definition of tools available to the LLM
        self.tools_schema = {
            "get_employees_by_department": {
                "desc": "Find employees in a dept (AI, Backend, Frontend, DevOps)",
                "args": ["department"]
            },
            "get_projects_by_status": {
                "desc": "Find projects by status (Completed, In Progress, Planning)",
                "args": ["status"]
            },
            "get_issues_by_priority": {
                "desc": "Find issues by priority (Critical, High, Medium, Low)",
                "args": ["priority"]
            },
            "run_sql_query": {
                "desc": "Execute a raw SQL SELECT query for complex data retrieval. Use this when no other tool fits.",
                "args": ["query"]
            }
        }
        
        # Simple DB Schema for the LLM to know what to query
        self.db_schema = """
        Database Schema:
        - employees(id, name, email, department, salary, hire_date, is_active)
        - projects(id, name, description, status, start_date, end_date, budget, lead_id)
        - issues(id, title, description, priority, status, assigned_to, project_id, created_date, due_date)
        """
    
    def plan(self, query: str):
        logger.info(f"Planning for query: '{query}'")
        
        prompt = self._build_prompt(query)
        
        try:
            raw_response = self.llm.generate(prompt)
            plan = self._parse_response(raw_response)
            
            # Basic validation
            if plan.get("tool") not in self.tools_schema:
                logger.warning(f"LLM hallucinated tool: {plan.get('tool')}")
                return self._fallback_logic(query)
                
            logger.info(f"Selected tool: {plan['tool']} with params: {plan.get('parameters')}")
            return plan

        except Exception as e:
            logger.error(f"Planning failed: {e}")
            return self._fallback_logic(query)

    def _build_prompt(self, query):
        schema_str = json.dumps(self.tools_schema, indent=2)
        return (
            f"You are a smart routing agent. Your goal is to pick the best tool to answer the user's question.\n"
            f"If the question is simple, use a specific tool (e.g. get_employees_by_department).\n"
            f"If the question is complex or about fields like 'salary' or 'budget' that are not covered by specific tools, use 'run_sql_query' and generate a valid SQL SELECT statement.\n\n"
            f"Available Tools:\n{schema_str}\n\n"
            f"{self.db_schema}\n\n"
            f"User Query: \"{query}\"\n\n"
            f"Constraints:\n"
            f"- For 'run_sql_query', the 'query' parameter MUST be a valid SQL SELECT Statement.\n"
            f"- Do NOT use DROP, DELETE, or INSERT.\n\n"
            f"Return purely JSON in this format:\n"
            f'{{"tool": "TOOL_NAME", "parameters": {{"ARG_NAME": "VALUE"}}, "reasoning": "..."}}'
        )

    def _parse_response(self, text):
        # Extract JSON substring if the LLM is chatty
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            text = match.group(0)
        return json.loads(text)

    def _fallback_logic(self, query):
        """Simple keyword matching if LLM fails."""
        q = query.lower()
        plan = {}
        
        # Heuristics
        if "salary" in q or "budget" in q:
            # Fallback for complex queries -> try to generate SQL if possible, or just fail safely
            # Since this is a simple fallback, we might not want to guess SQL.
            # But we can try a simple one.
            if "salary" in q:
                 # Try to extract a number for salary threshold
                 import re
                 match = re.search(r'(\d[\d,]+)', q)
                 if match:
                     amount = match.group(1).replace(',', '')
                     sql = f"SELECT * FROM employees WHERE salary > {amount} ORDER BY salary DESC"
                 else:
                     sql = "SELECT * FROM employees ORDER BY salary DESC"
                 plan = {"tool": "run_sql_query", "parameters": {"query": sql}}
            elif "budget" in q:
                 plan = {"tool": "run_sql_query", "parameters": {"query": "SELECT * FROM projects ORDER BY budget DESC"}}
        
        elif "department" in q or "employees" in q:
            plan = {"tool": "get_employees_by_department", "parameters": {"department": "AI"}}
            for d in ["backend", "frontend", "devops"]:
                if d in q: plan["parameters"]["department"] = d.capitalize()
                
        elif "project" in q:
            plan = {"tool": "get_projects_by_status", "parameters": {"status": "In Progress"}}
            
        elif "issue" in q:
            plan = {"tool": "get_issues_by_priority", "parameters": {"priority": "High"}}
            
        if not plan:
            return {"error": "Sorry, I couldn't figure out which tool to use."}
            
        plan["reasoning"] = "Fallback heuristic used."
        return plan
