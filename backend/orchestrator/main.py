"""
MagiStock — Orchestrator Agent

The main entry point for the MagiStock system.
Coordinates all strategy agents and the Judge using Agentfield primitives:
- Cross-agent communication via app.call()
- Shared memory for state coordination
- Parallel execution of strategy pipelines
"""

import sys
import os
from pathlib import Path

# Add project root to path for shared imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(os.path.join(Path(__file__).parent.parent, ".env"))

from agentfield import Agent, AIConfig
from reasoners import reasoners_router

app = Agent(
    node_id="magistock",
    agentfield_server=os.getenv("AGENTFIELD_SERVER", "http://localhost:8080"),
    version="1.0.0",
    dev_mode=True,
    ai_config=AIConfig(
        model=os.getenv("AI_MODEL", "openai/gpt-4o"),
        temperature=0.7,
    ),
)

app.include_router(reasoners_router)

if __name__ == "__main__":
    app.run()
