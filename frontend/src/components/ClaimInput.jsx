import { useState, useEffect, useRef } from 'react';
import { Search, Sparkles, ArrowRight, BookCheck, Check, X } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function ClaimInput({ initialClaim = "", onExampleClick }) {
  const [claim, setClaim] = useState(initialClaim);
  const [suggestion, setSuggestion] = useState(null);
  const [dismissed, setDismissed] = useState(false);
  const debounceTimer = useRef(null);
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!claim.trim()) return;
    navigate('/analyze', { state: { claim } });
  };

  if (initialClaim !== claim && document.activeElement !== document.getElementById('claim-input') && initialClaim) {
     setClaim(initialClaim);
  }

  // Debounced spell check call to backend
  useEffect(() => {
    if (debounceTimer.current) {
      clearTimeout(debounceTimer.current);
    }

    const trimmed = claim.trim();
    if (trimmed.length < 5) {
      setSuggestion(null);
      return;
    }

    debounceTimer.current = setTimeout(async () => {
      try {
        const res = await fetch('/api/spellcheck', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ claim: trimmed }),
        });
        if (res.ok) {
          const data = await res.json();
          if (data.has_suggestion && data.suggested_claim && data.suggested_claim.toLowerCase() !== trimmed.toLowerCase()) {
            setSuggestion(data.suggested_claim);
            setDismissed(false);
          } else {
            setSuggestion(null);
          }
        }
      } catch (err) {
        // Gracefully ignore network/offline errors for spellcheck
      }
    }, 450);

    return () => {
      if (debounceTimer.current) clearTimeout(debounceTimer.current);
    };
  }, [claim]);

  const handleApplySuggestion = () => {
    if (suggestion) {
      setClaim(suggestion);
      setSuggestion(null);
      setDismissed(true);
    }
  };

  return (
    <div className="w-full max-w-3xl mx-auto">
      <form onSubmit={handleSubmit} className="relative group">
        {/* Exterior Subtle Accent Glow */}
        <div className="absolute -inset-1 bg-gradient-to-r from-teal-500/20 via-sky-500/15 to-emerald-500/20 rounded-3xl blur-xl opacity-50 group-hover:opacity-80 transition-all duration-500 pointer-events-none" />
        
        {/* Core Input Console */}
        <div className="relative rounded-2xl border border-slate-700/60 bg-[#0b131b]/85 shadow-2xl backdrop-blur-2xl focus-within:border-teal-400/80 focus-within:ring-2 focus-within:ring-teal-400/20 transition-all overflow-hidden">
          
          {/* Header Strip */}
          <div className="flex items-center justify-between px-5 py-3 bg-[#080e14]/90 border-b border-slate-800/80 text-xs font-mono text-slate-400">
            <div className="flex items-center gap-2">
              <BookCheck className="w-3.5 h-3.5 text-teal-400" />
              <span className="font-semibold text-slate-300">HYPOTHESIS / SCIENTIFIC CLAIM</span>
            </div>
            <div className="flex items-center gap-2 text-[11px] text-slate-400">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
              <span>Dual-Retrieval Active</span>
            </div>
          </div>

          <textarea
            id="claim-input"
            rows={4}
            spellCheck={true}
            autoCorrect="off"
            autoCapitalize="sentences"
            className="block w-full resize-none border-0 py-4 px-5 sm:px-6 bg-transparent text-slate-100 placeholder:text-slate-500 focus:ring-0 text-base sm:text-lg sm:leading-relaxed font-sans focus:outline-none"
            placeholder="Enter a scientific, biomedical, or clinical claim (e.g., 'Metformin reduces all-cause mortality in diabetic cohorts' or 'Autophagy promotes cell survival')..."
            value={claim}
            onChange={(e) => setClaim(e.target.value)}
          />

          {/* Interactive Spelling Suggestion Strip */}
          {suggestion && !dismissed && (
            <div className="flex items-center justify-between gap-3 px-5 py-2.5 bg-teal-950/40 border-t border-teal-500/25 text-xs font-sans text-teal-200">
              <div className="flex items-center gap-2 min-w-0">
                <Sparkles className="w-3.5 h-3.5 text-teal-400 shrink-0" />
                <span className="truncate">
                  Did you mean: <button type="button" onClick={handleApplySuggestion} className="font-semibold text-teal-300 hover:text-white underline decoration-dotted text-left cursor-pointer">{suggestion}</button>?
                </span>
              </div>
              <div className="flex items-center gap-1.5 shrink-0">
                <button
                  type="button"
                  onClick={handleApplySuggestion}
                  className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md bg-teal-500/25 hover:bg-teal-500/35 text-teal-200 hover:text-white font-medium text-[11px] transition-colors cursor-pointer"
                  title="Apply correction"
                >
                  <Check className="w-3 h-3" />
                  <span>Apply</span>
                </button>
                <button
                  type="button"
                  onClick={() => setDismissed(true)}
                  className="inline-flex items-center gap-0.5 px-2 py-1 rounded-md text-slate-400 hover:text-slate-200 hover:bg-slate-800 text-[11px] transition-colors cursor-pointer"
                  title="Dismiss suggestion"
                >
                  <X className="w-3 h-3" />
                  <span>Dismiss</span>
                </button>
              </div>
            </div>
          )}

          <div className="flex flex-col sm:flex-row items-center justify-between gap-3 border-t border-slate-800/80 bg-[#080e14]/80 px-5 py-3.5">
            <span className="text-xs text-slate-400 font-sans flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-teal-400 shrink-0" />
              <span>Cross-referenced against <strong>5,183+ SciFact papers</strong> and <strong>PubMed Live</strong></span>
            </span>

            <button
              type="submit"
              disabled={!claim.trim()}
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-teal-400 to-emerald-400 px-6 py-2.5 text-sm font-bold text-slate-950 shadow-md shadow-teal-500/20 hover:brightness-105 active:scale-[0.98] focus-visible:outline-none disabled:opacity-30 disabled:scale-100 disabled:cursor-not-allowed transition-all cursor-pointer font-sans"
            >
              <Search className="w-4 h-4 stroke-[2.5]" />
              <span>Verify Claim</span>
              <ArrowRight className="w-3.5 h-3.5 stroke-[2.5] hidden sm:inline" />
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}


