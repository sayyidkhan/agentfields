"""
MagiStock — Shared Pydantic Schemas

All typed models used across agents. Every Reasoner produces structured data,
not free-form text. Your code consumes it directly.
"""

from pydantic import BaseModel, Field
from typing import Literal


# ─── User Persona ────────────────────────────────────────────────────────────

class UserPersona(BaseModel):
    """Simplified user profile for persona-aware strategy selection."""
    risk_tolerance: Literal["low", "medium", "high"] = Field(
        description="User's tolerance for investment risk"
    )
    time_horizon: Literal["short", "long"] = Field(
        description="Investment time horizon"
    )
    drawdown_sensitivity: Literal["low", "medium", "high"] = Field(
        description="How sensitive the user is to portfolio drawdowns"
    )


# ─── Backtest Results ────────────────────────────────────────────────────────

class BacktestResult(BaseModel):
    """Deterministic output from a backtesting Skill."""
    total_return: float = Field(description="Total return as decimal (e.g. 0.32 = 32%)")
    max_drawdown: float = Field(description="Maximum drawdown as negative decimal (e.g. -0.18)")
    volatility: float = Field(description="Annualized volatility as decimal")
    sharpe_ratio: float = Field(description="Sharpe ratio (risk-adjusted return)")
    trades: int = Field(description="Total number of trades executed")
    win_rate: float = Field(description="Percentage of winning trades (0.0 to 1.0)")
    avg_trade_return: float = Field(description="Average return per trade")


# ─── Strategy Critique ───────────────────────────────────────────────────────

class StrategyCritique(BaseModel):
    """AI-generated critique of a strategy's performance. Produced by Reasoners."""
    agent_name: Literal["fire", "water", "grass"] = Field(
        description="Which strategy agent produced this"
    )
    backtest: BacktestResult = Field(
        description="The underlying backtest results"
    )
    regime_suitability: str = Field(
        description="Assessment of which market regimes this strategy suits"
    )
    risk_alignment_score: float = Field(
        ge=0.0, le=1.0,
        description="How well this strategy aligns with risk management (0.0 to 1.0)"
    )
    strengths: list[str] = Field(
        description="Key strengths of this strategy"
    )
    weaknesses: list[str] = Field(
        description="Key weaknesses and risk factors"
    )
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Agent's confidence in this strategy (0.0 to 1.0)"
    )


# ─── Judge Decision ──────────────────────────────────────────────────────────

class JudgeDecision(BaseModel):
    """The Judge's final persona-aware recommendation. The core output of MagiStock."""
    selected_agent: Literal["fire", "water", "grass"] = Field(
        description="Which strategy agent was selected"
    )
    reasoning: str = Field(
        description="Detailed explanation of why this strategy was chosen for this user"
    )
    persona_alignment_score: float = Field(
        ge=0.0, le=1.0,
        description="How well the selected strategy aligns with the user's persona"
    )
    tradeoffs: list[str] = Field(
        description="Key tradeoffs the user should be aware of"
    )
    recommendation_summary: str = Field(
        description="One-paragraph summary suitable for presenting to the user"
    )


# ─── Market Regime ───────────────────────────────────────────────────────────

class MarketRegime(BaseModel):
    """AI-detected market regime used by the Grass (adaptive) agent."""
    regime: Literal["trending_up", "trending_down", "mean_reverting", "high_volatility"] = Field(
        description="Detected market regime"
    )
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Confidence in regime detection"
    )
    reasoning: str = Field(
        description="Explanation of why this regime was detected"
    )
    recommended_approach: str = Field(
        description="Recommended trading approach for this regime"
    )


# ─── Pipeline Result ─────────────────────────────────────────────────────────

class PipelineResult(BaseModel):
    """Complete output from a strategy agent's pipeline."""
    agent_name: str
    backtest: BacktestResult
    critique: StrategyCritique


# ─── Analysis Request ────────────────────────────────────────────────────────

class AnalysisRequest(BaseModel):
    """Input to the orchestrator's main analysis flow."""
    ticker: str = Field(default="SPY", description="Asset ticker symbol")
    period_days: int = Field(default=252, description="Historical period in trading days")
    persona: UserPersona
