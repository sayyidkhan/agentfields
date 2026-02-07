import type { AnalysisResponse } from '../types';
import StrategyCard from './StrategyCard';
import JudgeDecisionView from './JudgeDecisionView';
import StockChart from './StockChart';

interface ResultsViewProps {
  result: AnalysisResponse;
  onReset: () => void;
}

export default function ResultsView({ result, onReset }: ResultsViewProps) {
  const { decision, strategies, persona, ticker } = result;
  
  // Get the selected strategy details
  const selectedStrategy = strategies[decision.selected_agent];
  const initialInvestment = 1000;
  const finalValue = initialInvestment * (1 + selectedStrategy.backtest.total_return);
  const profit = finalValue - initialInvestment;

  const strategyNames: Record<string, string> = {
    fire: 'Fire (Aggressive Momentum)',
    water: 'Water (Conservative Preservation)',
    grass: 'Grass (Adaptive Regime-Switching)',
  };

  return (
    <div className="max-w-5xl mx-auto space-y-10">
      {/* Header */}
      <div className="text-center fade-in-up">
        <h2 className="text-3xl font-bold text-white mb-2">
          {ticker} Analysis Complete
        </h2>
        <p className="text-muted text-sm mb-4">
          Three strategy agents analyzed {ticker}. The Judge selected your best fit.
        </p>
        
        {/* Quick result summary */}
        <div className="inline-block bg-surface border border-judge/30 rounded-xl px-6 py-4 mt-2">
          <div className="text-xs uppercase tracking-wider text-muted mb-1">Best Strategy for Your Profile</div>
          <div className="text-2xl font-bold text-judge mb-2">
            {strategyNames[decision.selected_agent]}
          </div>
          <div className="text-sm text-muted">
            $1,000 would have grown to{' '}
            <span className={`font-bold ${profit > 0 ? 'text-grass' : 'text-fire-light'}`}>
              ${finalValue.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}
            </span>
            {' '}in 1 year
          </div>
        </div>
      </div>

      {/* Stock chart */}
      <div className="fade-in-up" style={{ animationDelay: '0.1s' }}>
        <StockChart ticker={ticker} height={340} />
      </div>

      {/* Strategy Comparison */}
      <div>
        <h3 className="text-sm font-semibold uppercase tracking-wider text-muted mb-2 text-center">
          Investment Scenario
        </h3>
        <p className="text-center text-muted text-sm mb-6">
          How <span className="text-white font-medium">$1,000</span> invested 1 year ago would have performed under each strategy
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 stagger-children">
          <StrategyCard
            result={strategies.fire}
            isSelected={decision.selected_agent === 'fire'}
            agentType="fire"
          />
          <StrategyCard
            result={strategies.water}
            isSelected={decision.selected_agent === 'water'}
            agentType="water"
          />
          <StrategyCard
            result={strategies.grass}
            isSelected={decision.selected_agent === 'grass'}
            agentType="grass"
          />
        </div>
      </div>

      {/* Judge Decision */}
      <div className="fade-in-up" style={{ animationDelay: '0.4s' }}>
        <JudgeDecisionView decision={decision} persona={persona} />
      </div>

      {/* Agent Flow Summary */}
      <div className="fade-in-up bg-surface rounded-xl p-6 border border-surface-light" style={{ animationDelay: '0.6s' }}>
        <h4 className="text-sm font-semibold uppercase tracking-wider text-muted mb-4 text-center">
          How This Was Built — Agentfield Primitives
        </h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
          <PrimitiveCard
            title="Reasoners"
            desc="AI critique, Judge persona matching, regime detection"
            icon="🧠"
          />
          <PrimitiveCard
            title="Skills"
            desc="Backtesting, indicators, portfolio math (deterministic)"
            icon="⚡"
          />
          <PrimitiveCard
            title="Memory"
            desc="Persona + strategy results flow between agents"
            icon="💾"
          />
          <PrimitiveCard
            title="Discovery"
            desc="Agents find each other via Control Plane"
            icon="🔍"
          />
        </div>
      </div>

      {/* Reset */}
      <div className="text-center pb-8">
        <button
          onClick={onReset}
          className="px-8 py-3 rounded-xl bg-surface border border-surface-light text-muted 
                     hover:text-white hover:border-muted/50 transition-all duration-200 cursor-pointer"
        >
          Try a different persona
        </button>
      </div>
    </div>
  );
}

function PrimitiveCard({ title, desc, icon }: { title: string; desc: string; icon: string }) {
  return (
    <div className="p-3 rounded-lg bg-darker/50">
      <div className="text-2xl mb-1">{icon}</div>
      <div className="font-semibold text-white text-sm">{title}</div>
      <div className="text-xs text-muted mt-1">{desc}</div>
    </div>
  );
}
