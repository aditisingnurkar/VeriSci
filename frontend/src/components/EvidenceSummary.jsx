import { BarChart3 } from 'lucide-react';

export default function EvidenceSummary({ supporting, contradicting, neutral }) {
  const total = supporting + contradicting + neutral;

  return (
    <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm w-full">
      <div className="flex items-center gap-2 mb-6 border-b border-slate-100 pb-4">
        <BarChart3 className="w-5 h-5 text-slate-500" />
        <h3 className="text-lg font-semibold text-slate-900">Evidence Summary</h3>
      </div>
      
      <div className="flex items-center justify-between gap-4">
        <div className="flex-1 flex flex-col items-center p-4 bg-green-50 rounded-xl border border-green-100">
          <span className="text-3xl font-bold text-green-700">{supporting}</span>
          <span className="text-xs font-semibold text-green-800 uppercase tracking-wide mt-1">Supports</span>
        </div>
        
        <div className="flex-1 flex flex-col items-center p-4 bg-red-50 rounded-xl border border-red-100">
          <span className="text-3xl font-bold text-red-700">{contradicting}</span>
          <span className="text-xs font-semibold text-red-800 uppercase tracking-wide mt-1">Contradicts</span>
        </div>

        <div className="flex-1 flex flex-col items-center p-4 bg-slate-50 rounded-xl border border-slate-200">
          <span className="text-3xl font-bold text-slate-700">{neutral}</span>
          <span className="text-xs font-semibold text-slate-600 uppercase tracking-wide mt-1">Neutral</span>
        </div>
      </div>

      <div className="mt-6 text-sm text-center text-slate-500">
        Analyzed <span className="font-semibold text-slate-700">{total}</span> total scientific passages.
      </div>
    </div>
  );
}
