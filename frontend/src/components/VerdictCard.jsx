import { cn } from '../lib/utils';
import { AlertCircle, AlertTriangle, CheckCircle, Info } from 'lucide-react';

export default function VerdictCard({ verdict, confidence, claim }) {
  let colorClass = "from-slate-800 to-slate-900 text-white";
  let badgeClass = "bg-slate-700/50 text-slate-100 border border-slate-600";
  let Icon = Info;

  if (verdict.includes("SUPPORTED")) {
    colorClass = "from-emerald-600 to-teal-800 text-white";
    badgeClass = "bg-emerald-500/30 text-emerald-50 border border-emerald-400/30";
    Icon = CheckCircle;
  } else if (verdict.includes("CONTRADICTED")) {
    colorClass = "from-rose-600 to-red-800 text-white";
    badgeClass = "bg-rose-500/30 text-rose-50 border border-rose-400/30";
    Icon = AlertCircle;
  } else if (verdict.includes("INCONCLUSIVE")) {
    colorClass = "from-amber-500 to-orange-700 text-white";
    badgeClass = "bg-amber-500/30 text-amber-50 border border-amber-400/30";
    Icon = AlertTriangle;
  }

  return (
    <div className={cn("rounded-3xl shadow-xl bg-gradient-to-br relative overflow-hidden", colorClass)}>
      {/* Background large icon for aesthetics */}
      <div className="absolute top-0 right-0 -mt-16 -mr-16 opacity-10 pointer-events-none mix-blend-overlay">
        <Icon className="w-96 h-96" />
      </div>
      
      <div className="p-8 sm:p-12 relative z-10 flex flex-col justify-between h-full min-h-[320px]">
        <div>
          <div className="flex items-center gap-3 mb-8">
            <div className={cn("px-4 py-1.5 rounded-full text-sm font-bold uppercase tracking-widest flex items-center gap-2 shadow-sm", badgeClass)}>
              <Icon className="w-5 h-5" />
              Final Verdict
            </div>
          </div>
          
          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold leading-tight tracking-tight max-w-4xl">
            <span className="opacity-80 font-medium">The claim </span>
            <span className="italic leading-snug">"{claim}"</span>
            <span className="opacity-80 font-medium"> is </span>
            <span className="underline decoration-4 underline-offset-8 drop-shadow-sm">{verdict}</span>
          </h1>
        </div>
        
        <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-6 mt-12 pt-8 border-t border-white/20">
          <div className="flex flex-col">
            <span className="text-sm font-semibold uppercase tracking-widest opacity-80 mb-1">Model Confidence</span>
            <div className="flex items-baseline gap-1">
              <span className="text-6xl font-black drop-shadow-sm">{confidence}</span>
              <span className="text-3xl font-bold opacity-80">%</span>
            </div>
          </div>
          
          <div className="text-sm opacity-80 max-w-xs text-left sm:text-right">
            Calculated by analyzing ML predictions across multiple retrieved scientific papers.
          </div>
        </div>
      </div>
    </div>
  );
}
