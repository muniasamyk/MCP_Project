from database.db_executor import (
    fetch_employees_by_department,
    fetch_projects_by_status,
    fetch_issues_by_priority
)
from utils.logger import get_logger

logger = get_logger(__name__)


# Tool 1: Get employees by department
def mcp_get_employees_by_department(department):
    """
    Tool: Fetch employees from a specific department
    
    Parameters:
    - department: string like 'AI', 'Backend', 'Frontend'
    
    Returns:
    - List of employee records
    """
    logger.info(f"Tool called: get_employees_by_department with input={department}")
    return fetch_employees_by_department(department)

# Tool 2: Get projects by status
def mcp_get_projects_by_status(status):
    """
    Tool: Fetch projects with a specific status
    
    Parameters:
    - status: string like 'Completed', 'In Progress'
    
    Returns:
    - List of project records
    """
    logger.info(f"Tool called: get_projects_by_status with input={status}")
    return fetch_projects_by_status(status)

# Tool 3: Get issues by priority
def mcp_get_issues_by_priority(priority):
    """
    Tool: Fetch issues with a specific priority
    
    Parameters:
    - priority: string like 'High', 'Medium', 'Low'
    
    Returns:
    - List of issue records
    """
    logger.info(f"Tool called: get_issues_by_priority with input={priority}")
    return fetch_issues_by_priority(priority)

# This dictionary is THE SANDBOX
# LLM can ONLY use tools listed here
TOOLS = {
    "get_employees_by_department": mcp_get_employees_by_department,
    "get_projects_by_status": mcp_get_projects_by_status,
    "get_issues_by_priority": mcp_get_issues_by_priority,
}
