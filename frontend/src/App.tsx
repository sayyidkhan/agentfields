import { useState } from 'react';
import type { AppStep, UserPersona, AnalysisResponse, ChatMessage } from './types';
import { runAnalysis, generateMockAnalysis } from './api';
import ChatPersona from './components/ChatPersona';
import ProfileSummary from './components/ProfileSummary';
import AnalyzingView from './components/AnalyzingView';
import ResultsView from './components/ResultsView';

// Set to true to use mock strategy analysis (no Agentfield backend required)
// The chat with Magi always uses the real OpenAI API.
const USE_MOCK_ANALYSIS = true;

function App() {
  const [step, setStep] = useState<AppStep>('chat');
  const [loading, setLoading] = useState(false);
  const [persona, setPersona] = useState<UserPersona | null>(null);
  const [profileSummary, setProfileSummary] = useState('');
  const [, setChatHistory] = useState<ChatMessage[]>([]);
  const [ticker, setTicker] = useState('SPY');
  const [result, setResult] = useState<AnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  // Increment to force ChatPersona remount (clears its internal message state)
  const [sessionKey, setSessionKey] = useState(0);

  // Chat complete — AI extracted the persona + ticker
  const handleProfileReady = (p: UserPersona, summary: string, t: string, messages: ChatMessage[]) => {
    setPersona(p);
    setProfileSummary(summary);
    setTicker(t);
    setChatHistory(messages);
    setStep('summary');
  };

  // User confirmed the profile — run analysis
  const handleConfirmProfile = async () => {
    if (!persona) return;
    setLoading(true);
    setError(null);
    setStep('analyzing');

    try {
      let analysisResult: AnalysisResponse;

      if (USE_MOCK_ANALYSIS) {
        // Wait long enough for the console animation to finish (~14s of logs)
        await new Promise((r) => setTimeout(r, 15000));
        analysisResult = generateMockAnalysis(persona, ticker);
      } else {
        analysisResult = await runAnalysis(persona, ticker);
      }

      setResult(analysisResult);
      setStep('results');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed');
      setStep('summary');
    } finally {
      setLoading(false);
    }
  };

  // Go back to chat to refine
  const handleEditProfile = () => {
    setStep('chat');
  };

  // Full reset — bumps sessionKey so ChatPersona remounts fresh
  const handleReset = () => {
    setStep('chat');
    setPersona(null);
    setProfileSummary('');
    setTicker('SPY');
    setChatHistory([]);
    setResult(null);
    setError(null);
    setSessionKey((k) => k + 1);
  };

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="border-b border-surface-light/30 bg-darker/80 backdrop-blur-sm sticky top-0 z-50 flex-shrink-0">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3 cursor-pointer" onClick={handleReset}>
            <img src="/three-magi.png" alt="MagiStock" className="w-8 h-8 rounded" />
            <div>
              <h1 className="text-lg font-bold text-white tracking-tight">MagiStock</h1>
              <p className="text-[10px] text-muted -mt-0.5">Persona-Aware Investment Companion</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* Step indicators */}
            <div className="hidden sm:flex items-center gap-2 text-xs">
              <StepPill label="Chat" active={step === 'chat'} done={step !== 'chat'} />
              <span className="text-surface-light">&#8594;</span>
              <StepPill label="Profile" active={step === 'summary'} done={step === 'analyzing' || step === 'results'} />
              <span className="text-surface-light">&#8594;</span>
              <StepPill label="Analysis" active={step === 'analyzing'} done={step === 'results'} />
              <span className="text-surface-light">&#8594;</span>
              <StepPill label="Results" active={step === 'results'} done={false} />
            </div>

            {/* New session button */}
            <button
              type="button"
              onClick={handleReset}
              className="flex items-center gap-1.5 text-xs text-muted hover:text-white transition-colors 
                         px-3 py-1.5 rounded-lg border border-surface-light hover:border-judge/40 
                         hover:bg-judge/5 cursor-pointer"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
                <path d="M3 3v5h5" />
                <path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16" />
                <path d="M21 21v-5h-5" />
              </svg>
              New Chat
            </button>

            <a
              href="https://agentfield.ai"
              target="_blank"
              rel="noopener noreferrer"
              className="hidden sm:inline-flex text-xs text-muted hover:text-white transition-colors px-3 py-1.5 rounded-lg border border-surface-light hover:border-muted/50"
            >
              Built on Agentfield
            </a>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="flex-1 max-w-6xl mx-auto px-6 py-8 w-full">
        {/* Error banner */}
        {error && (
          <div className="mb-6 p-4 rounded-xl bg-fire/10 border border-fire/30 text-fire-light text-sm">
            <span className="font-medium">Error:</span> {error}
          </div>
        )}

        {step === 'chat' && <ChatPersona key={sessionKey} onProfileReady={handleProfileReady} />}
        {step === 'summary' && persona && (
          <ProfileSummary
            persona={persona}
            summary={profileSummary}
            ticker={ticker}
            onConfirm={handleConfirmProfile}
            onEdit={handleEditProfile}
            loading={loading}
          />
        )}
        {step === 'analyzing' && <AnalyzingView ticker={ticker} />}
        {step === 'results' && result && <ResultsView result={result} onReset={handleReset} />}
      </main>

      {/* Footer */}
      <footer className="flex-shrink-0 border-t border-surface-light/20 py-4 text-center text-xs text-muted/50">
        MagiStock — Multi-Agent Investment Companion built on{' '}
        <a href="https://agentfield.ai" className="text-muted hover:text-white transition-colors">
          AgentField.ai
        </a>
      </footer>
    </div>
  );
}

function StepPill({ label, active, done }: { label: string; active: boolean; done: boolean }) {
  return (
    <span
      className={`px-2.5 py-1 rounded-full transition-all duration-300 ${
        active
          ? 'bg-judge/20 text-judge font-medium'
          : done
          ? 'bg-grass/10 text-grass'
          : 'bg-surface text-muted/50'
      }`}
    >
      {done && <span className="mr-1">&#10003;</span>}
      {label}
    </span>
  );
}

export default App;
