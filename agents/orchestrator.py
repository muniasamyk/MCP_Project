from agents.planner_agent import PlannerAgent
from agents.executor_agent import ExecutorAgent
from agents.reasoner_agent import ReasonerAgent
from utils.logger import get_logger

logger = get_logger(__name__)

class AgentOrchestrator:
    """High-level controller for Plan -> Execute -> Explain."""
    
    def __init__(self, llm_provider="mock", model="mistral"):
        logger.info(f"Initializing Orchestrator with {llm_provider} ({model})")
        self.planner = PlannerAgent(llm_provider=llm_provider, model=model)
        self.executor = ExecutorAgent()
        self.reasoner = ReasonerAgent(llm_provider=llm_provider, model=model)
    
    def process_query(self, user_query):
        """
        Run a single query through the full workflow.

        Step 1 (Planner): choose the tool + extract parameter(s)
        Step 2 (Executor): validate tool is allowed and execute it
        Step 3 (Reasoner): summarize DB rows into a user-friendly answer
        """
  
        logger.info(f"Processing Query: {user_query}")
    
        
        try:
            # Step 1: Plan
            logger.info(f"[1/3] Planning...")
            plan = self.planner.plan(user_query)
            if plan.get("error"):
                logger.error(f"Planning error: {plan['error']}")
                return {
                    "query": user_query,
                    "status": "error",
                    "error": plan["error"]
                }
            
            # Step 2: Execute
            logger.info(f"  [2/3] Executing...")
            result = self.executor.execute(plan)
            if result.get("error"):
                logger.error(f"Execution error: {result['error']}")
                return {
                    "query": user_query,
                    "plan": plan,
                    "status": "error",
                    "error": result["error"]
                }
            
            # Step 3: Reason
            logger.info(f"[3/3] 🤔 Reasoning...")
            explanation = self.reasoner.reason(user_query, result.get("data", result))
            
    
            logger.info(f"✅ Query Processing Complete")
    
            
            return {
                "query": user_query,
                "status": "success",
                "plan": plan,
                "data": result.get("data", result),
                "row_count": result.get("row_count", 0),
                "explanation": explanation
            }
        
        except Exception as e:
            logger.error(f"❌ Orchestrator error: {e}")
            return {
                "query": user_query,
                "status": "error",
                "error": str(e)
            }
"""
Orchestrator Agent (Workflow Controller)

Purpose
-------
This file coordinates the full end-to-end pipeline for ONE user question:

  1) PlannerAgent  -> converts the user's English question into a small JSON "plan"
  2) ExecutorAgent -> safely executes ONLY allowed tools (no arbitrary SQL)
  3) ReasonerAgent -> converts raw database rows into a short explanation

Inputs / Outputs
----------------
Input:  user_query (str)
Output: dict with:
  - status: "success" | "error"
  - plan: the chosen tool + parameters
  - data: raw rows returned from the DB tool
  - explanation: friendly summary for the end user
"""