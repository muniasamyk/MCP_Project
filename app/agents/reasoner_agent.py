import json
from app.agents.llm_provider import LLMProvider
from app.utils.logger import get_logger

logger = get_logger(__name__)

class ReasonerAgent:
    """
    Takes raw data and explains it in natural language.
    """
    
    def __init__(self, llm: LLMProvider):
        self.llm = llm

    def explain(self, query: str, data):
        logger.info("Generating explanation...")
        
        # If data is empty, just say so
        if not data:
            return "I couldn't find any data matching your request."

        # Convert data to string for the prompt
        data_str = json.dumps(data, indent=2, default=str)
        
        prompt = (
            f"User Question: \"{query}\"\n\n"
            f"Database Result:\n{data_str}\n\n"
            f"Please summarize this data for the user. Highlight key insights.\n"
            f"Keep it concise (3-4 sentences)."
        )

        try:
            return self.llm.generate(prompt)
        except Exception as e:
            logger.error(f"Reasoning failed: {e}")
            return "Here is the raw data: " + str(data)
