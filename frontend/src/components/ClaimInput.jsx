import { useState } from 'react';
import { Search, Sparkles, Terminal } from 'lucide-react';
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
        {/* Exterior Neon Halo */}
        <div className="absolute -inset-1 bg-gradient-to-r from-emerald-500/30 via-cyan-400/30 to-emerald-500/30 rounded-3xl blur-md opacity-40 group-hover:opacity-75 transition-all duration-500 pointer-events-none" />
        
        {/* Core Input Console */}
        <div className="relative rounded-2xl border border-emerald-500/25 bg-[#061813]/90 shadow-2xl backdrop-blur-xl focus-within:border-cyan-400 focus-within:ring-2 focus-within:ring-cyan-400/30 transition-all overflow-hidden">
          
          {/* Header Strip */}
          <div className="flex items-center justify-between px-5 py-2.5 bg-[#040e0b]/80 border-b border-emerald-900/40 text-[11px] font-mono text-emerald-400/70">
            <div className="flex items-center gap-2">
              <Terminal className="w-3.5 h-3.5 text-cyan-400" />
              <span className="uppercase tracking-wider">TARGET_CLAIM_INPUT // PROMPT_STREAM</span>
            </div>
            <div className="flex items-center gap-1.5 text-emerald-400/50">
              <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse" />
              <span>ENGINES_ONLINE</span>
            </div>
          </div>

          <textarea
            id="claim-input"
            rows={4}
            className="block w-full resize-none border-0 py-4 px-6 bg-transparent text-[#E6FFF8] placeholder:text-emerald-300/30 focus:ring-0 text-base sm:text-lg sm:leading-relaxed font-sans focus:outline-none"
            placeholder="Enter a scientific or medical claim to verify (e.g. 'Vaccines cause infertility' or molecular hypotheses)..."
            value={claim}
            onChange={(e) => setClaim(e.target.value)}
          />

          <div className="flex flex-col sm:flex-row items-center justify-between gap-3 border-t border-emerald-900/40 bg-[#040e0b]/60 px-5 py-3.5">
            <span className="text-xs text-emerald-300/60 font-mono flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
              Verified across 5.1k+ SciFact & Live PubMed indexed papers
            </span>

            <button
              type="submit"
              disabled={!claim.trim()}
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-emerald-500 to-cyan-400 px-7 py-3 text-sm font-bold uppercase tracking-wider text-[#02140e] shadow-lg shadow-cyan-500/20 hover:shadow-cyan-400/40 hover:scale-[1.02] active:scale-[0.98] focus-visible:outline-none disabled:opacity-40 disabled:scale-100 disabled:cursor-not-allowed transition-all cursor-pointer font-display"
            >
              <Search className="w-4 h-4 stroke-[2.5]" />
              Verify Claim
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}
