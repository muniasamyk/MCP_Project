from app.database.db_executor import (
    execute_raw_sql,
    fetch_employees_by_department,
    fetch_projects_by_status,
    fetch_issues_by_priority
)
from app.utils.logger import get_logger

logger = get_logger(__name__)

# --- MCP Tool Wrappers ---

def run_sql_query(query: str):
    """
    Executes a raw SQL SELECT query.
    Use this tool when the user asks a complex question that requires joining tables or specific filtering not covered by other tools.
    The query MUST be a valid SQL SELECT statement.
    """
    logger.info(f"Tool: Run SQL Query")
    return execute_raw_sql(query)

def get_employees_by_department(department: str):
    """Fetch employees in a specific department (e.g. AI, Backend, Frontend)."""
    logger.info(f"Tool: Get employees (dept={department})")
    return fetch_employees_by_department(department)

def get_projects_by_status(status: str):
    """Fetch projects by status (e.g. In Progress, Completed, Planning)."""
    logger.info(f"Tool: Get projects (status={status})")
    return fetch_projects_by_status(status)

def get_issues_by_priority(priority: str):
    """Fetch issues by priority (High, Medium, Low, Critical)."""
    logger.info(f"Tool: Get issues (priority={priority})")
    return fetch_issues_by_priority(priority)

# Expose tools to the agent
# The keys here match what the Planner agent sees
TOOLS = {
    "run_sql_query": run_sql_query,
    "get_employees_by_department": get_employees_by_department,
    "get_projects_by_status": get_projects_by_status,
    "get_issues_by_priority": get_issues_by_priority,
}
