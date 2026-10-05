import { Network } from 'lucide-react';
import { cn } from '../lib/utils';

export default function MLAnalysis({ evidenceList }) {
  return (
    <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm w-full">
      <div className="flex items-center gap-2 mb-4 border-b border-slate-100 pb-4">
        <Network className="w-5 h-5 text-blue-600" />
        <h3 className="text-lg font-semibold text-slate-900">Machine Learning Analysis</h3>
      </div>
      
      <p className="text-sm text-slate-600 mb-6">
        The model evaluates the relationship between your claim and each retrieved scientific evidence passage independently before aggregating the final verdict.
      </p>

      <div className="space-y-3">
        {evidenceList.map((ev, idx) => (
          <div key={ev.id} className="flex items-center justify-between p-3 rounded-lg bg-slate-50 border border-slate-100 text-sm">
            <div className="flex items-center gap-3 truncate pr-4">
              <span className="text-slate-400 font-mono text-xs">#{idx + 1}</span>
              <span className="text-slate-800 font-medium truncate">{ev.title}</span>
            </div>
            
            <div className="flex items-center gap-3 shrink-0">
              <span className={cn(
                "px-2 py-0.5 rounded text-xs font-bold w-24 text-center",
                ev.prediction === 'SUPPORT' ? "bg-green-100 text-green-700" :
                ev.prediction === 'CONTRADICT' ? "bg-red-100 text-red-700" :
                "bg-slate-200 text-slate-700"
              )}>
                {ev.prediction}
              </span>
              <span className="font-mono text-slate-600 w-10 text-right">{ev.confidence}%</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
