// ─── Persona ──────────────────────────────────────────────────────────────

export type RiskTolerance = 'low' | 'medium' | 'high';
export type TimeHorizon = 'short' | 'long';
export type DrawdownSensitivity = 'low' | 'medium' | 'high';

export interface UserPersona {
  risk_tolerance: RiskTolerance;
  time_horizon: TimeHorizon;
  drawdown_sensitivity: DrawdownSensitivity;
}

// ─── Chat ─────────────────────────────────────────────────────────────────

export interface ChatMessage {
  role: 'assistant' | 'user';
  content: string;
}

// ─── Backtest ─────────────────────────────────────────────────────────────

export interface BacktestResult {
  total_return: number;
  max_drawdown: number;
  volatility: number;
  sharpe_ratio: number;
  trades: number;
  win_rate: number;
  avg_trade_return: number;
}

// ─── Strategy Critique ────────────────────────────────────────────────────

export interface StrategyCritique {
  agent_name: string;
  backtest: BacktestResult;
  regime_suitability: string;
  risk_alignment_score: number;
  strengths: string[];
  weaknesses: string[];
  confidence: number;
}

// ─── Judge Decision ───────────────────────────────────────────────────────

export interface JudgeDecision {
  selected_agent: 'fire' | 'water' | 'grass';
  reasoning: string;
  persona_alignment_score: number;
  tradeoffs: string[];
  recommendation_summary: string;
}

// ─── Strategy Result ──────────────────────────────────────────────────────

export interface StrategyResult {
  agent_name: string;
  backtest: BacktestResult;
  metrics: Record<string, unknown>;
  critique: StrategyCritique;
  regime?: Record<string, unknown>;
}

// ─── Full Analysis Response ───────────────────────────────────────────────

export interface AnalysisResponse {
  decision: JudgeDecision;
  strategies: {
    fire: StrategyResult;
    water: StrategyResult;
    grass: StrategyResult;
  };
  persona: UserPersona;
  ticker: string;
  period_days: number;
}

// ─── API Response wrapper ─────────────────────────────────────────────────

export interface AgentfieldResponse {
  execution_id: string;
  status: string;
  result: AnalysisResponse;
  duration_ms: number;
}

// ─── App State ────────────────────────────────────────────────────────────

export type AppStep = 'chat' | 'summary' | 'analyzing' | 'results';
