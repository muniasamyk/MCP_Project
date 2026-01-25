"""
MCP Dummy DB Integration and Data Retrieval POC

Entry point for running the agentic workflow demo.
"""

import os
import sys

if sys.platform == "win32":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")

from agents.orchestrator import AgentOrchestrator


def main() -> None:
    llm_provider = os.getenv("MCP_LLM_PROVIDER", "mock")
    model = os.getenv("MCP_LLM_MODEL", "tinyllama")

    orchestrator = AgentOrchestrator(llm_provider=llm_provider, model=model)

    print("MCP Dummy DB Integration POC")
    print(f"LLM provider: {llm_provider} | model: {model}")
    print("Type a question (or 'exit'):\n")

    while True:
        try:
            query = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            return

        if not query:
            continue
        if query.lower() in {"exit", "quit"}:
            print("Bye.")
            return

        result = orchestrator.process_query(query)
        if result.get("status") == "success":
            print(result.get("explanation", ""))
            print()
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
            print()


if __name__ == "__main__":
    main()

