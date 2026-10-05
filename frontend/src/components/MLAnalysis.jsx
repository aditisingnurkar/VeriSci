import { Cpu } from 'lucide-react';
import { cn } from '../lib/utils';

export default function MLAnalysis({ evidenceList }) {
  return (
    <div className="bg-[#061813]/90 p-6 rounded-3xl border border-emerald-500/20 shadow-2xl backdrop-blur-xl w-full">
      <div className="flex items-center gap-2 mb-4 border-b border-emerald-900/40 pb-3.5">
        <Cpu className="w-4 h-4 text-cyan-400" />
        <h3 className="text-sm sm:text-base font-bold text-white font-display uppercase tracking-wider">
          Machine Learning Classification Stream
        </h3>
      </div>
      
      <p className="text-xs text-emerald-200/70 mb-4 font-sans">
        Cross-Encoder evaluated bidirectional entailment and contradiction scores for each scientific passage.
      </p>

      <div className="space-y-2.5 font-mono">
        {evidenceList.map((ev, idx) => (
          <div key={ev.id || idx} className="flex items-center justify-between p-3 rounded-xl bg-[#030d09]/80 border border-emerald-950 text-xs">
            <div className="flex items-center gap-2.5 truncate pr-4">
              <span className="text-cyan-400 font-bold">#{idx + 1}</span>
              <span className="text-emerald-100 font-sans truncate">{ev.title}</span>
            </div>
            
            <div className="flex items-center gap-2.5 shrink-0">
              <span className={cn(
                "px-2 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-wider text-center border",
                ev.prediction === 'SUPPORT' ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/40" :
                ev.prediction === 'CONTRADICT' ? "bg-rose-500/20 text-rose-300 border-rose-500/40" :
                "bg-emerald-950 text-emerald-400 border-emerald-900"
              )}>
                {ev.prediction}
              </span>
              <span className="text-emerald-300 w-10 text-right">{ev.confidence}%</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
