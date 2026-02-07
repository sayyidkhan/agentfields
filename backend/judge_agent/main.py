"""
MagiStock — Judge Agent (Persona-Aware Arbiter)

⚖️  The synthesis agent in the Coordination pattern.
    Selects the most suitable strategy based on the USER PERSONA, not just performance.
    Shifts the system from "best strategy" to "best strategy for you".
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
    node_id="judge-agent",
    agentfield_server=os.getenv("AGENTFIELD_SERVER", "http://localhost:8080"),
    version="1.0.0",
    dev_mode=True,
    ai_config=AIConfig(
        model=os.getenv("AI_MODEL", "openai/gpt-4o"),
        temperature=0.5,  # Lower temperature for more consistent judgment
    ),
)

app.include_router(reasoners_router)

if __name__ == "__main__":
    app.run()
