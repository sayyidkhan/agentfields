import { useState } from 'react';
import type { StrategyResult } from '../types';

interface StrategyCardProps {
  result: StrategyResult;
  isSelected: boolean;
  agentType: 'fire' | 'water' | 'grass';
}

const agentConfig = {
  fire: {
    icon: '🔥',
    name: 'Fire',
    subtitle: 'Aggressive Momentum',
    color: 'fire',
    borderColor: 'border-fire/40',
    bgColor: 'bg-fire/10',
    tagBg: 'bg-fire/20',
    tagText: 'text-fire-light',
  },
  water: {
    icon: '💧',
    name: 'Water',
    subtitle: 'Conservative Preservation',
    color: 'water',
    borderColor: 'border-water/40',
    bgColor: 'bg-water/10',
    tagBg: 'bg-water/20',
    tagText: 'text-water-light',
  },
  grass: {
    icon: '🌱',
    name: 'Grass',
    subtitle: 'Adaptive Regime-Switching',
    color: 'grass',
    borderColor: 'border-grass/40',
    bgColor: 'bg-grass/10',
    tagBg: 'bg-grass/20',
    tagText: 'text-grass-light',
  },
};

function formatPct(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

function formatUSD(value: number): string {
  return `$${value.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`;
}

export default function StrategyCard({ result, isSelected, agentType }: StrategyCardProps) {
  const config = agentConfig[agentType];
  const { backtest, critique } = result;
  const [expanded, setExpanded] = useState(false);

  // Investment scenario: $1,000 initial investment
  const initialInvestment = 1000;
  const finalValue = initialInvestment * (1 + backtest.total_return);
  const profit = finalValue - initialInvestment;
  const isProfit = profit > 0;

  return (
    <div
      className={`relative rounded-xl p-5 transition-all duration-300 border-2 ${
        isSelected
          ? `${config.borderColor} ${config.bgColor} ring-2 ring-${config.color}/20 scale-[1.02]`
          : 'border-surface-light bg-surface hover:border-muted/40'
      }`}
    >
      {/* Selected badge */}
      {isSelected && (
        <div className="absolute -top-3 left-1/2 -translate-x-1/2">
          <span className="px-3 py-1 rounded-full bg-judge text-dark text-xs font-bold uppercase tracking-wider">
            Best fit for you
          </span>
        </div>
      )}

      {/* Header */}
      <div className="flex items-center gap-3 mb-5">
        <span className="text-3xl">{config.icon}</span>
        <div>
          <h3 className="font-bold text-white text-lg">{config.name}</h3>
          <p className="text-xs text-muted">{config.subtitle}</p>
        </div>
      </div>

      {/* Investment scenario */}
      <div className="space-y-4">
        {/* Initial investment */}
        <div className="flex justify-between items-center">
          <span className="text-sm text-muted">Initial Investment</span>
          <span className="text-lg font-semibold text-white">{formatUSD(initialInvestment)}</span>
        </div>

        {/* Arrow */}
        <div className="flex justify-center">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-muted">
            <line x1="12" y1="5" x2="12" y2="19" />
            <polyline points="19 12 12 19 5 12" />
          </svg>
        </div>

        {/* Final value */}
        <div className="bg-darker/50 rounded-lg p-4">
          <div className="text-[10px] uppercase tracking-wider text-muted mb-1">After 1 Year</div>
          <div className={`text-2xl font-bold ${isProfit ? 'text-grass' : 'text-fire-light'}`}>
            {formatUSD(finalValue)}
          </div>
          <div className="flex items-center gap-2 mt-2">
            <span className={`text-sm font-medium ${isProfit ? 'text-grass' : 'text-fire-light'}`}>
              {isProfit ? '+' : ''}{formatUSD(profit)}
            </span>
            <span className={`text-xs ${isProfit ? 'text-grass/70' : 'text-fire-light/70'}`}>
              ({formatPct(backtest.total_return)})
            </span>
          </div>
        </div>

        {/* Quick stats */}
        <div className="grid grid-cols-2 gap-3 text-xs">
          <div>
            <div className="text-muted mb-0.5">Max Loss</div>
            <div className="font-semibold text-fire-light">{formatPct(backtest.max_drawdown)}</div>
          </div>
          <div>
            <div className="text-muted mb-0.5">Win Rate</div>
            <div className="font-semibold text-white">{formatPct(backtest.win_rate)}</div>
          </div>
        </div>

        {/* Expanded details */}
        {expanded && critique && (
          <div className="mt-4 pt-4 border-t border-surface-light/50 space-y-3 animate-in fade-in duration-200">
            {/* Performance metrics */}
            <div>
              <div className="text-xs font-semibold text-muted uppercase tracking-wider mb-2">Performance Details</div>
              <div className="grid grid-cols-3 gap-2 text-xs">
                <div>
                  <div className="text-muted mb-0.5">Sharpe Ratio</div>
                  <div className="font-semibold text-white">{backtest.sharpe_ratio.toFixed(2)}</div>
                </div>
                <div>
                  <div className="text-muted mb-0.5">Volatility</div>
                  <div className="font-semibold text-white">{formatPct(backtest.volatility)}</div>
                </div>
                <div>
                  <div className="text-muted mb-0.5">Trades</div>
                  <div className="font-semibold text-white">{backtest.trades}</div>
                </div>
              </div>
            </div>

            {/* AI Analysis */}
            <div>
              <div className="text-xs font-semibold text-muted uppercase tracking-wider mb-2">AI Analysis</div>
              
              {/* Confidence + Alignment */}
              <div className="grid grid-cols-2 gap-3 mb-3">
                <div>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-muted">Confidence</span>
                    <span className="text-white font-medium">{formatPct(critique.confidence)}</span>
                  </div>
                  <div className="h-1.5 rounded-full bg-surface-light overflow-hidden">
                    <div
                      className={`h-full rounded-full ${config.tagBg.replace('/20', '')}`}
                      style={{ width: `${critique.confidence * 100}%`, backgroundColor: `var(--color-${config.color})` }}
                    />
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-muted">Risk Fit</span>
                    <span className="text-white font-medium">{formatPct(critique.risk_alignment_score)}</span>
                  </div>
                  <div className="h-1.5 rounded-full bg-surface-light overflow-hidden">
                    <div
                      className="h-full rounded-full bg-judge"
                      style={{ width: `${critique.risk_alignment_score * 100}%` }}
                    />
                  </div>
                </div>
              </div>

              {/* Regime fit */}
              <div className="text-xs bg-darker/50 rounded-lg p-2.5 mb-3">
                <span className="font-medium text-white">Market fit:</span>{' '}
                <span className="text-muted">{critique.regime_suitability}</span>
              </div>

              {/* Strengths/Weaknesses */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <div className="text-xs font-semibold text-grass mb-1.5">Strengths</div>
                  <ul className="space-y-1">
                    {critique.strengths.map((s, i) => (
                      <li key={i} className="text-xs text-muted flex items-start gap-1.5">
                        <span className="text-grass mt-0.5 flex-shrink-0">+</span>
                        <span>{s}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                <div>
                  <div className="text-xs font-semibold text-fire mb-1.5">Weaknesses</div>
                  <ul className="space-y-1">
                    {critique.weaknesses.map((w, i) => (
                      <li key={i} className="text-xs text-muted flex items-start gap-1.5">
                        <span className="text-fire mt-0.5 flex-shrink-0">-</span>
                        <span>{w}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Toggle button */}
        <button
          type="button"
          onClick={() => setExpanded(!expanded)}
          className="w-full mt-4 py-2 rounded-lg border border-surface-light text-xs text-muted
                     hover:text-white hover:border-muted/50 transition-all cursor-pointer
                     flex items-center justify-center gap-1.5"
        >
          <span>{expanded ? 'Show Less' : 'Show Details'}</span>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="12"
            height="12"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            className={`transition-transform duration-200 ${expanded ? 'rotate-180' : ''}`}
          >
            <polyline points="6 9 12 15 18 9" />
          </svg>
        </button>
      </div>
    </div>
  );
}

