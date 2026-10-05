import { useLocation, Navigate, Link } from 'react-router-dom';
import EvidenceCard from '../components/EvidenceCard';
import VerdictCard from '../components/VerdictCard';
import ExplanationCard from '../components/ExplanationCard';
import ClaimChat from '../components/ClaimChat';
import { ArrowLeft, FileText, CheckCircle, AlertCircle, AlertTriangle } from 'lucide-react';

export default function Results() {
  const location = useLocation();
  const data = location.state;

  if (!data || !data.claim) {
    return <Navigate to="/" replace />;
  }

  const { claim, verdict, strength, reason, counts, evidence, model, verification_id, sources_used } = data;

  return (
    <main className="flex-grow bg-slate-50/50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto space-y-12">
        
        <div>
          <Link to="/" className="inline-flex items-center text-sm font-medium text-slate-500 hover:text-blue-600 mb-8 transition-colors">
            <ArrowLeft className="w-4 h-4 mr-1" />
            Verify another claim
          </Link>
          
          <VerdictCard 
            verdict={verdict} 
            claim={claim} 
            strength={strength} 
            reason={reason} 
          />
        </div>

        {/* AI Explanation and Chat */}
        {verification_id && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <ExplanationCard verificationId={verification_id} />
            <ClaimChat verificationId={verification_id} verdict={verdict} />
          </div>
        )}

        {/* Evidence Breakdown */}
        {counts?.papers > 0 && (
          <section className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col sm:flex-row gap-6 justify-between items-center">
            <div>
              <h3 className="text-sm font-semibold uppercase tracking-widest text-slate-500 mb-1">Evidence Breakdown</h3>
              <p className="text-slate-600 text-sm">Analyzed {counts.support + counts.contradict + counts.neutral} passages from {counts.papers} studies.</p>
            </div>
            <div className="flex flex-wrap gap-4">
              <div className="flex items-center gap-2 px-3 py-1.5 bg-green-50 text-green-700 rounded-lg border border-green-100">
                <CheckCircle className="w-4 h-4" />
                <span className="font-bold">{counts.support} Support</span>
              </div>
              <div className="flex items-center gap-2 px-3 py-1.5 bg-red-50 text-red-700 rounded-lg border border-red-100">
                <AlertCircle className="w-4 h-4" />
                <span className="font-bold">{counts.contradict} Contradict</span>
              </div>
              <div className="flex items-center gap-2 px-3 py-1.5 bg-slate-100 text-slate-600 rounded-lg border border-slate-200">
                <AlertTriangle className="w-4 h-4" />
                <span className="font-bold">{counts.neutral} Neutral</span>
              </div>
            </div>
          </section>
        )}

        <section className="space-y-6">
          <div className="flex items-center justify-between border-b border-slate-200 pb-4">
            <div className="flex items-center gap-2">
              <FileText className="w-6 h-6 text-slate-800" />
              <h2 className="text-2xl font-bold text-slate-900">Retrieved Scientific Evidence</h2>
            </div>
          </div>
          
          <div className="space-y-6">
            {evidence?.map((ev, index) => (
              <EvidenceCard key={`${ev.doc_id}_${ev.sentence_idx}`} evidence={ev} index={index + 1} />
            ))}
            {(!evidence || evidence.length === 0) && (
              <p className="text-slate-500 italic p-6 bg-white rounded-xl border border-slate-200">No evidence was retrieved for this claim.</p>
            )}
          </div>
        </section>

        <section className="text-xs text-slate-400 text-center pt-8 border-t border-slate-200">
          <p>This verification was generated automatically by {model?.classifier} (via {model?.retriever}). It is based only on {sources_used ? sources_used.join(" and ") : "the SciFact corpus"} and is not medical or professional advice.</p>
        </section>

      </div>
    </main>
  );
}
