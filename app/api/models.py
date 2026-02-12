from pydantic import BaseModel, Field
from typing import Optional, Any, Dict, List

class QueryRequest(BaseModel):
    # Enforce some basic limits to prevent abuse
    query: str = Field(..., min_length=2, max_length=1000, description="The user's natural language question")

class QueryResponse(BaseModel):
    query: str
    status: str
    plan: Optional[Dict[str, Any]] = None
    data: Optional[Any] = None
    row_count: Optional[int] = 0
    explanation: Optional[str] = None
    error: Optional[str] = None
