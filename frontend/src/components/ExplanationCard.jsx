import { useState, useEffect } from 'react';
import { BookOpen, AlertCircle, Loader2, Sparkles, ShieldAlert, FileSearch } from 'lucide-react';
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
      el.classList.add('ring-2', 'ring-teal-400', 'bg-teal-950/40');
      setTimeout(() => {
        el.classList.remove('ring-2', 'ring-teal-400', 'bg-teal-950/40');
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
            className="inline-flex items-center justify-center px-2 py-0.5 mx-1 rounded text-xs font-mono font-bold bg-teal-950/90 text-teal-300 border border-teal-500/40 hover:bg-teal-400 hover:text-slate-950 transition-all cursor-pointer shadow-sm"
            title={`Jump to referenced study [${match[1]}]`}
          >
            {match[1]}
          </button>
        );
      }
      return <span key={i}>{part}</span>;
    });
  };

  return (
    <div className="science-card p-6 sm:p-7 rounded-2xl w-full flex flex-col justify-between">
      <div>
        {/* Header Bar */}
        <div className="flex items-center justify-between gap-2 mb-4 border-b border-slate-800/80 pb-3">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-teal-400" />
            <h3 className="text-sm font-semibold text-white font-sans tracking-wide">
              Scientific Synthesis & Analysis
            </h3>
          </div>
          <span className="text-[11px] font-mono text-slate-400 bg-slate-900/80 px-2 py-0.5 rounded border border-slate-800">
            Strictly Grounded
          </span>
        </div>
        
        {loading && (
          <div className="flex items-center gap-3 text-slate-400 py-8 justify-center font-sans text-xs">
            <Loader2 className="w-4 h-4 animate-spin text-teal-400" />
            <span>Synthesizing evidence from retrieved literature...</span>
          </div>
        )}
        
        {error && !loading && (
          <div className="flex items-center gap-2 text-rose-400 py-4 font-sans text-xs">
            <AlertCircle className="w-4 h-4 text-rose-500 shrink-0" />
            <span>{error}</span>
          </div>
        )}
        
        {explanation && !loading && (
          <div className="space-y-4">
            <div className="text-slate-200 leading-relaxed text-xs sm:text-sm font-sans bg-slate-950/60 p-4 rounded-xl border border-slate-800/60">
              {renderTextWithCitations(explanation.explanation, explanation.citations)}
            </div>
            
            {explanation.limitations && explanation.limitations.length > 0 && (
              <div className="mt-4 pt-3.5 border-t border-slate-800/80">
                <div className="flex items-center gap-1.5 text-[11px] font-mono font-semibold uppercase tracking-wider text-amber-400/90 mb-2">
                  <ShieldAlert className="w-3.5 h-3.5" />
                  <span>Analytical Considerations & Caveats</span>
                </div>
                <ul className="list-disc list-inside text-xs text-slate-300/85 space-y-1 font-sans">
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

