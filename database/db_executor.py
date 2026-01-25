import os
from dotenv import load_dotenv
import psycopg2
from utils.logger import get_logger

logger = get_logger(__name__)

# Load environment variables from .env (if present)
load_dotenv()

def get_connection():
    """
    Create a connection to the PostgreSQL database.

    Environment variables (see `.env.example`):
    - DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME
    """
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD"),
            dbname=os.getenv("DB_NAME", "mcp_db"),
        )
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to database: {str(e)}")
        return None

def fetch_employees_by_department(department):
    """
    Get employees from a specific department
    """
    conn = None
    try:
        conn = get_connection()
        if conn is None:
            return []
        
        cursor = conn.cursor()
        
        query = """
            SELECT id, name, email, department, salary 
            FROM employees 
            WHERE LOWER(department) = LOWER(%s)
            ORDER BY name
        """
        
        cursor.execute(query, (department,))
        result = cursor.fetchall()
        cursor.close()
        
        logger.info(f"Found {len(result)} employees in {department} department")
        return result
    
    except Exception as e:
        logger.error(f"Error fetching employees: {str(e)}")
        return []
    finally:
        if conn:
            conn.close()

def fetch_projects_by_status(status):
    """
    Get projects with a specific status
    """
    conn = None
    try:
        conn = get_connection()
        if conn is None:
            return []
        
        cursor = conn.cursor()
        
        query = """
            SELECT id, name, description, status, start_date, end_date, budget 
            FROM projects 
            WHERE LOWER(status) = LOWER(%s)
            ORDER BY name
        """
        
        cursor.execute(query, (status,))
        result = cursor.fetchall()
        cursor.close()
        
        logger.info(f"Found {len(result)} projects with status {status}")
        return result
    
    except Exception as e:
        logger.error(f"Error fetching projects: {str(e)}")
        return []
    finally:
        if conn:
            conn.close()

def fetch_issues_by_priority(priority):
    """
    Get issues with a specific priority
    """
    conn = None
    try:
        conn = get_connection()
        if conn is None:
            return []
        
        cursor = conn.cursor()
        
        query = """
            SELECT id, title, description, priority, status, assigned_to, project_id 
            FROM issues 
            WHERE LOWER(priority) = LOWER(%s)
            ORDER BY created_date DESC
        """
        
        cursor.execute(query, (priority,))
        result = cursor.fetchall()
        cursor.close()
        
        logger.info(f"Found {len(result)} issues with priority {priority}")
        return result
    
    except Exception as e:
        logger.error(f"Error fetching issues: {str(e)}")
        return []
    finally:
        if conn:
            conn.close()
