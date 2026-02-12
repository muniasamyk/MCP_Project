import json
import requests
import re
from app.utils.logger import get_logger
from app.core.config import settings

logger = get_logger(__name__)

class LLMProvider:
    """
    Unified interface for different LLM backends (Mock, Ollama, OpenAI).
    """
    
    def __init__(self, provider=None, model=None):
        self.provider = provider or settings.MCP_LLM_PROVIDER
        self.model = model or settings.MCP_LLM_MODEL
        
        # Configs
        self.ollama_url = settings.OLLAMA_URL
        self.ollama_timeout = settings.OLLAMA_TIMEOUT_SECONDS
        self.openai_key = settings.OPENAI_API_KEY
    
    def generate(self, prompt: str) -> str:
        """Dispatch query to the configured provider."""
        if self.provider == "mock":
            return self._mock_response(prompt)
        elif self.provider == "ollama":
            return self._call_ollama(prompt)
        elif self.provider == "openai":
            return self._call_openai(prompt)
        else:
            raise ValueError(f"Unknown LLM provider: {self.provider}")

    def _mock_response(self, prompt: str) -> str:
        """
        Simulates an LLM for testing without running a real model.
        """
        logger.info(f"Mock LLM: Processing prompt...")
        prompt_lower = prompt.lower()
        
        # --- 1. MOCK REASONER ---
        # Detect if this is a reasoning task (summarizing data)
        # Fix: Detect "Database Result" or "summarize this data"
        if "database result:" in prompt_lower or "summarize this data" in prompt_lower:
            # Count the records by looking for 'id' or 'name' fields in the JSON data
            count = len(re.findall(r'"id":|"name":', prompt_lower))
            # Avoid double-counting if both 'id' and 'name' exist per record
            id_count = len(re.findall(r'"id":', prompt_lower))
            name_count = len(re.findall(r'"name":', prompt_lower))
            count = max(id_count, name_count)
            
            if count == 0 and ("[]" in prompt or "empty" in prompt_lower or "null" in prompt_lower):
                return "No records found matching your query."
            
            # Make the response sound natural based on context
            entity = "records"
            if "employee" in prompt_lower: entity = "employees"
            elif "project" in prompt_lower: entity = "projects"
            elif "issue" in prompt_lower: entity = "issues"
            
            # If generated SQL was used, the result is raw data
            return f"Found {count} {entity} matching your criteria. (Mocked SQL Result)"

        # --- 2. MOCK PLANNER ---
        # Only look for keywords in the "User Query" part
        user_query_part = ""
        if "user query:" in prompt_lower:
            user_query_part = prompt_lower.split("user query:")[-1]
        else:
            user_query_part = prompt_lower 

        response = {}
        
        # --- NEW: Handle Text-to-SQL Scenarios ---
        if "salary" in user_query_part:
            # Extract the actual number from the query (e.g. "more than 900000")
            salary_match = re.search(r'(\d[\d,]+)', user_query_part)
            salary_threshold = salary_match.group(1).replace(',', '') if salary_match else "90000"
            response = {
                "tool": "run_sql_query", 
                "parameters": {
                    "query": f"SELECT name, department, salary FROM employees WHERE salary > {salary_threshold} ORDER BY salary DESC"
                }
            }
        
        elif "budget" in user_query_part:
            # Generate a SQL query for projects budget
            response = {
                "tool": "run_sql_query", 
                "parameters": {
                    "query": "SELECT name, status, budget FROM projects WHERE budget > 200000 ORDER BY budget DESC"
                }
            }

        # --- Standard Tools ---
        elif "department" in user_query_part or "employees" in user_query_part:
            dept = "AI" 
            if "backend" in user_query_part: dept = "Backend"
            if "frontend" in user_query_part: dept = "Frontend"
            if "devops" in user_query_part: dept = "DevOps"
            response = {"tool": "get_employees_by_department", "parameters": {"department": dept}}
        
        elif "project" in user_query_part:
            status = "In Progress"
            if "completed" in user_query_part: status = "Completed"
            if "planning" in user_query_part: status = "Planning"
            response = {"tool": "get_projects_by_status", "parameters": {"status": status}}

        elif "issue" in user_query_part:
            priority = "High"
            if "critical" in user_query_part: priority = "Critical"
            if "medium" in user_query_part: priority = "Medium"
            if "low" in user_query_part: priority = "Low"
            response = {"tool": "get_issues_by_priority", "parameters": {"priority": priority}}
        
        if response:
            return json.dumps(response)
        
        logger.warning(f"Mock LLM couldn't match prompt: {prompt[:50]}...")
        return json.dumps({"error": "Mock LLM didn't understand query"})

    def _call_ollama(self, prompt: str) -> str:
        try:
            logger.info(f"Ollama ({self.model}): Generating...")
            res = requests.post(
                self.ollama_url,
                json={
                    "model": self.model, 
                    "prompt": prompt, 
                    "stream": False, 
                    "temperature": 0.1 
                },
                timeout=self.ollama_timeout
            )
            res.raise_for_status()
            return res.json().get("response", "")
        except Exception as e:
            logger.error(f"Ollama failed: {e}")
            raise

    def _call_openai(self, prompt: str) -> str:
        if not self.openai_key:
            raise ValueError("OpenAI API Key is missing in settings")
            
        try:
            from openai import OpenAI
            # Set a short timeout (5s) so we fail fast and use fallback logic if the API is slow/broken
            client = OpenAI(api_key=self.openai_key, timeout=5.0)
            
            logger.info(f"OpenAI ({self.model}): Generating...")
            res = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            return res.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI failed: {e}")
            raise
