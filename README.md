# MCP Agent POC

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

- `app/agents/`: The brain (Planner, Executor, Orchestrator)
- `app/mcp/`: The tool layer (Connector to DB)
- `app/database/`: Low-level DB connection pool
- `app/api/`: FastAPI routes

## Getting Started

### 1. Setup Env
Copy the example config:
```sh
cp .env.example .env
```

### 2. Run with Docker
The easiest way to stand it up (Postgres + API):
```sh
docker-compose up --build
```
The API listens on **http://localhost:8000**.

### 3. Test It
You can use the swagger UI at `/docs` or curl:

```sh
curl -X POST "http://localhost:8000/api/v1/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "Find all projects that are in progress"}'
```

## Local Dev (No Docker)

If you have Python 3.11+ and a local Postgres running:

1. `pip install -r requirements.txt`
2. Update `.env` with your DB credentials
3. `python -m app.main`
