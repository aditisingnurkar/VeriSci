import { cn } from '../lib/utils';
import { ExternalLink, Database, Network } from 'lucide-react';

export default function EvidenceCard({ evidence, index }) {
  const { title, evidence_text, prediction, confidence, relevance_score, source } = evidence;

  const isSupport = prediction === 'SUPPORT';
  const isContradict = prediction === 'CONTRADICT';

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden flex flex-col sm:flex-row">
      
      {/* Evidence Source & Content */}
      <div className="p-6 sm:w-2/3 border-b sm:border-b-0 sm:border-r border-slate-100 flex flex-col justify-between">
        <div>
          <div className="flex items-center gap-3 mb-3">
            <span className="text-xs font-mono font-bold text-slate-400 bg-slate-100 px-2 py-1 rounded">
              #{index < 10 ? `0${index}` : index}
            </span>
            <div className="flex items-center text-xs text-slate-500 font-medium truncate">
              <Database className="w-3 h-3 mr-1 shrink-0" />
              <span className="truncate">{source || "SciFact"}</span>
            </div>
          </div>
          
          <h4 className="font-semibold text-slate-900 leading-snug mb-4">{title}</h4>
          
          <div className="bg-slate-50 border-l-4 border-slate-300 p-4 rounded-r-xl text-sm text-slate-700 italic mb-4">
            "{evidence_text}"
          </div>
        </div>
        
        <div className="flex items-center gap-4 text-xs mt-4 pt-4 border-t border-slate-100">
          <div className="flex flex-col">
            <span className="text-slate-500 font-medium">Relevance to claim</span>
            <span className="font-semibold text-slate-900">{(relevance_score * 100).toFixed(0)}%</span>
          </div>
        </div>
      </div>
      
      {/* ML Prediction Attached Directly to Evidence */}
      <div className={cn(
        "p-6 sm:w-1/3 flex flex-col justify-center",
        isSupport ? "bg-green-50/50" :
        isContradict ? "bg-red-50/50" : "bg-slate-50/50"
      )}>
        <div className="flex items-center gap-2 mb-4">
          <Network className="w-4 h-4 text-slate-400" />
          <h5 className="text-xs font-semibold uppercase tracking-widest text-slate-500">ML Assessment</h5>
        </div>
        
        <div className={cn(
          "inline-block px-3 py-1.5 rounded-md text-sm font-bold uppercase tracking-wide mb-3 border",
          isSupport ? "bg-green-100 text-green-800 border-green-200" :
          isContradict ? "bg-red-100 text-red-800 border-red-200" :
          "bg-slate-100 text-slate-700 border-slate-200"
        )}>
          {prediction === "SUPPORT" ? "SUPPORTS THE CLAIM" : 
           prediction === "CONTRADICT" ? "CONTRADICTS THE CLAIM" : "NEUTRAL TO CLAIM"}
        </div>
        
        <div className="flex flex-col">
          <span className="text-2xl font-bold text-slate-900">{(confidence * 100).toFixed(0)}%</span>
          <span className="text-xs font-medium text-slate-500">confidence</span>
        </div>
      </div>
      
    </div>
  );
}
