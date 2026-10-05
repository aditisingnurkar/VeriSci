import { cn } from '../lib/utils';
import { ExternalLink, Database, Cpu, FileText, CheckCircle2, XCircle, MinusCircle } from 'lucide-react';

export default function EvidenceCard({ evidence, index }) {
  const { title, evidence_text, context_before, context_after, prediction, confidence, relevance_score, source, url, evidence_id } = evidence;

  const isSupport = prediction === 'SUPPORT';
  const isContradict = prediction === 'CONTRADICT';

  return (
    <div 
      id={`evidence-${evidence_id}`} 
      className="tech-card rounded-3xl border border-emerald-500/20 shadow-xl overflow-hidden flex flex-col md:flex-row transition-all duration-300 hover:border-cyan-400/40"
    >
      
      {/* Evidence Source & Content */}
      <div className="p-6 md:w-8/12 border-b md:border-b-0 md:border-r border-emerald-900/40 flex flex-col justify-between bg-[#061813]/90">
        <div>
          {/* Header Metadata Bar */}
          <div className="flex flex-wrap items-center gap-2.5 mb-3.5">
            <span className="text-xs font-mono font-bold text-cyan-300 bg-cyan-950/80 border border-cyan-500/40 px-2.5 py-1 rounded-md">
              {evidence_id ? `[${evidence_id}]` : `#${index < 10 ? `0${index}` : index}`}
            </span>
            
            <div className="flex items-center text-xs font-mono text-emerald-400/80 bg-[#040f0c] px-2.5 py-1 rounded-md border border-emerald-950">
              <Database className="w-3 h-3 mr-1.5 text-cyan-400 shrink-0" />
              <span className="truncate">{source || "SciFact Corpus"}</span>
            </div>

            {url && (
              <a 
                href={url} 
                target="_blank" 
                rel="noopener noreferrer" 
                className="flex items-center text-xs font-mono text-cyan-400 hover:text-cyan-200 transition-colors ml-auto bg-[#040f0c] px-2.5 py-1 rounded-md border border-cyan-950/60"
              >
                PubMed Article <ExternalLink className="w-3 h-3 ml-1" />
              </a>
            )}
          </div>
          
          {/* Paper Title */}
          <h4 className="font-semibold text-[#F0FDF9] text-base sm:text-lg leading-snug mb-4 font-sans">
            {title}
          </h4>
          
          {/* Highlighted Evidence Snippet */}
          <div className="bg-[#030d09]/90 border-l-2 border-cyan-400 p-4 rounded-r-xl text-xs sm:text-sm text-emerald-100/90 leading-relaxed font-sans mb-4 shadow-inner">
            {context_before && <span className="text-emerald-500/60 mr-1 font-mono text-xs">{context_before} </span>}
            <span className="font-medium text-white bg-cyan-950/40 px-1 py-0.5 rounded">{evidence_text}</span>
            {context_after && <span className="text-emerald-500/60 ml-1 font-mono text-xs"> {context_after}</span>}
          </div>
        </div>
        
        {/* Footer Metrics */}
        <div className="flex items-center justify-between text-xs font-mono mt-2 pt-3 border-t border-emerald-950/60 text-emerald-400/70">
          <div className="flex items-center gap-2">
            <span className="text-emerald-500">Relevance Match:</span>
            <span className="font-bold text-white">{(relevance_score * 100).toFixed(1)}%</span>
          </div>
          <div className="w-24 bg-[#030d09] h-1.5 rounded-full overflow-hidden border border-emerald-950">
            <div 
              className="bg-gradient-to-r from-emerald-500 to-cyan-400 h-full rounded-full" 
              style={{ width: `${Math.min(100, Math.max(10, relevance_score * 100))}%` }}
            />
          </div>
        </div>
      </div>
      
      {/* ML Classification Diagnosis Pod */}
      <div className={cn(
        "p-6 md:w-4/12 flex flex-col justify-center items-start md:items-center text-left md:text-center relative overflow-hidden",
        isSupport ? "bg-[#042018]/90 border-t md:border-t-0 md:border-l border-emerald-500/30" :
        isContradict ? "bg-[#24080e]/90 border-t md:border-t-0 md:border-l border-rose-500/30" : 
        "bg-[#071914]/90 border-t md:border-t-0 md:border-l border-emerald-900/30"
      )}>
        
        <div className="flex items-center gap-1.5 mb-3 font-mono text-[10px] uppercase tracking-wider text-emerald-400/60">
          <Cpu className="w-3.5 h-3.5 text-cyan-400" />
          <span>NLI Inference</span>
        </div>
        
        {/* Verdict Badge */}
        <div className={cn(
          "inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-mono font-bold uppercase tracking-wider mb-4 border shadow-sm",
          isSupport ? "bg-emerald-500/20 text-emerald-300 border-emerald-400/50" :
          isContradict ? "bg-rose-500/20 text-rose-300 border-rose-500/50" :
          "bg-emerald-950/60 text-emerald-300 border-emerald-800/40"
        )}>
          {isSupport ? <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> :
           isContradict ? <XCircle className="w-3.5 h-3.5 text-rose-400" /> :
           <MinusCircle className="w-3.5 h-3.5 text-emerald-400" />}
          
          <span>
            {prediction === "SUPPORT" ? "Supports Claim" : 
             prediction === "CONTRADICT" ? "Contradicts Claim" : "Neutral / Insufficient"}
          </span>
        </div>
        
        {/* Confidence Percentage */}
        <div className="flex flex-col items-start md:items-center">
          <span className="text-3xl sm:text-4xl font-extrabold text-white font-mono tracking-tight">
            {(confidence * 100).toFixed(0)}%
          </span>
          <span className="text-[10px] font-mono uppercase tracking-widest text-emerald-400/60 mt-0.5">
            Model Confidence
          </span>
        </div>
      </div>
      
    </div>
  );
}
