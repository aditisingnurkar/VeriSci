import { useLocation, Navigate, Link } from 'react-router-dom';
import EvidenceCard from '../components/EvidenceCard';
import VerdictCard from '../components/VerdictCard';
import ExplanationCard from '../components/ExplanationCard';
import ClaimChat from '../components/ClaimChat';
import { ArrowLeft, FileText, CheckCircle2, XCircle, MinusCircle, Layers, Cpu, Database } from 'lucide-react';

export default function Results() {
  const location = useLocation();
  const data = location.state;

  if (!data || !data.claim) {
    return <Navigate to="/" replace />;
  }

  const { claim, verdict, strength, reason, counts, evidence, model, verification_id, sources_used } = data;

  return (
    <main className="flex-grow py-10 px-4 sm:px-6 lg:px-8 bg-grid-pattern relative overflow-hidden">
      {/* Background ambient lighting */}
      <div className="absolute top-20 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-emerald-500/5 rounded-full blur-[150px] pointer-events-none -z-10" />

      <div className="max-w-5xl mx-auto space-y-10">
        
        {/* Navigation & Main Verdict */}
        <div>
          <Link 
            to="/" 
            className="inline-flex items-center text-xs font-mono font-medium text-emerald-400 hover:text-cyan-300 mb-6 transition-colors group"
          >
            <ArrowLeft className="w-3.5 h-3.5 mr-1.5 group-hover:-translate-x-1 transition-transform" />
            &lt; RETURN // VERIFY_ANOTHER_CLAIM
          </Link>
          
          <VerdictCard 
            verdict={verdict} 
            claim={claim} 
            strength={strength} 
            reason={reason} 
          />
        </div>

        {/* AI Explanation and Neural Chat */}
        {verification_id && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <ExplanationCard verificationId={verification_id} />
            <ClaimChat verificationId={verification_id} verdict={verdict} />
          </div>
        )}

        {/* Evidence Breakdown Telemetry Strip */}
        {counts?.papers > 0 && (
          <section className="p-6 rounded-3xl border border-emerald-500/20 bg-[#061813]/90 shadow-xl backdrop-blur-xl flex flex-col sm:flex-row gap-6 justify-between items-start sm:items-center">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <Layers className="w-4 h-4 text-cyan-400" />
                <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-emerald-300">
                  Evidence Breakdown & Distribution
                </h3>
              </div>
              <p className="text-xs sm:text-sm text-emerald-100/70 font-sans">
                Evaluated <span className="font-bold text-white font-mono">{counts.support + counts.contradict + counts.neutral}</span> passages across <span className="font-bold text-white font-mono">{counts.papers}</span> peer-reviewed scientific studies.
              </p>
            </div>

            <div className="flex flex-wrap gap-2.5 font-mono text-xs">
              <div className="flex items-center gap-1.5 px-3 py-1.5 bg-[#042018] text-emerald-300 rounded-xl border border-emerald-500/40 shadow-sm">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                <span className="font-bold">{counts.support} Support</span>
              </div>
              
              <div className="flex items-center gap-1.5 px-3 py-1.5 bg-[#25080e] text-rose-300 rounded-xl border border-rose-500/40 shadow-sm">
                <XCircle className="w-3.5 h-3.5 text-rose-400" />
                <span className="font-bold">{counts.contradict} Contradict</span>
              </div>
              
              <div className="flex items-center gap-1.5 px-3 py-1.5 bg-[#071914] text-emerald-300/80 rounded-xl border border-emerald-900/50 shadow-sm">
                <MinusCircle className="w-3.5 h-3.5 text-emerald-400" />
                <span className="font-bold">{counts.neutral} Neutral</span>
              </div>
            </div>
          </section>
        )}

        {/* Evidence List Section */}
        <section className="space-y-6">
          <div className="flex items-center justify-between border-b border-emerald-900/40 pb-4">
            <div className="flex items-center gap-2.5">
              <FileText className="w-5 h-5 text-cyan-400" />
              <h2 className="text-xl sm:text-2xl font-bold text-[#F0FDF9] font-display">
                Retrieved Scientific Evidence
              </h2>
            </div>
            <span className="text-xs font-mono text-emerald-400/60 uppercase">
              {evidence?.length || 0} PASSAGES_LOADED
            </span>
          </div>
          
          <div className="space-y-5">
            {evidence?.map((ev, index) => (
              <EvidenceCard key={`${ev.doc_id}_${ev.sentence_idx}`} evidence={ev} index={index + 1} />
            ))}
            {(!evidence || evidence.length === 0) && (
              <div className="p-8 rounded-2xl bg-[#061813] border border-emerald-900/40 text-emerald-400/60 text-center font-mono text-xs">
                No indexed scientific passages met the relevance threshold for this query.
              </div>
            )}
          </div>
        </section>

        {/* System Model Telemetry Stamp */}
        <section className="text-[11px] font-mono text-emerald-500/60 text-center pt-8 border-t border-emerald-950 flex flex-col items-center gap-1.5">
          <div className="flex flex-wrap items-center justify-center gap-2 text-emerald-400/80">
            <span className="flex items-center gap-1"><Cpu className="w-3 h-3 text-cyan-400" /> Model: {model?.classifier || "Hybrid Transformer NLI Cross-Encoder"}</span>
            <span>•</span>
            <span className="flex items-center gap-1"><Database className="w-3 h-3 text-emerald-400" /> Retriever: {model?.retriever || "TF-IDF + MeSH PubMed API"}</span>
          </div>
          <p className="max-w-2xl text-emerald-600/70">
            Corpora: {sources_used ? sources_used.join(" & ") : "SciFact corpus & PubMed Live"}. For research reference only. Not medical or clinical advice.
          </p>
        </section>

      </div>
    </main>
  );
}
