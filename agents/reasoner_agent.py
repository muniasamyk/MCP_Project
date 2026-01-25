"""
Reasoner Agent (Rows -> Friendly Explanation)

Purpose
-------
Take the raw database rows returned by the Executor/Tools layer and generate a
short, human-friendly explanation.

Important note
--------------
This agent does NOT query the database. It only summarizes what the database
already returned.

Example
-------
Input:  user_query="Fetch employees in AI"
        execution_result=[(1, "Alice", ...), (2, "Bob", ...)]
Output: "I found 2 employees in the AI department: Alice and Bob..."
"""

import json
from agents.llm_provider import LLMProvider
from utils.logger import get_logger
from utils.serializer import json_dumps

logger = get_logger(__name__)

class ReasonerAgent:
    """Summarizes raw results into a short explanation."""
    
    def __init__(self, llm_provider="ollama", model="mistral"):
        self.llm = LLMProvider(provider=llm_provider, model=model)
    
    def reason(self, user_query, execution_result):
        """
        Use the LLM to produce a short explanation (3-4 sentences) based on:
        - the original user query
        - the raw data returned from the database
        """
        logger.info(f"Reasoning about results...")
        
        # Convert result to string if it's a dict/list
        if isinstance(execution_result, (dict, list)):
            result_str = json_dumps(execution_result, indent=2)
        else:
            result_str = str(execution_result)
        
        prompt = f"""User asked: "{user_query}"

Database returned:
{result_str}

Provide a clear, concise explanation of:
1. What data was retrieved
2. Key insights or patterns
3. Any recommendations

Be conversational and helpful. Keep response to 3-4 sentences."""
        
        try:
            explanation = self.llm.generate(prompt)
            logger.info(f"Reasoning complete")
            return explanation
        except Exception as e:
            logger.error(f"Reasoning failed: {e}")
            return f"Database returned {len(execution_result)} records" if isinstance(execution_result, list) else str(execution_result)

