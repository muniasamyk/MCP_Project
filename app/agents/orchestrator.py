from app.agents.planner_agent import PlannerAgent
from app.agents.executor_agent import ExecutorAgent
from app.agents.reasoner_agent import ReasonerAgent
from app.agents.llm_provider import LLMProvider
from app.utils.logger import get_logger
from app.core.config import settings

logger = get_logger(__name__)

class AgentOrchestrator:
    """
    Main controller:
    1. Plan (LLM decides tool)
    2. Execute (Tool runs SQL)
    3. Reason (LLM explains output)
    """
    
    def __init__(self):
        # Initialize the shared LLM provider
        self.llm = LLMProvider()
        
        # Initialize agents
        self.planner = PlannerAgent(self.llm)
        self.executor = ExecutorAgent()
        self.reasoner = ReasonerAgent(self.llm)
        
        logger.info(f"Orchestrator ready (Provider: {self.llm.provider})")

    def process_query(self, user_query: str):
        # 1. PLANNING
        plan = self.planner.plan(user_query)
        if "error" in plan:
            return self._error_response(user_query, plan["error"])

        # 2. EXECUTION
        exec_result = self.executor.execute(plan)
        if "error" in exec_result:
             return self._error_response(user_query, exec_result["error"])

        # 3. REASONING
        # We pass the raw data to the reasoner to get a human-friendly summary
        raw_data = exec_result.get("data", [])
        explanation = self.reasoner.explain(user_query, raw_data)

        return {
            "query": user_query,
            "status": "success",
            "plan": plan,
            "data": raw_data,
            "row_count": len(raw_data) if isinstance(raw_data, list) else 1,
            "explanation": explanation
        }

    def _error_response(self, query, error_msg):
        logger.error(f"Request failed: {error_msg}")
        return {
            "query": query,
            "status": "error",
            "error": error_msg
        }
