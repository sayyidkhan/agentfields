import { useEffect, useState, useRef } from 'react';

// ─── Console log entries ────────────────────────────────────────
// Each entry simulates a real agent action with realistic timing.

interface LogEntry {
  agent: string;
  color: string;
  message: string;
  delay: number; // ms after previous entry
  type: 'info' | 'ai' | 'skill' | 'memory' | 'result' | 'discovery';
}

function buildLogs(ticker: string): LogEntry[] {
  return [
    // Orchestrator starts
    { agent: 'Orchestrator', color: 'text-white', message: `Pipeline initiated — analyzing ${ticker} with user persona...`, delay: 400, type: 'info' },
    { agent: 'Orchestrator', color: 'text-white', message: 'Persona loaded: risk_tolerance, time_horizon, drawdown_sensitivity', delay: 300, type: 'memory' },
    { agent: 'Orchestrator', color: 'text-white', message: 'Discovering strategy agents via Control Plane...', delay: 500, type: 'discovery' },
    { agent: 'Control Plane', color: 'text-slate-400', message: 'Registered agents: [fire-agent, water-agent, grass-agent, judge-agent]', delay: 350, type: 'discovery' },
    { agent: 'Orchestrator', color: 'text-white', message: `Dispatching parallel ${ticker} analysis to Fire, Water, Grass agents`, delay: 400, type: 'info' },

    // Fire Agent
    { agent: 'Fire Agent', color: 'text-fire-light', message: `Received ${ticker} — running momentum strategy`, delay: 600, type: 'info' },
    { agent: 'Fire Agent', color: 'text-fire-light', message: `[skill] fetch_market_data → ${ticker} 1Y historical data (252 bars)`, delay: 450, type: 'skill' },
    { agent: 'Fire Agent', color: 'text-fire-light', message: '[skill] compute_indicators → SMA(20), SMA(50), RSI(14), MACD', delay: 350, type: 'skill' },
    { agent: 'Fire Agent', color: 'text-fire-light', message: `[skill] run_momentum_backtest → simulating long-only momentum on ${ticker}...`, delay: 500, type: 'skill' },

    // Water Agent (parallel)
    { agent: 'Water Agent', color: 'text-water-light', message: `Received ${ticker} — running conservative strategy`, delay: 100, type: 'info' },
    { agent: 'Water Agent', color: 'text-water-light', message: `[skill] fetch_market_data → ${ticker} 1Y historical data (252 bars)`, delay: 400, type: 'skill' },
    { agent: 'Water Agent', color: 'text-water-light', message: '[skill] compute_indicators → Bollinger Bands, rolling volatility', delay: 350, type: 'skill' },
    { agent: 'Water Agent', color: 'text-water-light', message: `[skill] run_conservative_backtest → simulating capital preservation on ${ticker}...`, delay: 450, type: 'skill' },

    // Grass Agent (parallel)
    { agent: 'Grass Agent', color: 'text-grass-light', message: `Received ${ticker} — running adaptive strategy`, delay: 100, type: 'info' },
    { agent: 'Grass Agent', color: 'text-grass-light', message: `[skill] fetch_market_data → ${ticker} 1Y historical data (252 bars)`, delay: 300, type: 'skill' },
    { agent: 'Grass Agent', color: 'text-grass-light', message: '[skill] compute_regime_indicators → autocorrelation, vol clustering', delay: 400, type: 'skill' },

    // Fire backtest done
    { agent: 'Fire Agent', color: 'text-fire-light', message: '[skill] calculate_fire_metrics → return: +18.4%, sharpe: 1.21, max_dd: -12.3%', delay: 300, type: 'result' },
    { agent: 'Fire Agent', color: 'text-fire-light', message: '[reasoner] critique_fire_strategy → calling AI (gpt-4o)...', delay: 200, type: 'ai' },

    // Grass regime detection
    { agent: 'Grass Agent', color: 'text-grass-light', message: `[reasoner] detect_market_regime → analyzing ${ticker} regime (gpt-4o)...`, delay: 350, type: 'ai' },
    { agent: 'Grass Agent', color: 'text-grass-light', message: '[reasoner] AI response: regime = "trending_up", confidence = 0.78', delay: 800, type: 'ai' },
    { agent: 'Grass Agent', color: 'text-grass-light', message: '[skill] run_adaptive_backtest → momentum-biased for trending regime', delay: 400, type: 'skill' },

    // Water done
    { agent: 'Water Agent', color: 'text-water-light', message: '[skill] calculate_water_metrics → return: +7.2%, sharpe: 0.89, max_dd: -4.1%', delay: 200, type: 'result' },
    { agent: 'Water Agent', color: 'text-water-light', message: '[reasoner] critique_water_strategy → calling AI (gpt-4o)...', delay: 200, type: 'ai' },

    // Fire AI critique returns
    { agent: 'Fire Agent', color: 'text-fire-light', message: `[reasoner] AI critique: "Strong ${ticker} momentum capture but elevated drawdown risk..."`, delay: 600, type: 'ai' },
    { agent: 'Fire Agent', color: 'text-fire-light', message: 'Pipeline complete — storing results in Shared Memory', delay: 200, type: 'memory' },

    // Water AI critique returns
    { agent: 'Water Agent', color: 'text-water-light', message: '[reasoner] AI critique: "Excellent capital preservation, tight drawdowns..."', delay: 500, type: 'ai' },
    { agent: 'Water Agent', color: 'text-water-light', message: 'Pipeline complete — storing results in Shared Memory', delay: 200, type: 'memory' },

    // Grass finishes
    { agent: 'Grass Agent', color: 'text-grass-light', message: '[skill] calculate_grass_metrics → return: +14.1%, sharpe: 1.08, max_dd: -8.7%', delay: 400, type: 'result' },
    { agent: 'Grass Agent', color: 'text-grass-light', message: '[reasoner] critique_grass_strategy → calling AI (gpt-4o)...', delay: 200, type: 'ai' },
    { agent: 'Grass Agent', color: 'text-grass-light', message: '[reasoner] AI critique: "Smart regime adaptation but switching costs add up..."', delay: 700, type: 'ai' },
    { agent: 'Grass Agent', color: 'text-grass-light', message: 'Pipeline complete — storing results in Shared Memory', delay: 200, type: 'memory' },

    // Shared Memory
    { agent: 'Shared Memory', color: 'text-purple-400', message: `workflow:${ticker.toLowerCase()} → 3 strategy results stored (fire, water, grass)`, delay: 300, type: 'memory' },
    { agent: 'Shared Memory', color: 'text-purple-400', message: `workflow:${ticker.toLowerCase()} → 3 AI critiques stored`, delay: 200, type: 'memory' },

    // Judge Agent
    { agent: 'Orchestrator', color: 'text-white', message: 'All strategies complete — dispatching to Judge Agent via app.call()', delay: 400, type: 'discovery' },
    { agent: 'Judge Agent', color: 'text-judge', message: `Received ${ticker} strategy results + persona for evaluation`, delay: 500, type: 'info' },
    { agent: 'Judge Agent', color: 'text-judge', message: '[reasoner] select_strategy → calling AI (gpt-4o, temp=0.5)...', delay: 300, type: 'ai' },
    { agent: 'Judge Agent', color: 'text-judge', message: '[reasoner] AI evaluating persona alignment: risk, horizon, drawdown fit...', delay: 800, type: 'ai' },
    { agent: 'Judge Agent', color: 'text-judge', message: `[reasoner] Best strategy selected for ${ticker} — generating explanation...`, delay: 600, type: 'ai' },
    { agent: 'Judge Agent', color: 'text-judge', message: '[reasoner] explain_decision → calling AI (gpt-4o)...', delay: 300, type: 'ai' },
    { agent: 'Judge Agent', color: 'text-judge', message: '[reasoner] Decision + explanation ready', delay: 700, type: 'result' },

    // Final
    { agent: 'Shared Memory', color: 'text-purple-400', message: `workflow:${ticker.toLowerCase()} → judge decision stored`, delay: 200, type: 'memory' },
    { agent: 'Orchestrator', color: 'text-white', message: `app.note("analysis_complete") — ${ticker} analysis finished successfully`, delay: 300, type: 'info' },
    { agent: 'Orchestrator', color: 'text-white', message: 'Pipeline complete — delivering results to UI', delay: 400, type: 'result' },
  ];
}

// ─── Step tracker (sidebar) ─────────────────────────────────────

const STEPS = [
  { id: 'init', label: 'Initialize pipeline', agent: 'Orchestrator', triggerLog: 0 },
  { id: 'fire', label: 'Momentum backtest + AI critique', agent: 'Fire Agent', triggerLog: 5 },
  { id: 'water', label: 'Conservative backtest + AI critique', agent: 'Water Agent', triggerLog: 9 },
  { id: 'grass', label: 'Regime detection + adaptive backtest', agent: 'Grass Agent', triggerLog: 13 },
  { id: 'memory', label: 'Results stored in Shared Memory', agent: 'Control Plane', triggerLog: 30 },
  { id: 'judge', label: 'Persona-aware strategy selection', agent: 'Judge Agent', triggerLog: 33 },
  { id: 'done', label: 'Delivering results', agent: 'Orchestrator', triggerLog: 40 },
];

// Type badge color map
function typeBadge(type: LogEntry['type']) {
  switch (type) {
    case 'ai':        return { bg: 'bg-amber-500/15', text: 'text-amber-400', label: 'AI' };
    case 'skill':     return { bg: 'bg-blue-500/15', text: 'text-blue-400', label: 'SKILL' };
    case 'memory':    return { bg: 'bg-purple-500/15', text: 'text-purple-400', label: 'MEM' };
    case 'discovery': return { bg: 'bg-cyan-500/15', text: 'text-cyan-400', label: 'DISC' };
    case 'result':    return { bg: 'bg-green-500/15', text: 'text-green-400', label: 'RES' };
    default:          return { bg: 'bg-slate-500/15', text: 'text-slate-400', label: 'INFO' };
  }
}

interface AnalyzingViewProps {
  ticker?: string;
}

export default function AnalyzingView({ ticker = 'SPY' }: AnalyzingViewProps) {
  const logs = buildLogs(ticker);
  const [visibleLogs, setVisibleLogs] = useState<number>(0);
  const consoleRef = useRef<HTMLDivElement>(null);

  // Stream log entries with realistic timing
  useEffect(() => {
    let timeoutId: ReturnType<typeof setTimeout>;
    let current = 0;

    function showNext() {
      if (current >= logs.length) return;
      current++;
      setVisibleLogs(current);

      if (current < logs.length) {
        timeoutId = setTimeout(showNext, logs[current].delay);
      }
    }

    // Start after a brief pause
    timeoutId = setTimeout(showNext, logs[0].delay);

    return () => clearTimeout(timeoutId);
  }, [logs]);

  // Auto-scroll console smoothly
  useEffect(() => {
    if (consoleRef.current) {
      consoleRef.current.scrollTo({
        top: consoleRef.current.scrollHeight,
        behavior: 'smooth',
      });
    }
  }, [visibleLogs]);

  // Determine current step based on visible logs
  const currentStepIdx = STEPS.findIndex((step, i) => {
    // Active if we're past this step's trigger but before the next
    const nextStep = STEPS[i + 1];
    return visibleLogs >= step.triggerLog && (!nextStep || visibleLogs < nextStep.triggerLog);
  });
  
  // If not found (all complete), use last step
  const activeStepIdx = currentStepIdx >= 0 ? currentStepIdx : STEPS.length - 1;

  const elapsed = logs.slice(0, visibleLogs).reduce((sum, l) => sum + l.delay, 0);

  return (
    <div className="max-w-5xl mx-auto">
      {/* Header */}
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-white mb-2">Analyzing {ticker}</h2>
        <p className="text-muted text-sm">
          Three strategy agents analyze <span className="text-white font-medium">{ticker}</span> in parallel, then the Judge selects your best fit
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-[260px_1fr] gap-5">
        {/* ─── Left: Step tracker ─────────────── */}
        <div className="space-y-2">
          {STEPS.map((step, i) => {
            const isDone = i < activeStepIdx;
            const isActive = i === activeStepIdx;
            const isPending = i > activeStepIdx;

            return (
              <div
                key={step.id}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-300 ${
                  isActive
                    ? 'bg-surface border border-judge/30'
                    : isDone
                    ? 'bg-surface/40 border border-grass/10'
                    : 'border border-transparent opacity-35'
                }`}
              >
                {/* Dot */}
                <div className="flex-shrink-0">
                  {isDone ? (
                    <span className="text-grass text-sm">&#10003;</span>
                  ) : isActive ? (
                    <span className="block w-2 h-2 rounded-full bg-judge animate-pulse" />
                  ) : (
                    <span className="block w-2 h-2 rounded-full bg-muted/30" />
                  )}
                </div>
                <div className="min-w-0">
                  <div className={`text-xs font-medium truncate ${isPending ? 'text-muted/40' : 'text-white'}`}>
                    {step.label}
                  </div>
                  <div className={`text-[10px] ${isPending ? 'text-muted/25' : 'text-muted/60'}`}>
                    {step.agent}
                  </div>
                </div>
              </div>
            );
          })}

          {/* Progress info */}
          <div className="text-center pt-3 space-y-1">
            <div className="text-xs font-semibold text-judge">
              Step {activeStepIdx + 1} of {STEPS.length}
            </div>
            <div className="text-xs text-muted/50 font-mono">
              {(elapsed / 1000).toFixed(1)}s elapsed
            </div>
          </div>
        </div>

        {/* ─── Right: Console ─────────────────── */}
        <div className="rounded-xl bg-[#0d1117] border border-surface-light/20 overflow-hidden flex flex-col" style={{ height: '480px' }}>
          {/* Console title bar */}
          <div className="flex items-center gap-2 px-4 py-2.5 bg-[#161b22] border-b border-surface-light/20 flex-shrink-0">
            <div className="flex gap-1.5">
              <span className="w-3 h-3 rounded-full bg-fire/60" />
              <span className="w-3 h-3 rounded-full bg-judge/60" />
              <span className="w-3 h-3 rounded-full bg-grass/60" />
            </div>
            <span className="text-[11px] text-muted/60 font-mono ml-2">agent-console</span>
            <div className="flex-1" />
            <span className="text-[10px] text-muted/40 font-mono">{visibleLogs}/{logs.length} events</span>
          </div>

          {/* Console output */}
          <div ref={consoleRef} className="flex-1 overflow-y-auto p-4 space-y-1 scrollbar-thin font-mono text-[12px] leading-[1.7]">
            {logs.slice(0, visibleLogs).map((log, i) => {
              const badge = typeBadge(log.type);
              return (
                <div key={i} className="flex gap-2 items-start fade-in-up" style={{ animationDuration: '0.15s' }}>
                  {/* Timestamp */}
                  <span className="text-muted/30 flex-shrink-0 w-[52px] text-right">
                    {String(Math.floor(i / 60)).padStart(2, '0')}:{String(i % 60).padStart(2, '0')}.{String((i * 37) % 100).padStart(2, '0')}
                  </span>

                  {/* Type badge */}
                  <span className={`flex-shrink-0 px-1.5 py-0 rounded text-[10px] font-semibold ${badge.bg} ${badge.text}`}>
                    {badge.label}
                  </span>

                  {/* Agent */}
                  <span className={`flex-shrink-0 font-semibold ${log.color}`}>
                    [{log.agent}]
                  </span>

                  {/* Message */}
                  <span className="text-slate-300">{log.message}</span>
                </div>
              );
            })}

            {/* Cursor blink */}
            {visibleLogs < logs.length && (
              <div className="flex items-center gap-1 mt-1">
                <span className="w-2 h-4 bg-judge/60 animate-pulse rounded-sm" />
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Agent flow diagram */}
      <div className="mt-6 p-5 rounded-xl bg-surface/30 border border-surface-light/20">
        <div className="text-[10px] font-semibold uppercase tracking-wider text-muted/50 mb-3 text-center">
          Multi-Agent Data Flow
        </div>
        <div className="flex items-center justify-center gap-2 text-sm flex-wrap">
          <span className="px-3 py-1.5 rounded-lg bg-surface-light text-white font-medium text-xs">You</span>
          <span className="text-muted/40">&#8594;</span>
          <span className="px-3 py-1.5 rounded-lg bg-surface-light text-white font-medium text-xs">Orchestrator</span>
          <span className="text-muted/40">&#8594;</span>
          <div className="flex gap-1">
            <span className="px-2 py-1 rounded bg-fire/20 text-fire-light text-[11px]">Fire</span>
            <span className="px-2 py-1 rounded bg-water/20 text-water-light text-[11px]">Water</span>
            <span className="px-2 py-1 rounded bg-grass/20 text-grass-light text-[11px]">Grass</span>
          </div>
          <span className="text-muted/40">&#8594;</span>
          <span className="px-3 py-1.5 rounded-lg bg-purple-500/15 text-purple-400 font-medium text-xs">Shared Memory</span>
          <span className="text-muted/40">&#8594;</span>
          <span className="px-3 py-1.5 rounded-lg bg-judge/20 text-judge font-medium text-xs">Judge</span>
          <span className="text-muted/40">&#8594;</span>
          <span className="px-3 py-1.5 rounded-lg bg-grass/20 text-grass font-medium text-xs">Result</span>
        </div>
      </div>
    </div>
  );
}
