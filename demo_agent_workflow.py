"""
MCP Agent Workflow Demo - LLM Query Execution with Ollama
"""

import sys
import os

if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'

from agents.orchestrator import AgentOrchestrator


def main():
    """Execute queries through agent workflow"""
    
    llm_provider = os.getenv("MCP_LLM_PROVIDER", "mock")
    model = os.getenv("MCP_LLM_MODEL", "tinyllama")

    # Use 'mock' provider for reliable demo, or 'ollama' if you have it running
    orchestrator = AgentOrchestrator(llm_provider=llm_provider, model=model)
    
    queries = [
        "Fetch employee details where department is AI.",
        "What are the projects that are in progress?",
        "What are the high priority issues?",
    ]
    
    for query in queries:
        print(f"Query: {query}")
    
        
        result = orchestrator.process_query(query)
        
        if result.get("status") == "success":
            print(f"Answer: {result.get('explanation', '')}\n")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}\n")


if __name__ == "__main__":
    main()
