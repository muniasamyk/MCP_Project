from fastapi import APIRouter, HTTPException, Depends, Header
from app.api.models import QueryRequest, QueryResponse
from app.agents.orchestrator import AgentOrchestrator
from app.core.config import settings
from app.utils.logger import get_logger
from typing import Optional

router = APIRouter()
logger = get_logger(__name__)

# Keep a single instance of the orchestrator
_agent_orchestrator = None

def get_orchestrator():
    global _agent_orchestrator
    if not _agent_orchestrator:
        logger.info("Initializing Agent Orchestrator...")
        _agent_orchestrator = AgentOrchestrator()
    return _agent_orchestrator

# Simple API Key check
async def check_api_key(x_api_key: Optional[str] = Header(None)):
    if settings.API_KEY and x_api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

@router.post("/query", response_model=QueryResponse)
async def run_query(
    req: QueryRequest,
    agent: AgentOrchestrator = Depends(get_orchestrator),
    _ = Depends(check_api_key) # Enforce auth if enabled
):
    """
    Main entry point: User asks a question -> Agent answers.
    """
    logger.info(f"Received query: {req.query}")

    try:
        # Pass the query to our agent pipeline
        result = agent.process_query(req.query)
        return result
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Simple health check that also pings the DB."""
    status = {"api": "online", "db": "unknown"}
    
    try:
        from app.database.db_executor import get_db_connection
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                status["db"] = "connected"
    except Exception as e:
        status["db"] = f"unreachable: {e}"
        
    return status
