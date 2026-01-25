
# MCP Dummy DB Integration and Data Retrieval POC
## Executive Summary

This project demonstrates a secure, production-ready implementation of the **Model Context Protocol (MCP)** as a connector layer between AI agents and PostgreSQL databases. The solution enables natural language queries without exposing database credentials to the LLM.

**Key Achievement**: LLM cannot access database directly - only through predefined MCP tools.

---

## 🏗️ Architecture Overview

```
┌────────────────────────────────────────────────────────┐
│                    USER QUERY                         │
│          "Fetch employees in AI department"           │
└───────────────────┬────────────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────────────────┐
│         PLANNER AGENT (LLM)                           │
│  ✓ Natural Language Understanding                     │
│  ✗ NO database credentials                            │
│  Output: {"tool": "get_employees_by_department",      │
│           "parameters": {"department": "AI"}}         │
└───────────────────┬────────────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────────────────┐
│         EXECUTOR AGENT                                 │
│  ✓ Validates tool request                            │
│  ✓ Maps to allowed operations only                   │
│  ✗ Cannot execute arbitrary SQL                      │
└───────────────────┬────────────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────────────────┐
│         MCP TOOLS LAYER (Sandbox)                     │
│  ✓ get_employees_by_department("AI")                │
│  ✓ get_projects_by_status("Completed")              │
│  ✓ get_issues_by_priority("High")                   │
│  ✗ Cannot run arbitrary SQL                          │
└───────────────────┬────────────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────────────────┐
│         DATABASE CONNECTION (Secure)                  │
│  ✓ Credentials in environment variables             │
│  ✓ Only parameterized queries (SQL injection safe)  │
└───────────────────┬────────────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────────────────┐
│         RESULT TO USER                               │
│    [Secure data retrieval via MCP]                   │
└────────────────────────────────────────────────────────┘
```

## 🔒 Security Features

| Feature             | With MCP 
|---------            |---------
| **DB Credentials**  | Secure in .env ✅ 
| **SQL Access**      | Predefined tools only ✅ 
| **Attack Surface**  | Limited operations only ✅ 
| **Audit Trail**     | Full logging ✅ 
| **Connection Pool** | Yes ✅ 

## Project Structure
```
MCP Task/
├── demo_agent_workflow.py  # Main Entry point (Agentic Workflow)
├── main.py                 # Interactive CLI entry point
├── .env                    # Database credentials (not in git)
├── README.md               # This file
├── database/
│   └── db_executor.py     # Database connection & queries
├── mcp/
│   └── tools.py           # MCP tool definitions
├── agents/
│   ├── orchestrator.py    # Manages the Agentic Workflow
│   ├── planner_agent.py   # Query planning agent (w/ Robust Fallback)
│   ├── executor_agent.py  # Query execution agent (Safe validation)
│   ├── reasoner_agent.py  # Result explanation agent
│   └── llm_provider.py    # LLM Interface
├── utils/
│   └── serializer.py      # Custom JSON serialization
└── datas_insert/
    └── sample_data.sql    # Sample database setup (PostgreSQL)
```

## Setup Instructions

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Ollama (running locally) or other LLM provider
- pip packages: `psycopg2`, `python-dotenv`

### Installation
1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure `.env`:
   ```
   DB_HOST=localhost
   DB_PORT=5432
   DB_USER=postgres
   DB_PASSWORD=your_password
   DB_NAME=mcp_db
   ```
5. Initialize database:
   ```bash
   psql -U postgres -d mcp_db -f datas_insert/sample_data.sql
   ```

### Running the Demo
```bash
python demo_agent_workflow.py
```

### Running the Interactive CLI
```bash
python main.py
```

## Agentic Workflow Design

This project uses a multi-agent secure architecture:

1.  **Orchestrator**: The central brain that manages the lifecycle of a request.
2.  **Planner Agent**:
    *   **Role**: Analyzes the user query and selects the appropriate MCP tool.
    *   **Robustness**: Uses a **Dual-Layer Strategy**.
        *   *Layer 1*: Tries to parse the LLM's JSON output.
        *   *Layer 2*: If LLM output is malformed (common with small models), it falls back to a deterministic **keyword extraction** strategy to ensure the query is always answered correctly.
3.  **Executor Agent**:
    *   **Role**: Validates the plan and executes the cached tool.
    *   **Safety**: Ensures only allowed tools are called and handles parameter types safely.
4.  **MCP Tool Layer**: A sandboxed layer that prevents direct SQL access.
5.  **Reasoner Agent**: (Optional) Summarizes the raw data into a human-readable answer.

## How MCP Works as a Connector Layer

1. **User Query** → "Fetch employee details where department is AI"
2. **Planner Agent** → LLM interprets query, creates plan without DB access
3. **MCP Tools** → Translates plan to allowed operations (get_employees_by_department)
4. **Secure Execution** → Only predefined MCP tools can access the database
5. **Result** → Data returned to user

**Security Benefit**: The LLM never sees or uses database credentials directly.

## MCP Tools Available
- `get_employees_by_department(department)` - Fetch employees by department
- `get_projects_by_status(status)` - Fetch projects by status
- `get_issues_by_priority(priority)` - Fetch issues by priority

## Example Queries
- "Fetch employee details where department is AI"
- "Show all projects with status completed"
- "List all high priority issues"


**Created by: [Muniasamy K](https://github.com/muniasamy)**
