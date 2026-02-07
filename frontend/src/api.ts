import type { UserPersona, ChatMessage, AnalysisResponse, AgentfieldResponse } from './types';

const env = import.meta.env as unknown as Record<string, string | undefined>;
const OPENAI_API_KEY = env.VITE_OPENAI_API_KEY || env.OPENAI_API_KEY;
const OPENAI_MODEL = env.VITE_OPENAI_MODEL || env.OPENAI_MODEL || 'gpt-4o-mini';
const API_BASE = '/api/v1';

// ─── Conversational Persona Builder ───────────────────────────────────────

const ADVISOR_SYSTEM_PROMPT = `You are a warm, friendly investment advisor named Magi working for MagiStock — a persona-aware investment companion.

Your job is to understand the user's investment profile through natural conversation. You need to determine four things:
1. Risk tolerance (low, medium, or high)
2. Time horizon (short = under 1 year, long = 1+ years)
3. Drawdown sensitivity — how they emotionally react to portfolio drops (low, medium, or high)
4. A stock ticker they want to analyze (e.g. AAPL, TSLA, MSFT, SPY, etc.)

CONVERSATION RULES:
- Ask at most 2-3 follow-up questions — keep it concise, not an interrogation
- Ask questions that naturally reveal their risk profile (e.g. "How would you feel if your portfolio dropped 20% in a week?")
- If the user hasn't mentioned a specific stock, ask which stock or ETF they'd like to analyze
- If they're unsure about a stock, suggest a few popular options (e.g. AAPL, TSLA, MSFT, SPY, QQQ) based on their profile
- Be conversational and empathetic, not clinical
- Use plain language, avoid jargon
- Keep each response to 2-3 sentences max
- When you have enough information to determine all four dimensions (including a ticker), call the extract_persona function

IMPORTANT: Do NOT tell the user what their profile is. Just have the conversation and call the function when ready. The app will show them a summary.`;

const PERSONA_TOOL = {
  type: 'function' as const,
  function: {
    name: 'extract_persona',
    description: 'Extract the user investment persona once enough information has been gathered from the conversation.',
    parameters: {
      type: 'object',
      properties: {
        risk_tolerance: {
          type: 'string',
          enum: ['low', 'medium', 'high'],
          description: 'How much risk the user is comfortable with',
        },
        time_horizon: {
          type: 'string',
          enum: ['short', 'long'],
          description: 'Investment time horizon. short = under 1 year, long = 1+ years',
        },
        drawdown_sensitivity: {
          type: 'string',
          enum: ['low', 'medium', 'high'],
          description: 'How emotionally sensitive the user is to portfolio drops',
        },
        summary: {
          type: 'string',
          description: 'A 1-2 sentence summary of the user profile in second person (e.g. "You are a cautious investor who...")',
        },
        ticker: {
          type: 'string',
          description: 'The stock or ETF ticker symbol to analyze (e.g. AAPL, TSLA, SPY). Uppercase.',
        },
      },
      required: ['risk_tolerance', 'time_horizon', 'drawdown_sensitivity', 'summary', 'ticker'],
    },
  },
};

export interface AdvisorResponse {
  message: string | null;
  persona: (UserPersona & { summary: string; ticker: string }) | null;
}

function assertOpenAIConfigured() {
  if (!OPENAI_API_KEY || OPENAI_API_KEY.trim().length === 0) {
    throw new Error(
      [
        'OpenAI is not configured.',
        'Set `VITE_OPENAI_API_KEY` (recommended) or `OPENAI_API_KEY` in `frontend/.env.local`, then restart `npm run dev`.',
      ].join(' '),
    );
  }
}

/**
 * Send conversation to the advisor and get back either a follow-up message
 * or an extracted persona (when the model calls the function).
 */
export async function chatWithAdvisor(messages: ChatMessage[]): Promise<AdvisorResponse> {
  assertOpenAIConfigured();

  const openaiMessages = [
    { role: 'system' as const, content: ADVISOR_SYSTEM_PROMPT },
    ...messages.map((m) => ({ role: m.role as 'assistant' | 'user', content: m.content })),
  ];

  const response = await fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${OPENAI_API_KEY}`,
    },
    body: JSON.stringify({
      model: OPENAI_MODEL,
      messages: openaiMessages,
      tools: [PERSONA_TOOL],
      tool_choice: 'auto',
      temperature: 0.8,
    }),
  });

  if (!response.ok) {
    const err = await response.text();
    throw new Error(`OpenAI API error: ${err}`);
  }

  const data = await response.json();
  const choice = data.choices[0];

  // Check if the model called the extract_persona function
  if (choice.message.tool_calls && choice.message.tool_calls.length > 0) {
    const toolCall = choice.message.tool_calls[0];
    if (toolCall.function.name === 'extract_persona') {
      const args = JSON.parse(toolCall.function.arguments);
      return {
        message: null,
        persona: {
          risk_tolerance: args.risk_tolerance,
          time_horizon: args.time_horizon,
          drawdown_sensitivity: args.drawdown_sensitivity,
          summary: args.summary,
          ticker: (args.ticker || 'SPY').toUpperCase(),
        },
      };
    }
  }

  // Regular message response
  return {
    message: choice.message.content,
    persona: null,
  };
}

// ─── Analysis ─────────────────────────────────────────────────────────────

/**
 * Run a full MagiStock analysis via the Agentfield control plane.
 */
export async function runAnalysis(
  persona: UserPersona,
  ticker: string = 'SPY',
  periodDays: number = 252,
): Promise<AnalysisResponse> {
  const response = await fetch(`${API_BASE}/execute/magistock.run_analysis`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      input: {
        ticker,
        period_days: periodDays,
        risk_tolerance: persona.risk_tolerance,
        time_horizon: persona.time_horizon,
        drawdown_sensitivity: persona.drawdown_sensitivity,
      },
    }),
  });

  if (!response.ok) {
    const err = await response.text();
    throw new Error(`Analysis failed: ${err}`);
  }

  const data: AgentfieldResponse = await response.json();
  if (data.status !== 'succeeded') {
    throw new Error(`Analysis status: ${data.status}`);
  }
  return data.result;
}

// ─── Mock Data ────────────────────────────────────────────────────────────

export function generateMockAnalysis(persona: UserPersona, ticker: string = 'SPY'): AnalysisResponse {
  const fireBacktest = {
    total_return: 0.0907, max_drawdown: -0.0854, volatility: 0.1842,
    sharpe_ratio: 0.43, trades: 3, win_rate: 0.667, avg_trade_return: 0.0302,
  };
  const waterBacktest = {
    total_return: 0.0234, max_drawdown: -0.0312, volatility: 0.0823,
    sharpe_ratio: 0.18, trades: 5, win_rate: 0.6, avg_trade_return: 0.0047,
  };
  const grassBacktest = {
    total_return: 0.0612, max_drawdown: -0.0567, volatility: 0.1234,
    sharpe_ratio: 0.38, trades: 7, win_rate: 0.571, avg_trade_return: 0.0087,
  };

  let selected: 'fire' | 'water' | 'grass';
  let alignment: number;
  if (persona.risk_tolerance === 'high' && persona.drawdown_sensitivity === 'low') {
    selected = 'fire'; alignment = 0.88;
  } else if (persona.risk_tolerance === 'low' || persona.drawdown_sensitivity === 'high') {
    selected = 'water'; alignment = 0.91;
  } else {
    selected = 'grass'; alignment = 0.85;
  }

  const summaries: Record<string, string> = {
    fire: `Based on your profile, the aggressive momentum strategy offers the highest return potential at ${(fireBacktest.total_return * 100).toFixed(1)}%. With your risk appetite, drawdowns up to ${(Math.abs(fireBacktest.max_drawdown) * 100).toFixed(1)}% should be manageable. This strategy works best in trending markets.`,
    water: `Given your preference for capital preservation, the conservative strategy is your best fit. Returns are modest at ${(waterBacktest.total_return * 100).toFixed(1)}%, but the maximum drawdown of only ${(Math.abs(waterBacktest.max_drawdown) * 100).toFixed(1)}% means you can sleep at night. This is the strategy you'll actually stick with.`,
    grass: `The adaptive strategy balances risk and reward by switching approaches based on market conditions. With a ${(grassBacktest.total_return * 100).toFixed(1)}% return and controlled drawdown of ${(Math.abs(grassBacktest.max_drawdown) * 100).toFixed(1)}%, it offers a middle ground.`,
  };

  return {
    decision: {
      selected_agent: selected,
      reasoning: `After evaluating all three strategies against the user's ${persona.risk_tolerance} risk tolerance, ${persona.time_horizon} time horizon, and ${persona.drawdown_sensitivity} drawdown sensitivity, the ${selected} strategy provides the best persona-aligned fit.`,
      persona_alignment_score: alignment,
      tradeoffs: [
        selected === 'fire' ? 'Higher returns come with significant drawdown risk' : 'Lower drawdown risk means potentially missing strong rallies',
        `Strategy optimized for ${persona.time_horizon} time horizon`,
        selected === 'grass' ? 'Regime switching adds complexity but improves adaptability' : `${selected === 'fire' ? 'Momentum strategies struggle in sideways markets' : 'Conservative strategies underperform in strong bull markets'}`,
      ],
      recommendation_summary: summaries[selected],
    },
    strategies: {
      fire: {
        agent_name: 'fire', backtest: fireBacktest,
        metrics: { aggression_score: 0.59, risk_reward_ratio: 1.06 },
        critique: {
          agent_name: 'fire', backtest: fireBacktest,
          regime_suitability: 'Best suited for trending and speculative markets with strong directional momentum.',
          risk_alignment_score: 0.65,
          strengths: ['Strong upside capture in trending markets', 'Clear entry/exit signals via SMA crossovers', 'RSI confirmation reduces false signals'],
          weaknesses: ['Vulnerable to whipsaws in ranging markets', 'High drawdown potential during reversals', 'May miss initial moves due to indicator lag'],
          confidence: 0.72,
        },
      },
      water: {
        agent_name: 'water', backtest: waterBacktest,
        metrics: { preservation_score: 0.84, stability_score: 0.75 },
        critique: {
          agent_name: 'water', backtest: waterBacktest,
          regime_suitability: 'Excels in sideways, uncertain, or mildly bearish markets where capital preservation matters most.',
          risk_alignment_score: 0.88,
          strengths: ['Excellent drawdown control', 'Low volatility provides psychological comfort', 'Works well in uncertain environments'],
          weaknesses: ['Significantly underperforms in bull markets', 'Few trade opportunities limit upside', 'May stay in cash too long during recoveries'],
          confidence: 0.81,
        },
      },
      grass: {
        agent_name: 'grass', backtest: grassBacktest,
        metrics: { consistency_score: 0.57, adaptability_score: 0.68 },
        critique: {
          agent_name: 'grass', backtest: grassBacktest,
          regime_suitability: 'Versatile across market conditions due to regime-switching, though regime detection has inherent lag.',
          risk_alignment_score: 0.76,
          strengths: ['Adapts to changing market conditions', 'Balances risk and reward effectively', 'Regime detection adds an intelligent layer'],
          weaknesses: ['Regime switching can cause whipsaw losses', 'More complex signals may lag in fast markets', 'Jack of all trades, master of none'],
          confidence: 0.68,
        },
      },
    },
    persona, ticker, period_days: 252,
  };
}
