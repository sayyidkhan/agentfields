import type { JudgeDecision, UserPersona } from '../types';

interface JudgeDecisionViewProps {
  decision: JudgeDecision;
  persona: UserPersona;
}

const agentLabels = {
  fire: { icon: '🔥', name: 'Fire (Momentum)', color: 'fire' },
  water: { icon: '💧', name: 'Water (Conservative)', color: 'water' },
  grass: { icon: '🌱', name: 'Grass (Adaptive)', color: 'grass' },
};

export default function JudgeDecisionView({ decision, persona }: JudgeDecisionViewProps) {
  const selected = agentLabels[decision.selected_agent];

  return (
    <div className="space-y-6">
      {/* Judge Header */}
      <div className="text-center">
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-judge/10 border border-judge/30 mb-4">
          <span className="text-xl">⚖️</span>
          <span className="text-judge font-semibold text-sm">Judge Agent Decision</span>
        </div>

        <h3 className="text-2xl font-bold text-white mb-1">
          {selected.icon} {selected.name}
        </h3>
        <p className="text-muted text-sm">Selected as the best strategy for your profile</p>
      </div>

      {/* Alignment Score */}
      <div className="bg-surface rounded-xl p-5 border border-surface-light">
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm font-medium text-muted">Persona Alignment</span>
          <span className="text-2xl font-bold text-judge">
            {(decision.persona_alignment_score * 100).toFixed(0)}%
          </span>
        </div>
        <div className="h-3 rounded-full bg-surface-light overflow-hidden">
          <div
            className="h-full rounded-full bg-gradient-to-r from-judge/60 to-judge transition-all duration-1000"
            style={{ width: `${decision.persona_alignment_score * 100}%` }}
          />
        </div>
        <div className="flex justify-between text-xs text-muted mt-2">
          <span>Based on: {persona.risk_tolerance} risk, {persona.time_horizon} horizon, {persona.drawdown_sensitivity} drawdown sensitivity</span>
        </div>
      </div>

      {/* Recommendation */}
      <div className="bg-surface rounded-xl p-5 border border-surface-light">
        <h4 className="text-sm font-semibold uppercase tracking-wider text-muted mb-3">
          Recommendation
        </h4>
        <p className="text-white leading-relaxed text-[15px]">
          {decision.recommendation_summary}
        </p>
      </div>

      {/* Reasoning */}
      <div className="bg-surface rounded-xl p-5 border border-surface-light">
        <h4 className="text-sm font-semibold uppercase tracking-wider text-muted mb-3">
          Judge Reasoning
        </h4>
        <p className="text-muted leading-relaxed text-sm">
          {decision.reasoning}
        </p>
      </div>

      {/* Tradeoffs */}
      {decision.tradeoffs.length > 0 && (
        <div className="bg-surface rounded-xl p-5 border border-surface-light">
          <h4 className="text-sm font-semibold uppercase tracking-wider text-muted mb-3">
            Key Tradeoffs
          </h4>
          <ul className="space-y-2">
            {decision.tradeoffs.map((t, i) => (
              <li key={i} className="flex items-start gap-3 text-sm text-muted">
                <span className="text-judge mt-0.5 flex-shrink-0">&#9670;</span>
                <span>{t}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
