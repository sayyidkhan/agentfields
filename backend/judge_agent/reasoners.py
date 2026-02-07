"""
MagiStock — Judge Agent Reasoners

The core intelligence of MagiStock. The Judge weighs all strategy outputs
against the user's persona to select the most SUITABLE strategy — not
necessarily the one with the highest return.

This is what makes MagiStock different: behavioral alignment over performance.
"""

import json
from agentfield.router import AgentRouter
from shared.schemas import JudgeDecision, UserPersona, StrategyCritique

reasoners_router = AgentRouter(prefix="reasoners")


@reasoners_router.reasoner()
async def select_strategy(
    persona: dict,
    fire_result: dict,
    water_result: dict,
    grass_result: dict,
) -> dict:
    """
    The core judgment call — which strategy fits THIS user?

    Not the highest return. The best fit.

    This is what a lookup table could never do: synthetic judgment that weighs
    persona alignment, emotional sustainability, and practical suitability.
    """
    user = UserPersona(**persona)

    decision = await reasoners_router.ai(
        system="""You are a persona-aware investment arbiter for the MagiStock system.

Your role is NOT to pick the best-performing strategy. Your role is to pick 
the strategy that THIS SPECIFIC USER can actually stick with.

Key principles:
- A strategy the user abandons during a drawdown is worse than a lower-return 
  strategy they hold through volatility
- High-risk-tolerance users still need honest risk warnings
- Low-risk-tolerance users shouldn't be pushed into aggressive strategies 
  even if returns are higher
- Drawdown sensitivity matters MORE than stated risk tolerance (people 
  overestimate their tolerance)
- Time horizon affects which metrics matter most

Your judgment should weigh:
1. PERSONA FIT: Does this strategy match the user's stated profile?
2. EMOTIONAL SUSTAINABILITY: Can this user psychologically handle the drawdowns?
3. RISK-ADJUSTED PERFORMANCE: Sharpe ratio matters more than raw return
4. REGIME APPROPRIATENESS: Is the strategy suited to current conditions?

Be specific in your reasoning. Explain tradeoffs honestly.
The recommendation summary should be written directly TO the user in plain language.""",

        user=f"""Select the most suitable strategy for this user.

USER PERSONA:
- Risk Tolerance: {user.risk_tolerance}
- Time Horizon: {user.time_horizon}  
- Drawdown Sensitivity: {user.drawdown_sensitivity}

STRATEGY RESULTS:

🔥 FIRE (Aggressive Momentum):
{json.dumps(fire_result.get('critique', fire_result.get('backtest', {})), indent=2)}

💧 WATER (Conservative Capital-Preservation):
{json.dumps(water_result.get('critique', water_result.get('backtest', {})), indent=2)}

🌱 GRASS (Adaptive Regime-Switching):
{json.dumps(grass_result.get('critique', grass_result.get('backtest', {})), indent=2)}

Select the most suitable strategy for this user. Not the highest return — the best fit.
Explain your reasoning, rate persona alignment, list key tradeoffs, and write 
a recommendation summary addressed directly to the user.""",

        schema=JudgeDecision,
    )

    return decision.model_dump()


@reasoners_router.reasoner()
async def explain_decision(decision: dict, persona: dict) -> dict:
    """
    Generate a detailed, human-readable explanation of the Judge's decision.

    This additional Reasoner provides a more accessible explanation
    that can be shown in a UI or sent as a report.
    """
    user = UserPersona(**persona)

    explanation = await reasoners_router.ai(
        system="""You are a financial advisor explaining an investment strategy 
recommendation to a client. Be clear, empathetic, and educational.

Write in second person ("you", "your"). 
Acknowledge the user's preferences and concerns.
Explain WHY this strategy fits them specifically.
Include 2-3 specific, actionable takeaways.""",

        user=f"""Explain this strategy recommendation to the user:

Selected Strategy: {decision.get('selected_agent', 'unknown')}
Reasoning: {decision.get('reasoning', '')}
Tradeoffs: {json.dumps(decision.get('tradeoffs', []))}

User Profile:
- Risk tolerance: {user.risk_tolerance}
- Time horizon: {user.time_horizon}
- Drawdown sensitivity: {user.drawdown_sensitivity}

Write a warm, clear explanation (2-3 paragraphs) with specific takeaways.""",

        schema=str,
    )

    return {
        "decision": decision,
        "explanation": explanation,
        "persona": persona,
    }
