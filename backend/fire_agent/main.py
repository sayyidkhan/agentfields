"""
MagiStock — Fire Agent (Aggressive / Momentum Strategy)

🔥 Focus: Momentum, volatility, asymmetric upside
   Objective: Maximize returns
   Accepts high drawdowns
   Performs best in trending or speculative markets
"""

import sys
import os
from pathlib import Path

# Add project root to path for shared imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(os.path.join(Path(__file__).parent.parent, ".env"))

from agentfield import Agent, AIConfig
from skills import skills_router
from reasoners import reasoners_router

app = Agent(
    node_id="fire-agent",
    agentfield_server=os.getenv("AGENTFIELD_SERVER", "http://localhost:8080"),
    version="1.0.0",
    dev_mode=True,
    ai_config=AIConfig(
        model=os.getenv("AI_MODEL", "openai/gpt-4o"),
        temperature=0.7,
    ),
)

app.include_router(skills_router)
app.include_router(reasoners_router)

if __name__ == "__main__":
    app.run()
