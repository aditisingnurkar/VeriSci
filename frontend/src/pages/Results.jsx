import { useState } from 'react';
import { useLocation, Navigate, Link } from 'react-router-dom';
import EvidenceCard from '../components/EvidenceCard';
import VerdictCard from '../components/VerdictCard';
import ExplanationCard from '../components/ExplanationCard';
import ClaimChat from '../components/ClaimChat';
import { ArrowLeft, FileText, CheckCircle2, XCircle, MinusCircle, Layers, Cpu, Database, Filter } from 'lucide-react';

export default function Results() {
  const location = useLocation();
  const data = location.state;
  const [filterStance, setFilterStance] = useState('ALL');

  if (!data || !data.claim) {
    return <Navigate to="/" replace />;
  }

  const { claim, verdict, strength, reason, counts, evidence, model, verification_id, sources_used } = data;

  const filteredEvidence = (evidence || []).filter(ev => {
    if (filterStance === 'ALL') return true;
    if (filterStance === 'SUPPORT') return ev.prediction === 'SUPPORT';
    if (filterStance === 'CONTRADICT') return ev.prediction === 'CONTRADICT';
    if (filterStance === 'NEUTRAL') return ev.prediction === 'NEUTRAL';
    return true;
  });

  return (
    <main className="flex-grow py-10 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
      <div className="max-w-5xl mx-auto space-y-8">
        
        {/* Navigation & Main Verdict */}
        <div>
          <Link 
            to="/" 
            className="inline-flex items-center text-xs font-mono font-medium text-teal-400 hover:text-teal-300 mb-5 transition-colors group"
          >
            <ArrowLeft className="w-3.5 h-3.5 mr-1.5 group-hover:-translate-x-1 transition-transform" />
            Return to Verification Desk
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

        {/* Evidence Breakdown & Filter Strip */}
        {counts?.papers > 0 && (
          <section className="p-5 sm:p-6 rounded-2xl science-card flex flex-col sm:flex-row gap-5 justify-between items-start sm:items-center">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <Layers className="w-4 h-4 text-teal-400" />
                <h3 className="text-xs font-mono font-semibold uppercase tracking-wider text-slate-300">
                  Literature Distribution
                </h3>
              </div>
              <p className="text-xs sm:text-sm text-slate-300 font-sans">
                Synthesized <span className="font-bold text-white font-mono">{counts.support + counts.contradict + counts.neutral}</span> passages across <span className="font-bold text-white font-mono">{counts.papers}</span> peer-reviewed papers.
              </p>
            </div>

            <div className="flex flex-wrap gap-2 font-mono text-xs">
              <button 
                onClick={() => setFilterStance('ALL')}
                className={`px-3 py-1 rounded-lg border transition-all cursor-pointer ${filterStance === 'ALL' ? 'bg-teal-950 text-teal-300 border-teal-500/50' : 'bg-slate-900/80 text-slate-400 border-slate-800 hover:text-white'}`}
              >
                All ({counts.support + counts.contradict + counts.neutral})
              </button>
              <button 
                onClick={() => setFilterStance('SUPPORT')}
                className={`flex items-center gap-1.5 px-3 py-1 rounded-lg border transition-all cursor-pointer ${filterStance === 'SUPPORT' ? 'bg-emerald-950 text-emerald-300 border-emerald-500/50' : 'bg-slate-900/80 text-slate-400 border-slate-800 hover:text-emerald-300'}`}
              >
                <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                <span>Support ({counts.support})</span>
              </button>
              
              <button 
                onClick={() => setFilterStance('CONTRADICT')}
                className={`flex items-center gap-1.5 px-3 py-1 rounded-lg border transition-all cursor-pointer ${filterStance === 'CONTRADICT' ? 'bg-rose-950 text-rose-300 border-rose-500/50' : 'bg-slate-900/80 text-slate-400 border-slate-800 hover:text-rose-300'}`}
              >
                <XCircle className="w-3 h-3 text-rose-400" />
                <span>Refute ({counts.contradict})</span>
              </button>
              
              {counts.neutral > 0 && (
                <button 
                  onClick={() => setFilterStance('NEUTRAL')}
                  className={`flex items-center gap-1.5 px-3 py-1 rounded-lg border transition-all cursor-pointer ${filterStance === 'NEUTRAL' ? 'bg-slate-800 text-slate-200 border-slate-600' : 'bg-slate-900/80 text-slate-400 border-slate-800 hover:text-slate-200'}`}
                >
                  <MinusCircle className="w-3 h-3 text-slate-400" />
                  <span>Neutral ({counts.neutral})</span>
                </button>
              )}
            </div>
          </section>
        )}

        {/* Evidence List Section */}
        <section className="space-y-5">
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
            <div className="flex items-center gap-2">
              <FileText className="w-4 h-4 text-teal-400" />
              <h2 className="text-xl font-serif font-medium text-white">
                Indexed Evidence Passages
              </h2>
            </div>
            <span className="text-xs font-mono text-slate-400">
              Showing {filteredEvidence.length} of {evidence?.length || 0} studies
            </span>
          </div>
          
          <div className="space-y-4">
            {filteredEvidence.map((ev, index) => (
              <EvidenceCard key={`${ev.doc_id}_${ev.sentence_idx}`} evidence={ev} index={index + 1} />
            ))}
            {filteredEvidence.length === 0 && (
              <div className="p-8 rounded-2xl science-card text-slate-400 text-center font-sans text-xs">
                No evidence matches the selected stance filter.
              </div>
            )}
          </div>
        </section>

        {/* System Model Provenance */}
        <section className="text-xs font-mono text-slate-400 text-center pt-8 border-t border-slate-800/80 flex flex-col items-center gap-1.5">
          <div className="flex flex-wrap items-center justify-center gap-2 text-slate-300">
            <span className="flex items-center gap-1"><Cpu className="w-3 h-3 text-teal-400" /> Model: {model?.classifier || "Hybrid Transformer NLI"}</span>
            <span>•</span>
            <span className="flex items-center gap-1"><Database className="w-3 h-3 text-sky-400" /> Retriever: {model?.retriever || "SciFact TF-IDF + PubMed Live"}</span>
          </div>
          <p className="max-w-2xl text-slate-400 text-[11px] font-sans">
            Corpus Sources: {sources_used ? sources_used.join(" & ") : "SciFact corpus & PubMed Live"}. Designed for biomedical research and literature review.
          </p>
        </section>

      </div>
    </main>
  );
}

