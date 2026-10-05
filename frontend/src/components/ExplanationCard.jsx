import { useState, useEffect } from 'react';
import { BookOpen, AlertCircle, Loader2, Cpu, Sparkles, ShieldAlert } from 'lucide-react';
import { cn } from '../lib/utils';

export default function ExplanationCard({ verificationId }) {
  const [explanation, setExplanation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!verificationId) return;
    
    const fetchExplanation = async () => {
      setLoading(true);
      setError(null);
      try {
        const apiUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
        const response = await fetch(`${apiUrl}/api/explain`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ verification_id: verificationId }),
        });
        
        if (!response.ok) {
          throw new Error('Failed to load explanation');
        }
        
        const data = await response.json();
        setExplanation(data);
      } catch (err) {
        console.error(err);
        setError("Evidence explanation synthesis offline.");
      } finally {
        setLoading(false);
      }
    };
    
    fetchExplanation();
  }, [verificationId]);

  const highlightEvidence = (cid) => {
    const el = document.getElementById(`evidence-${cid}`);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'center' });
      el.classList.add('ring-2', 'ring-cyan-400', 'bg-[#0e352a]');
      setTimeout(() => {
        el.classList.remove('ring-2', 'ring-cyan-400', 'bg-[#0e352a]');
      }, 2500);
    }
  };

  const renderTextWithCitations = (text, citations) => {
    if (!text) return null;
    
    // Split by [E#]
    const parts = text.split(/(\[E\d+\])/g);
    return parts.map((part, i) => {
      const match = part.match(/^\[(E\d+)\]$/);
      if (match && citations?.includes(match[1])) {
        return (
          <button 
            key={i} 
            onClick={() => highlightEvidence(match[1])}
            className="inline-flex items-center justify-center px-2 py-0.5 mx-1 rounded-md text-xs font-mono font-bold bg-cyan-950/90 text-cyan-300 border border-cyan-400/40 hover:bg-cyan-400 hover:text-[#02140e] hover:border-cyan-300 transition-all cursor-pointer shadow-sm shadow-cyan-950/40"
            title={`Jump to Citation [${match[1]}]`}
          >
            {match[1]}
          </button>
        );
      }
      return <span key={i}>{part}</span>;
    });
  };

  return (
    <div className="bg-[#061813]/90 text-[#E6FFF8] p-6 sm:p-7 rounded-3xl border border-emerald-500/20 shadow-2xl backdrop-blur-xl w-full relative overflow-hidden flex flex-col justify-between">
      {/* Ambient background glow */}
      <div className="absolute top-0 right-0 w-48 h-48 bg-cyan-500/5 rounded-full blur-3xl pointer-events-none" />

      <div className="relative z-10">
        {/* Header HUD Bar */}
        <div className="flex items-center justify-between gap-2 mb-5 border-b border-emerald-900/40 pb-3.5">
          <div className="flex items-center gap-2">
            <Cpu className="w-4 h-4 text-cyan-400" />
            <h3 className="text-sm sm:text-base font-bold text-white font-display uppercase tracking-wider">
              Neural Synthesis & Analysis
            </h3>
          </div>
          <div className="flex items-center gap-1 text-[10px] font-mono text-emerald-400/70">
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse" />
            <span>GROUNDED_CITATIONS</span>
          </div>
        </div>
        
        {loading && (
          <div className="flex items-center gap-3 text-emerald-400/80 py-8 justify-center font-mono text-xs">
            <Loader2 className="w-4 h-4 animate-spin text-cyan-400" />
            <span>Synthesizing scientific literature explanation...</span>
          </div>
        )}
        
        {error && !loading && (
          <div className="flex items-center gap-2 text-rose-400 py-4 font-mono text-xs">
            <AlertCircle className="w-4 h-4 text-rose-500" />
            <span>{error}</span>
          </div>
        )}
        
        {explanation && !loading && (
          <div className="space-y-4">
            <div className="text-emerald-100/90 leading-relaxed text-xs sm:text-sm font-sans bg-[#030d09]/60 p-4 rounded-xl border border-emerald-900/30">
              {renderTextWithCitations(explanation.explanation, explanation.citations)}
            </div>
            
            {explanation.limitations && explanation.limitations.length > 0 && (
              <div className="mt-4 pt-3.5 border-t border-emerald-950/80">
                <div className="flex items-center gap-1.5 text-[11px] font-mono font-semibold uppercase tracking-wider text-amber-400/90 mb-2">
                  <ShieldAlert className="w-3.5 h-3.5" />
                  <span>Analytical Considerations & Caveats</span>
                </div>
                <ul className="list-disc list-inside text-xs text-emerald-300/70 space-y-1 font-sans">
                  {explanation.limitations.map((lim, i) => (
                    <li key={i}>{lim}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
