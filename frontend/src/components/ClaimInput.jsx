import { useState } from 'react';
import { Search, Sparkles, ArrowRight, BookCheck } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function ClaimInput({ initialClaim = "", onExampleClick }) {
  const [claim, setClaim] = useState(initialClaim);
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!claim.trim()) return;
    navigate('/analyze', { state: { claim } });
  };

  if (initialClaim !== claim && document.activeElement !== document.getElementById('claim-input') && initialClaim) {
     setClaim(initialClaim);
  }

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
            className="block w-full resize-none border-0 py-4 px-5 sm:px-6 bg-transparent text-slate-100 placeholder:text-slate-500 focus:ring-0 text-base sm:text-lg sm:leading-relaxed font-sans focus:outline-none"
            placeholder="Enter a scientific, biomedical, or clinical claim (e.g., 'Metformin reduces all-cause mortality in diabetic cohorts' or 'Autophagy promotes cell survival')..."
            value={claim}
            onChange={(e) => setClaim(e.target.value)}
          />

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

