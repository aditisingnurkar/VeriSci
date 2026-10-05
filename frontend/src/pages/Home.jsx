import { useState } from 'react';
import ClaimInput from '../components/ClaimInput';
import ExampleClaims from '../components/ExampleClaims';
import { ShieldCheck, Cpu, Database, Activity, FileSearch } from 'lucide-react';

export default function Home() {
  const [selectedClaim, setSelectedClaim] = useState("");

  return (
    <main className="flex-grow flex flex-col items-center justify-center px-4 py-12 sm:py-16 sm:px-6 lg:px-8 relative overflow-hidden bg-grid-pattern">
      {/* Background Decorative Glow Auras */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-emerald-500/10 rounded-full blur-[120px] pointer-events-none -z-10 animate-pulse-glow" />
      <div className="absolute top-1/3 left-1/4 w-[300px] h-[300px] bg-cyan-500/10 rounded-full blur-[100px] pointer-events-none -z-10" />

      <div className="text-center w-full max-w-4xl mx-auto mb-12">
        {/* Top Status Badge */}
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-emerald-500/30 bg-[#072019]/80 backdrop-blur-md mb-6 shadow-inner">
          <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
          <span className="text-xs font-mono font-medium text-emerald-300 uppercase tracking-widest">
            Scientific Truth Verification Engine
          </span>
        </div>

        {/* Hero Title */}
        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-[#F0FDF9] tracking-tight mb-6 font-display leading-[1.15]">
          Verify Scientific Claims <br className="hidden sm:block" />
          <span className="bg-clip-text text-transparent bg-gradient-to-r from-cyan-300 via-emerald-400 to-[#10E7C1] drop-shadow-[0_0_35px_rgba(0,245,212,0.3)]">
            With Empirical Evidence
          </span>
        </h1>

        <p className="text-base sm:text-lg text-emerald-100/70 max-w-2xl mx-auto mb-10 leading-relaxed font-sans">
          Cross-reference scientific hypotheses across peer-reviewed literature using dual-stage biomedical retrieval and transformer-based Natural Language Inference.
        </p>
        
        {/* Claim Input Console */}
        <ClaimInput initialClaim={selectedClaim} />
        
        {/* Example Claim Buttons */}
        <ExampleClaims onSelect={setSelectedClaim} />

        {/* Engine Capability Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-14 max-w-3xl mx-auto text-left">
          <div className="p-3.5 rounded-xl border border-emerald-950/80 bg-[#061813]/60 backdrop-blur-sm">
            <div className="flex items-center gap-2 text-cyan-400 mb-1">
              <Database className="w-4 h-4" />
              <span className="text-xs font-mono font-bold text-emerald-200">5,183+ Papers</span>
            </div>
            <p className="text-[11px] text-emerald-400/60 font-mono">SciFact Corpus Indexed</p>
          </div>

          <div className="p-3.5 rounded-xl border border-emerald-950/80 bg-[#061813]/60 backdrop-blur-sm">
            <div className="flex items-center gap-2 text-emerald-400 mb-1">
              <FileSearch className="w-4 h-4" />
              <span className="text-xs font-mono font-bold text-emerald-200">Live PubMed</span>
            </div>
            <p className="text-[11px] text-emerald-400/60 font-mono">MeSH Query Expansion</p>
          </div>

          <div className="p-3.5 rounded-xl border border-emerald-950/80 bg-[#061813]/60 backdrop-blur-sm">
            <div className="flex items-center gap-2 text-teal-300 mb-1">
              <Cpu className="w-4 h-4" />
              <span className="text-xs font-mono font-bold text-emerald-200">NLI Classifier</span>
            </div>
            <p className="text-[11px] text-emerald-400/60 font-mono">Cross-Encoder Inference</p>
          </div>

          <div className="p-3.5 rounded-xl border border-emerald-950/80 bg-[#061813]/60 backdrop-blur-sm">
            <div className="flex items-center gap-2 text-emerald-300 mb-1">
              <Activity className="w-4 h-4" />
              <span className="text-xs font-mono font-bold text-emerald-200">0% Hallucination</span>
            </div>
            <p className="text-[11px] text-emerald-400/60 font-mono">Grounded [E#] Citations</p>
          </div>
        </div>

      </div>
    </main>
  );
}
