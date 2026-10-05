import { useEffect, useState } from 'react';
import { useNavigate, useLocation, Navigate } from 'react-router-dom';
import { AlertCircle, RotateCcw, Database, Search, Sparkles, CheckCircle2 } from 'lucide-react';

export default function Analysis() {
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const [scanPhase, setScanPhase] = useState(0);
  const navigate = useNavigate();
  const location = useLocation();
  const claim = location.state?.claim;

  const phases = [
    { label: "Formulating Query Vectors", detail: "MeSH expansion and biomedical semantic mapping" },
    { label: "Querying Scientific Indices", detail: "Searching SciFact (5,183 papers) & PubMed Live" },
    { label: "Cross-Encoder NLI Inference", detail: "Classifying evidence stances with Transformer model" },
    { label: "Synthesizing Evidence Dossier", detail: "Calibrating verdict and grounding citations" }
  ];

  useEffect(() => {
    const timer = setInterval(() => {
      setScanPhase((prev) => (prev < phases.length - 1 ? prev + 1 : prev));
    }, 850);
    return () => clearInterval(timer);
  }, []);

  const analyzeClaim = async () => {
    if (!claim) return;
    try {
      setLoading(true);
      setError(null);
      
      const apiUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
      const response = await fetch(`${apiUrl}/api/verify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ claim, top_k: 5 })
      });
      
      if (!response.ok) {
         throw new Error(`Server returned ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      // Delay slightly for smooth transition
      setTimeout(() => {
        navigate('/results', { 
          state: data
        });
      }, 500);

    } catch (err) {
      console.error(err);
      setError(err.message || "Failed to connect to the backend verification server.");
      setLoading(false);
    }
  };

  useEffect(() => {
    analyzeClaim();
  }, [claim]);

  if (!claim) {
    return <Navigate to="/" replace />;
  }

  return (
    <main className="flex-grow flex flex-col items-center justify-center px-4 py-16 sm:px-6 lg:px-8 relative overflow-hidden">
      <div className="w-full max-w-2xl mx-auto text-center">
        
        {/* Status Pill */}
        <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full border border-teal-500/30 bg-slate-900/80 text-xs font-mono text-teal-300 mb-6 shadow-sm">
          <span className="w-2 h-2 rounded-full bg-teal-400 animate-pulse" />
          <span>Biomedical Verification in Progress</span>
        </div>

        {/* Claim Box */}
        <div className="p-6 rounded-2xl science-card mb-10 text-left relative overflow-hidden">
          <p className="text-xs font-mono font-semibold uppercase tracking-wider text-slate-400 mb-2">
            Target Hypothesis
          </p>
          <h2 className="text-lg sm:text-xl font-serif text-white leading-relaxed border-l-2 border-teal-400 pl-3.5">
            "{claim}"
          </h2>
        </div>
        
        {loading ? (
          <div className="flex flex-col items-center justify-center">
            {/* Scientific Scanner Pulse */}
            <div className="relative w-28 h-28 flex items-center justify-center mb-8">
              <div className="absolute inset-0 rounded-full border border-teal-500/20 animate-ping opacity-25" />
              <div className="absolute inset-3 rounded-full border border-teal-400/30 animate-pulse" />
              <div className="w-14 h-14 rounded-full bg-slate-900 border border-teal-400/60 flex items-center justify-center shadow-lg shadow-teal-950/50">
                <Search className="w-6 h-6 text-teal-300 animate-pulse" />
              </div>
            </div>

            {/* Step Progression */}
            <div className="w-full space-y-2.5 font-sans text-left max-w-md mx-auto">
              {phases.map((phase, idx) => (
                <div 
                  key={idx}
                  className={`flex items-center gap-3 p-3 rounded-xl border text-xs transition-all duration-300 ${
                    idx === scanPhase 
                      ? "border-teal-500/50 bg-slate-900/90 text-teal-200 shadow-sm" 
                      : idx < scanPhase
                      ? "border-slate-800 bg-slate-950/40 text-slate-300"
                      : "border-transparent text-slate-400"
                  }`}
                >
                  <span className={`w-2 h-2 rounded-full ${idx <= scanPhase ? "bg-teal-400" : "bg-slate-800"}`} />
                  <div className="flex flex-col truncate">
                    <span className="font-semibold text-slate-200">{phase.label}</span>
                    <span className="text-[11px] text-slate-400 truncate">{phase.detail}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : error ? (
          <div className="bg-rose-950/40 border border-rose-500/30 text-rose-200 px-6 py-6 rounded-2xl max-w-md mx-auto text-center shadow-xl">
            <AlertCircle className="w-8 h-8 mx-auto mb-2 text-rose-400" />
            <h3 className="font-semibold text-base mb-1 text-white font-sans">Analysis Request Failed</h3>
            <p className="text-xs text-rose-300/80 mb-4 font-mono">{error}</p>
            <button 
              onClick={analyzeClaim}
              className="inline-flex items-center px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white rounded-lg transition-all text-xs font-sans font-semibold cursor-pointer"
            >
              <RotateCcw className="w-3.5 h-3.5 mr-1.5" /> Retry Analysis
            </button>
          </div>
        ) : null}

      </div>
    </main>
  );
}

