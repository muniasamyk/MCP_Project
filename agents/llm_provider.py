import os
import json
import requests
from utils.logger import get_logger

logger = get_logger(__name__)


class LLMProvider:
    """Small wrapper around multiple LLM backends."""
    
    def __init__(self, provider="ollama", model="mistral"):
        self.provider = provider
        self.model = model
        self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
        self.ollama_timeout_seconds = int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "180"))
        self.openai_key = os.getenv("OPENAI_API_KEY")
    
    def call_mock(self, prompt):
        """
        Mock LLM response for testing / demos.

        This makes the project runnable even if you don't have Ollama/OpenAI.
        It returns valid JSON for the Planner, and a short explanation for the Reasoner.
        """
        logger.info(f"Calling Mock Provider (simulating {self.model})...")
        
        prompt_lower = prompt.lower()
        
        # 1) Reasoner prompt starts with "User asked:" -> return a short explanation
        if prompt.startswith("User asked:"):
            # Extract the "Database returned:" part to show the user the actual data
            # This makes the mock "reasoner" actually useful because it repeats the findings
            try:
                # The prompt has format:
                # User asked: "..."
                # Database returned:
                # [...]
                # Provide a clear...
                
                start_marker = "Database returned:\n"
                end_marker = "\n\nProvide a clear"
                
                start_idx = prompt.find(start_marker)
                end_idx = prompt.find(end_marker)
                
                if start_idx != -1 and end_idx != -1:
                    data_str = prompt[start_idx + len(start_marker) : end_idx].strip()
                    return (
                        f"Here is the data found in the database:\n{data_str}\n\n"
                        "(Data retrieved via MCP tools layer)"
                    )
            except:
                pass

            return (
                "Here is the data you requested. "
                "It was retrieved securely via the MCP tools layer (no direct DB access by the LLM)."
            )

        # 2) Planner prompt -> return a JSON plan (tool + parameters)
        
        # Extract just the query part to avoid matching words in the tool descriptions
        # Planner prompt has: Query: "{user_query}"
        query_text = prompt_lower
        if "query:" in prompt_lower:
            parts = prompt_lower.split("query:")
            if len(parts) > 1:
                query_text = parts[1].split("\n")[0].strip('" ')
        
        response_data = {}
        
        if "department" in query_text and "ai" in query_text:
            response_data = {
                "tool": "get_employees_by_department",
                "parameters": {"department": "AI"},
                "reasoning": "User asked for employees in AI department."
            }
        elif "project" in query_text:
            if "progress" in query_text:
                response_data = {
                    "tool": "get_projects_by_status",
                    "parameters": {"status": "In Progress"},
                    "reasoning": "User asked for projects in progress."
                }
            elif "completed" in query_text:
                response_data = {
                    "tool": "get_projects_by_status",
                    "parameters": {"status": "Completed"},
                    "reasoning": "User asked for completed projects."
                }
        elif "issue" in query_text:
            if "high" in query_text:
                response_data = {
                    "tool": "get_issues_by_priority",
                    "parameters": {"priority": "High"},
                    "reasoning": "User asked for high priority issues."
                }
            elif "critical" in query_text:
                response_data = {
                    "tool": "get_issues_by_priority",
                    "parameters": {"priority": "Critical"},
                    "reasoning": "User asked for critical priority issues."
                }
        
        if response_data:
            return json.dumps(response_data)
        
        # Default mock response
        logger.warning(f"Mock provider got unknown prompt: {prompt}")
        return json.dumps({"error": "I could not understand the query in mock mode."})

    def call_ollama(self, prompt):
        """Call a local Ollama model."""
        try:
            logger.info(f"Calling Ollama ({self.model})...")
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.7
                },
                timeout=self.ollama_timeout_seconds
            )
            response.raise_for_status()
            result = response.json()["response"]
            logger.info("Ollama response received")
            return result
        except requests.exceptions.ConnectionError:
            logger.error("Cannot connect to Ollama. Make sure to run: ollama serve")
            raise Exception("Ollama server not running on http://localhost:11434")
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            raise
    
    def call_openai(self, messages):
        """Call OpenAI Chat Completions API."""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_key)
            logger.info(f"Calling OpenAI ({self.model})...")
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7
            )
            logger.info("✅ OpenAI response received")
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"❌ OpenAI error: {e}")
            raise
    
    def generate(self, prompt):
        """Main entrypoint used by all agents: returns model output text."""
        if self.provider == "mock":
            return self.call_mock(prompt)
        if self.provider == "ollama":
            return self.call_ollama(prompt)
        messages = [{"role": "user", "content": prompt}]
        return self.call_openai(messages)

