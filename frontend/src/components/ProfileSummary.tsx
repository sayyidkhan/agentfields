import type { UserPersona, RiskTolerance, TimeHorizon, DrawdownSensitivity } from '../types';
import StockChart from './StockChart';

interface ProfileSummaryProps {
  persona: UserPersona;
  summary: string;
  ticker: string;
  onConfirm: () => void;
  onEdit: () => void;
  loading: boolean;
}

const riskConfig: Record<RiskTolerance, { label: string; icon: string; color: string; bg: string }> = {
  low: { label: 'Conservative', icon: '🛡️', color: 'text-water', bg: 'bg-water/10 border-water/30' },
  medium: { label: 'Balanced', icon: '⚖️', color: 'text-judge', bg: 'bg-judge/10 border-judge/30' },
  high: { label: 'Aggressive', icon: '🚀', color: 'text-fire', bg: 'bg-fire/10 border-fire/30' },
};

const horizonConfig: Record<TimeHorizon, { label: string; icon: string; color: string; bg: string }> = {
  short: { label: 'Short-term (< 1 year)', icon: '⏱️', color: 'text-fire', bg: 'bg-fire/10 border-fire/30' },
  long: { label: 'Long-term (1+ years)', icon: '📅', color: 'text-grass', bg: 'bg-grass/10 border-grass/30' },
};

const drawdownConfig: Record<DrawdownSensitivity, { label: string; icon: string; color: string; bg: string }> = {
  low: { label: 'Comfortable with drops', icon: '😎', color: 'text-grass', bg: 'bg-grass/10 border-grass/30' },
  medium: { label: 'Somewhat uneasy', icon: '😐', color: 'text-judge', bg: 'bg-judge/10 border-judge/30' },
  high: { label: 'Very loss-averse', icon: '😰', color: 'text-fire', bg: 'bg-fire/10 border-fire/30' },
};

export default function ProfileSummary({ persona, summary, ticker, onConfirm, onEdit, loading }: ProfileSummaryProps) {
  const risk = riskConfig[persona.risk_tolerance];
  const horizon = horizonConfig[persona.time_horizon];
  const drawdown = drawdownConfig[persona.drawdown_sensitivity];

  return (
    <div className="max-w-4xl mx-auto fade-in-up">
      {/* Header */}
      <div className="text-center mb-8">
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-grass/10 border border-grass/30 mb-4">
          <span className="text-grass text-sm">&#10003;</span>
          <span className="text-grass font-medium text-sm">Profile understood</span>
        </div>
        <h2 className="text-2xl font-bold text-white mb-2">Here&apos;s what we heard</h2>
        <p className="text-muted text-sm">Confirm this is right, or go back to adjust.</p>
      </div>

      {/* Two-column layout: chart + profile */}
      <div className="grid grid-cols-1 lg:grid-cols-[1fr_340px] gap-6 mb-8">
        {/* Left: Stock chart */}
        <div className="space-y-4">
          <StockChart ticker={ticker} height={380} />
        </div>

        {/* Right: Profile info */}
        <div className="space-y-4">
          {/* AI Summary */}
          <div className="bg-surface rounded-xl p-4 border border-surface-light">
            <div className="text-[10px] uppercase tracking-wider text-muted mb-2 font-semibold">Magi&apos;s Assessment</div>
            <p className="text-white text-[14px] leading-relaxed italic">&ldquo;{summary}&rdquo;</p>
          </div>

          {/* Profile cards */}
          <ProfileRow
            label="Risk Tolerance"
            icon={risk.icon}
            value={risk.label}
            color={risk.color}
            bg={risk.bg}
          />
          <ProfileRow
            label="Time Horizon"
            icon={horizon.icon}
            value={horizon.label}
            color={horizon.color}
            bg={horizon.bg}
          />
          <ProfileRow
            label="Loss Sensitivity"
            icon={drawdown.icon}
            value={drawdown.label}
            color={drawdown.color}
            bg={drawdown.bg}
          />
        </div>
      </div>

      {/* Actions */}
      <div className="max-w-lg mx-auto space-y-3">
        <button
          type="button"
          onClick={onConfirm}
          disabled={loading}
          className="w-full py-4 rounded-xl bg-gradient-to-r from-fire via-judge to-grass text-white font-bold text-lg 
                     transition-all duration-300 hover:shadow-lg hover:shadow-judge/20 hover:scale-[1.01] 
                     disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 cursor-pointer"
        >
          {loading ? (
            <span className="flex items-center justify-center gap-3">
              <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              Launching agents...
            </span>
          ) : (
            <>Looks right &mdash; analyze {ticker}</>
          )}
        </button>
        <button
          type="button"
          onClick={onEdit}
          disabled={loading}
          className="w-full py-3 rounded-xl bg-surface border border-surface-light text-muted text-sm
                     hover:text-white hover:border-muted/50 transition-all cursor-pointer
                     disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Not quite right &mdash; let me clarify
        </button>
      </div>
    </div>
  );
}

function ProfileRow({ label, icon, value, color, bg }: {
  label: string; icon: string; value: string; color: string; bg: string;
}) {
  return (
    <div className={`flex items-center gap-4 rounded-xl p-4 border ${bg}`}>
      <span className="text-2xl">{icon}</span>
      <div className="flex-1">
        <div className="text-[10px] uppercase tracking-wider text-muted">{label}</div>
        <div className={`font-semibold ${color}`}>{value}</div>
      </div>
    </div>
  );
}
