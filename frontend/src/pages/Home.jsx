import { useState } from 'react';
import ClaimInput from '../components/ClaimInput';
import ExampleClaims from '../components/ExampleClaims';
import { Database, FileSearch, Cpu, CheckCircle2, ShieldCheck, Sparkles } from 'lucide-react';

export default function Home() {
  const [selectedClaim, setSelectedClaim] = useState("");

  return (
    <main className="flex-grow flex flex-col items-center justify-center px-4 py-12 sm:py-20 sm:px-6 lg:px-8 relative overflow-hidden">
      
      <div className="text-center w-full max-w-4xl mx-auto mb-10">
        
        {/* Top Status Tag */}
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-slate-700/60 bg-slate-900/80 backdrop-blur-md mb-8 shadow-sm">
          <span className="w-2 h-2 rounded-full bg-teal-400" />
          <span className="text-xs font-mono font-medium text-slate-300 tracking-wider">
            Biomedical Claim Verification & Literature Synthesis
          </span>
        </div>

        {/* Editorial Hero Headline */}
        <h1 className="text-4xl sm:text-6xl lg:text-[68px] font-serif font-normal text-white tracking-tight mb-6 leading-[1.12]">
          Verify Scientific Claims with <br className="hidden sm:inline" />
          <span className="italic font-serif font-medium text-teal-300">
            Empirical Evidence
          </span>
        </h1>

        <p className="text-base sm:text-lg text-slate-300/85 max-w-2xl mx-auto mb-10 leading-relaxed font-sans font-normal">
          Cross-reference biomedical hypotheses against peer-reviewed literature using dual-stage corpus retrieval and calibrated Natural Language Inference.
        </p>
        
        {/* Claim Input Console */}
        <ClaimInput initialClaim={selectedClaim} />
        
        {/* Curated Sample Claims */}
        <ExampleClaims onSelect={setSelectedClaim} />

        {/* Engine Capability Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3.5 mt-16 max-w-4xl mx-auto text-left">
          <div className="p-4 rounded-xl border border-slate-800/80 bg-slate-900/60 backdrop-blur-md shadow-sm">
            <div className="flex items-center gap-2 text-teal-400 mb-1.5">
              <Database className="w-4 h-4" />
              <span className="text-xs font-mono font-bold text-slate-200">5,183+ Papers</span>
            </div>
            <p className="text-xs text-slate-400 font-sans">SciFact peer-reviewed index</p>
          </div>

          <div className="p-4 rounded-xl border border-slate-800/80 bg-slate-900/60 backdrop-blur-md shadow-sm">
            <div className="flex items-center gap-2 text-sky-400 mb-1.5">
              <FileSearch className="w-4 h-4" />
              <span className="text-xs font-mono font-bold text-slate-200">PubMed Live</span>
            </div>
            <p className="text-xs text-slate-400 font-sans">Real-time NCBI query expansion</p>
          </div>

          <div className="p-4 rounded-xl border border-slate-800/80 bg-slate-900/60 backdrop-blur-md shadow-sm">
            <div className="flex items-center gap-2 text-indigo-400 mb-1.5">
              <Cpu className="w-4 h-4" />
              <span className="text-xs font-mono font-bold text-slate-200">NLI Inference</span>
            </div>
            <p className="text-xs text-slate-400 font-sans">Transformer cross-encoder</p>
          </div>

          <div className="p-4 rounded-xl border border-slate-800/80 bg-slate-900/60 backdrop-blur-md shadow-sm">
            <div className="flex items-center gap-2 text-emerald-400 mb-1.5">
              <CheckCircle2 className="w-4 h-4" />
              <span className="text-xs font-mono font-bold text-slate-200">Grounded Citations</span>
            </div>
            <p className="text-xs text-slate-400 font-sans">Exact [E#] evidence links</p>
          </div>
        </div>

      </div>
    </main>
  );
}

