import { useState, useRef, useEffect, useCallback } from 'react';
import type { ChatMessage, UserPersona } from '../types';
import { chatWithAdvisor } from '../api';

interface ChatPersonaProps {
  onProfileReady: (persona: UserPersona, summary: string, ticker: string, messages: ChatMessage[]) => void;
}

const GREETING: ChatMessage = {
  role: 'assistant',
  content:
    "Hi, I'm Magi — your investment advisor. Before we find the right strategy for you, I'd love to understand a bit about your goals. What are you looking to do with your investments?",
};

const SUGGESTIONS = [
  { icon: '👔', label: 'Young professional', prompt: "I'm a young professional in my 30s investing for the next 5-10 years. I want growth but don't want to lose sleep over volatility." },
  { icon: '🏖️', label: 'Planning for retirement', prompt: "I'm 15 years from retirement and want to build a nest egg. I prefer steady growth over risky bets." },
  { icon: '🎓', label: 'Recent grad with savings', prompt: "I just graduated and have some savings to invest. I have time on my side and I'm okay with risk if it means higher returns." },
  { icon: '👴', label: 'Retiree preserving wealth', prompt: "I'm retired and want to preserve my capital. Stability is more important to me than chasing returns." },
  { icon: '💼', label: 'Mid-career investor', prompt: "I'm in my 40s with a decent portfolio. Looking for balanced growth over the next 10+ years without extreme volatility." },
  { icon: '🚀', label: 'Aggressive growth seeker', prompt: "I have a high risk tolerance and want maximum growth potential. I can handle big swings for bigger rewards." },
];

export default function ChatPersona({ onProfileReady }: ChatPersonaProps) {
  const [started, setStarted] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [thinking, setThinking] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, thinking]);

  // Auto-focus input when chat is active
  useEffect(() => {
    if (started) inputRef.current?.focus();
  }, [started, thinking]);

  // Send a message (text) and get response from Magi
  const sendMessage = useCallback(
    async (text: string, history: ChatMessage[]) => {
      setError(null);
      const userMsg: ChatMessage = { role: 'user', content: text };
      const updatedMessages = [...history, userMsg];
      setMessages(updatedMessages);
      setThinking(true);

      try {
        const response = await chatWithAdvisor(updatedMessages);

      if (response.persona) {
        onProfileReady(
          {
            risk_tolerance: response.persona.risk_tolerance,
            time_horizon: response.persona.time_horizon,
            drawdown_sensitivity: response.persona.drawdown_sensitivity,
          },
          response.persona.summary,
          response.persona.ticker,
          updatedMessages,
        );
        } else if (response.message) {
          setMessages([...updatedMessages, { role: 'assistant', content: response.message }]);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to reach advisor');
      } finally {
        setThinking(false);
      }
    },
    [onProfileReady],
  );

  // Start the conversation — show greeting, then send the user's first message
  const startConversation = useCallback(
    (firstMessage: string) => {
      const initial = [GREETING];
      setMessages(initial);
      setStarted(true);

      // Small delay so greeting renders first, then send user message
      setTimeout(() => sendMessage(firstMessage, initial), 300);
    },
    [sendMessage],
  );

  const handleSend = async () => {
    const text = input.trim();
    if (!text || thinking) return;
    setInput('');

    if (!started) {
      startConversation(text);
    } else {
      sendMessage(text, messages);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Generate contextual quick replies based on Magi's last question
  const getQuickReplies = (): string[] | null => {
    if (thinking || messages.length === 0) return null;
    const lastMsg = messages[messages.length - 1];
    if (lastMsg.role !== 'assistant') return null;

    const content = lastMsg.content.toLowerCase();

    // Risk tolerance questions
    if (content.includes('dropped') || content.includes('20%') || content.includes('portfolio drop') || content.includes('lose') || content.includes('anxious')) {
      return [
        "I'd stay calm and hold",
        "I'd be nervous but wouldn't panic",
        "I'd want to sell immediately",
      ];
    }

    // Time horizon questions
    if (content.includes('how long') || content.includes('time horizon') || content.includes('when do you need')) {
      return [
        'Less than a year',
        '1-3 years',
        '5+ years',
      ];
    }

    // Stock ticker questions
    if (content.includes('which stock') || content.includes('what ticker') || content.includes('which company')) {
      return ['AAPL', 'TSLA', 'MSFT', 'SPY', 'NVDA'];
    }

    // Goal / risk appetite questions
    if (content.includes('what are you looking') || content.includes('investment goal') || content.includes('risk') || content.includes('aggressive')) {
      return [
        'Aggressive growth',
        'Balanced approach',
        'Capital preservation',
      ];
    }

    // Generic fallbacks for open questions
    if (content.includes('?')) {
      return ['Tell me more', "I'm not sure yet", 'Skip this question'];
    }

    return null;
  };

  const quickReplies = started && !thinking ? getQuickReplies() : null;

  // Simple markdown renderer for bold, italic, and line breaks
  const renderMarkdown = (text: string) => {
    const parts: React.ReactNode[] = [];
    let currentIndex = 0;
    let key = 0;

    // Regex to match **bold** or *italic*
    const markdownRegex = /(\*\*[^*]+\*\*|\*[^*]+\*)/g;
    let match;

    while ((match = markdownRegex.exec(text)) !== null) {
      // Add text before the match
      if (match.index > currentIndex) {
        parts.push(text.slice(currentIndex, match.index));
      }

      const matched = match[0];
      if (matched.startsWith('**') && matched.endsWith('**')) {
        // Bold
        parts.push(<strong key={key++}>{matched.slice(2, -2)}</strong>);
      } else if (matched.startsWith('*') && matched.endsWith('*')) {
        // Italic
        parts.push(<em key={key++}>{matched.slice(1, -1)}</em>);
      }

      currentIndex = match.index + matched.length;
    }

    // Add remaining text
    if (currentIndex < text.length) {
      parts.push(text.slice(currentIndex));
    }

    // Split by line breaks and add <br /> tags
    const withBreaks: React.ReactNode[] = [];
    parts.forEach((part, i) => {
      if (typeof part === 'string') {
        const lines = part.split('\n');
        lines.forEach((line, j) => {
          withBreaks.push(line);
          if (j < lines.length - 1) {
            withBreaks.push(<br key={`br-${i}-${j}`} />);
          }
        });
      } else {
        withBreaks.push(part);
      }
    });

    return <>{withBreaks}</>;
  };

  // ─── Welcome Screen ──────────────────────────────────────────
  if (!started) {
    return (
      <div className="max-w-2xl mx-auto flex flex-col items-center justify-center" style={{ minHeight: 'calc(100vh - 260px)' }}>
        {/* Hero */}
        <div className="text-center mb-10 fade-in-up">
          <div className="w-16 h-16 mx-auto mb-5 rounded-2xl bg-gradient-to-br from-judge/30 to-fire/20 border border-judge/20 flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="text-judge">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
            </svg>
          </div>
          <h2 className="text-3xl font-bold text-white mb-2">What brings you here today?</h2>
          <p className="text-muted text-sm max-w-md mx-auto leading-relaxed">
            Tell Magi about your investment goals. A short conversation will build your
            personalized investor profile.
          </p>
        </div>

        {/* Suggestion Bubbles */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full mb-8">
          {SUGGESTIONS.map((s, i) => (
            <button
              key={i}
              type="button"
              onClick={() => startConversation(s.prompt)}
              className="group flex items-center gap-3 text-left px-4 py-3.5 rounded-xl
                         bg-surface border border-surface-light
                         hover:border-judge/30 hover:bg-judge/5
                         transition-all duration-200 cursor-pointer fade-in-up"
              style={{ animationDelay: `${0.05 + i * 0.06}s` }}
            >
              <span className="text-xl flex-shrink-0">{s.icon}</span>
              <span className="text-sm text-slate-300 group-hover:text-white transition-colors">
                {s.label}
              </span>
            </button>
          ))}
        </div>

        {/* Or type your own */}
        <div className="w-full max-w-lg fade-in-up" style={{ animationDelay: '0.4s' }}>
          <div className="flex gap-2 items-end">
            <div className="flex-1 relative">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Or describe your investment goals in your own words..."
                rows={1}
                className="w-full bg-surface border-2 border-surface-light rounded-xl px-4 py-3 pr-12
                           text-white placeholder-muted/40 text-[15px] resize-none
                           focus:outline-none focus:border-judge/40 transition-colors"
                style={{ maxHeight: '120px' }}
              />
            </div>
            <button
              type="button"
              onClick={handleSend}
              disabled={!input.trim()}
              className="flex-shrink-0 w-11 h-11 rounded-xl bg-judge/20 text-judge flex items-center justify-center
                         hover:bg-judge/30 transition-all disabled:opacity-30 disabled:cursor-not-allowed cursor-pointer"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="22" y1="2" x2="11" y2="13" />
                <polygon points="22 2 15 22 11 13 2 9 22 2" />
              </svg>
            </button>
          </div>
          <p className="text-[10px] text-muted/40 mt-2 text-center">
            Press Enter to send
          </p>
        </div>
      </div>
    );
  }

  // ─── Chat Screen ─────────────────────────────────────────────
  return (
    <div className="max-w-xl mx-auto flex flex-col" style={{ height: 'calc(100vh - 220px)', minHeight: '500px' }}>
      {/* Header */}
      <div className="text-center mb-6 flex-shrink-0">
        <h2 className="text-2xl font-bold text-white mb-1">Chat with Magi</h2>
        <p className="text-muted text-sm">
          A short conversation to understand your investment style
        </p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 mb-4 px-1 scrollbar-thin">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} fade-in-up`}
            style={{ animationDelay: `${i * 0.05}s` }}
          >
            <div
              className={`max-w-[85%] rounded-2xl px-4 py-3 text-[15px] leading-relaxed ${
                msg.role === 'user'
                  ? 'bg-judge/20 text-white rounded-br-md'
                  : 'bg-surface border border-surface-light text-slate-200 rounded-bl-md'
              }`}
            >
              {msg.role === 'assistant' && (
                <div className="text-[10px] uppercase tracking-wider text-muted mb-1 font-semibold">Magi</div>
              )}
              {renderMarkdown(msg.content)}
            </div>
          </div>
        ))}

        {/* Thinking indicator */}
        {thinking && (
          <div className="flex justify-start fade-in-up">
            <div className="bg-surface border border-surface-light rounded-2xl rounded-bl-md px-4 py-3">
              <div className="text-[10px] uppercase tracking-wider text-muted mb-1 font-semibold">Magi</div>
              <div className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-judge/60 animate-bounce" style={{ animationDelay: '0ms' }} />
                <span className="w-2 h-2 rounded-full bg-judge/60 animate-bounce" style={{ animationDelay: '150ms' }} />
                <span className="w-2 h-2 rounded-full bg-judge/60 animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Error */}
      {error && (
        <div className="mb-3 p-3 rounded-lg bg-fire/10 border border-fire/30 text-fire-light text-xs flex-shrink-0">
          {error}
        </div>
      )}

      {/* Quick replies */}
      {quickReplies && quickReplies.length > 0 && (
        <div className="flex-shrink-0 mb-3">
          <div className="flex flex-wrap gap-2 px-1">
            {quickReplies.map((reply, i) => (
              <button
                key={i}
                type="button"
                onClick={() => {
                  setInput('');
                  sendMessage(reply, messages);
                }}
                disabled={thinking}
                className="px-4 py-2 rounded-full bg-surface border border-surface-light text-white text-sm
                           hover:bg-judge/10 hover:border-judge/30 transition-all cursor-pointer
                           disabled:opacity-50 disabled:cursor-not-allowed fade-in-up"
                style={{ animationDelay: `${i * 0.05}s` }}
              >
                {reply}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <div className="flex-shrink-0 relative">
        <div className="flex gap-2 items-end">
          <div className="flex-1 relative">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Type your response..."
              rows={1}
              disabled={thinking}
              className="w-full bg-surface border-2 border-surface-light rounded-xl px-4 py-3 pr-12
                         text-white placeholder-muted/40 text-[15px] resize-none
                         focus:outline-none focus:border-judge/40 transition-colors
                         disabled:opacity-50"
              style={{ maxHeight: '120px' }}
            />
          </div>
          <button
            type="button"
            onClick={handleSend}
            disabled={!input.trim() || thinking}
            className="flex-shrink-0 w-11 h-11 rounded-xl bg-judge/20 text-judge flex items-center justify-center
                       hover:bg-judge/30 transition-all disabled:opacity-30 disabled:cursor-not-allowed cursor-pointer"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="22" y1="2" x2="11" y2="13" />
              <polygon points="22 2 15 22 11 13 2 9 22 2" />
            </svg>
          </button>
        </div>
        <p className="text-[10px] text-muted/40 mt-2 text-center">
          Press Enter to send. Magi will ask 2-3 questions to understand your profile.
        </p>
      </div>
    </div>
  );
}
