# MCP Agent POC

This is a **Proof of Concept** for a "Model Context Protocol" (MCP) agent. It connects a Large Language Model (LLM) to a secure database without letting the LLM run arbitrary SQL.

## How it Works

1. **User** asks a question (e.g., "Who works in the AI department?")
2. **Planner Agent** decides which tool to use (`get_employees_by_department`)
3. **Executor Agent** runs the tool safely (inputs match the schema)
4. **MCP Layer** executes the SQL query (parameterized, safe)
5. **Reasoner Agent** looks at the data and writes a summary

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
