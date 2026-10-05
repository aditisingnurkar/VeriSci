import { BarChart3 } from 'lucide-react';

export default function EvidenceSummary({ supporting, contradicting, neutral }) {
  const total = supporting + contradicting + neutral;

  return (
    <div className="bg-[#061813]/90 p-6 rounded-3xl border border-emerald-500/20 shadow-2xl backdrop-blur-xl w-full">
      <div className="flex items-center gap-2 mb-5 border-b border-emerald-900/40 pb-3.5">
        <BarChart3 className="w-4 h-4 text-cyan-400" />
        <h3 className="text-sm sm:text-base font-bold text-white font-display uppercase tracking-wider">
          Evidence Passage Aggregation
        </h3>
      </div>
      
      <div className="grid grid-cols-3 gap-3 font-mono">
        <div className="flex flex-col items-center p-3.5 bg-[#042018]/90 rounded-2xl border border-emerald-500/30">
          <span className="text-2xl sm:text-3xl font-extrabold text-emerald-300">{supporting}</span>
          <span className="text-[10px] font-bold text-emerald-400 uppercase tracking-wider mt-1">Supports</span>
        </div>
        
        <div className="flex flex-col items-center p-3.5 bg-[#25080e]/90 rounded-2xl border border-rose-500/30">
          <span className="text-2xl sm:text-3xl font-extrabold text-rose-300">{contradicting}</span>
          <span className="text-[10px] font-bold text-rose-400 uppercase tracking-wider mt-1">Contradicts</span>
        </div>

        <div className="flex flex-col items-center p-3.5 bg-[#071914]/90 rounded-2xl border border-emerald-900/40">
          <span className="text-2xl sm:text-3xl font-extrabold text-emerald-100">{neutral}</span>
          <span className="text-[10px] font-bold text-emerald-400/70 uppercase tracking-wider mt-1">Neutral</span>
        </div>
      </div>

      <div className="mt-4 text-xs font-mono text-center text-emerald-400/60">
        Analyzed <span className="font-bold text-cyan-300">{total}</span> total scientific passages.
      </div>
    </div>
  );
}
