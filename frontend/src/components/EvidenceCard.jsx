import { cn } from '../lib/utils';
import { ExternalLink, BookOpen, CheckCircle2, XCircle, MinusCircle, FileText } from 'lucide-react';

export default function EvidenceCard({ evidence, index }) {
  const { title, evidence_text, context_before, context_after, prediction, confidence, relevance_score, source, url, evidence_id } = evidence;

  const isSupport = prediction === 'SUPPORT';
  const isContradict = prediction === 'CONTRADICT';

  return (
    <div 
      id={`evidence-${evidence_id}`} 
      className="science-card rounded-2xl overflow-hidden flex flex-col md:flex-row transition-all duration-300"
    >
      
      {/* Paper Metadata & Context Excerpt */}
      <div className="p-6 md:w-8/12 border-b md:border-b-0 md:border-r border-slate-800/80 flex flex-col justify-between">
        <div>
          {/* Header Metadata Bar */}
          <div className="flex flex-wrap items-center gap-2 mb-3">
            <span className="text-xs font-mono font-bold text-teal-300 bg-teal-950/80 border border-teal-500/40 px-2.5 py-0.5 rounded-md">
              {evidence_id ? `[${evidence_id}]` : `#${index < 10 ? `0${index}` : index}`}
            </span>
            
            <div className="flex items-center text-xs font-mono text-slate-300 bg-slate-900/90 px-2.5 py-0.5 rounded-md border border-slate-800">
              <BookOpen className="w-3 h-3 mr-1.5 text-teal-400 shrink-0" />
              <span className="truncate">{source || "SciFact Corpus"}</span>
            </div>

            {url && (
              <a 
                href={url} 
                target="_blank" 
                rel="noopener noreferrer" 
                className="flex items-center text-xs font-mono text-teal-400 hover:text-teal-200 transition-colors ml-auto bg-slate-900/90 px-2.5 py-0.5 rounded-md border border-slate-800"
              >
                PubMed Study <ExternalLink className="w-3 h-3 ml-1" />
              </a>
            )}
          </div>
          
          {/* Paper Title */}
          <h4 className="font-serif font-medium text-white text-base sm:text-lg leading-snug mb-3.5">
            {title}
          </h4>
          
          {/* Highlighted Evidence Passage */}
          <div className="bg-slate-950/80 border-l-2 border-teal-400 p-3.5 rounded-r-xl text-xs sm:text-sm text-slate-200 leading-relaxed font-sans mb-3 shadow-inner">
            {context_before && <span className="text-slate-400 mr-1 font-mono text-xs">{context_before} </span>}
            <span className="font-semibold text-white bg-teal-950/60 px-1 py-0.5 rounded">{evidence_text}</span>
            {context_after && <span className="text-slate-400 ml-1 font-mono text-xs"> {context_after}</span>}
          </div>
        </div>
        
        {/* Footer Metrics */}
        <div className="flex items-center justify-between text-xs font-mono mt-2 pt-2.5 border-t border-slate-800/80 text-slate-400">
          <div className="flex items-center gap-2">
            <span>Relevance Match:</span>
            <span className="font-bold text-slate-200">{(relevance_score * 100).toFixed(1)}%</span>
          </div>
          <div className="w-24 bg-slate-950 h-1.5 rounded-full overflow-hidden border border-slate-800">
            <div 
              className="bg-gradient-to-r from-teal-400 to-emerald-400 h-full rounded-full" 
              style={{ width: `${Math.min(100, Math.max(10, relevance_score * 100))}%` }}
            />
          </div>
        </div>
      </div>
      
      {/* ML Classification Diagnosis Pod */}
      <div className={cn(
        "p-6 md:w-4/12 flex flex-col justify-center items-start md:items-center text-left md:text-center relative overflow-hidden",
        isSupport ? "bg-emerald-950/30 border-t md:border-t-0 md:border-l border-emerald-500/20" :
        isContradict ? "bg-rose-950/30 border-t md:border-t-0 md:border-l border-rose-500/20" : 
        "bg-slate-950/40 border-t md:border-t-0 md:border-l border-slate-800/50"
      )}>
        
        <div className="flex items-center gap-1.5 mb-2.5 font-mono text-[11px] uppercase tracking-wider text-slate-400">
          <FileText className="w-3.5 h-3.5 text-teal-400" />
          <span>NLI Stance</span>
        </div>
        
        {/* Stance Badge */}
        <div className={cn(
          "inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-mono font-bold tracking-wide mb-3 border shadow-sm",
          isSupport ? "bg-emerald-950/90 text-emerald-300 border-emerald-400/40" :
          isContradict ? "bg-rose-950/90 text-rose-300 border-rose-500/40" :
          "bg-slate-900 text-slate-300 border-slate-700"
        )}>
          {isSupport ? <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> :
           isContradict ? <XCircle className="w-3.5 h-3.5 text-rose-400" /> :
           <MinusCircle className="w-3.5 h-3.5 text-slate-400" />}
          
          <span>
            {prediction === "SUPPORT" ? "Supports Claim" : 
             prediction === "CONTRADICT" ? "Refutes Claim" : "Neutral / Insufficient"}
          </span>
        </div>
        
        {/* Confidence Percentage */}
        <div className="flex flex-col items-start md:items-center">
          <span className="text-3xl font-extrabold text-white font-mono tracking-tight">
            {(confidence * 100).toFixed(0)}%
          </span>
          <span className="text-[10px] font-mono uppercase tracking-widest text-slate-400 mt-0.5">
            Model Confidence
          </span>
        </div>
      </div>
      
    </div>
  );
}

