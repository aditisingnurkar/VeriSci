import { useEffect, useState } from 'react';
import { useNavigate, useLocation, Navigate } from 'react-router-dom';
import { AlertCircle, RotateCcw, Cpu, Database, Search, ShieldCheck } from 'lucide-react';

export default function Analysis() {
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const [scanPhase, setScanPhase] = useState(0);
  const navigate = useNavigate();
  const location = useLocation();
  const claim = location.state?.claim;

  const phases = [
    { label: "INITIALIZING_QUERY_EMBEDDING", detail: "Formulating MeSH expanded search vectors" },
    { label: "RETRIEVING_SCIENTIFIC_EVIDENCE", detail: "Querying SciFact 5.1k corpus & live PubMed indices" },
    { label: "CROSS_ENCODER_INFERENCE", detail: "Evaluating Natural Language Inference across evidence passages" },
    { label: "SYNTHESIZING_VERDICT_REPORT", detail: "Aggregating evidence strength and generating citations" }
  ];

  useEffect(() => {
    const timer = setInterval(() => {
      setScanPhase((prev) => (prev < phases.length - 1 ? prev + 1 : prev));
    }, 900);
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
      
      // Delay slightly for smooth HUD experience if fast
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
    <main className="flex-grow flex flex-col items-center justify-center px-4 py-12 sm:px-6 lg:px-8 bg-grid-pattern relative overflow-hidden">
      {/* Glow auras */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-cyan-500/10 rounded-full blur-[140px] pointer-events-none -z-10" />

      <div className="w-full max-w-2xl mx-auto text-center">
        
        {/* Target Header */}
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-cyan-500/30 bg-[#061e17] text-xs font-mono text-cyan-300 uppercase tracking-widest mb-6">
          <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
          <span>Active Verification Protocol</span>
        </div>

        {/* Claim Display Box */}
        <div className="p-6 rounded-2xl border border-emerald-500/20 bg-[#061813]/90 backdrop-blur-xl shadow-2xl mb-10 text-left relative overflow-hidden">
          <div className="absolute top-0 right-0 p-3 text-[10px] font-mono text-emerald-500/60 uppercase">
            TARGET_CLAIM_HASH // 0xVERI
          </div>
          <p className="text-xs font-mono font-semibold uppercase tracking-wider text-emerald-400 mb-2">
            Claim Under Examination
          </p>
          <h2 className="text-lg sm:text-xl font-medium text-[#F0FDF9] font-sans leading-relaxed border-l-2 border-cyan-400 pl-3.5">
            "{claim}"
          </h2>
        </div>
        
        {loading ? (
          <div className="flex flex-col items-center justify-center">
            {/* Cyber Radar Animation */}
            <div className="relative w-36 h-36 flex items-center justify-center mb-8">
              <div className="absolute inset-0 rounded-full border border-emerald-500/20 animate-ping opacity-30" />
              <div className="absolute inset-2 rounded-full border border-cyan-500/30 animate-pulse" />
              <div className="absolute inset-6 rounded-full border-2 border-dashed border-emerald-400/40 animate-spin" style={{ animationDuration: '8s' }} />
              <div className="w-16 h-16 rounded-full bg-gradient-to-tr from-emerald-500/20 to-cyan-500/30 border border-cyan-400/50 flex items-center justify-center shadow-lg shadow-cyan-500/20">
                <Search className="w-7 h-7 text-cyan-300 animate-pulse" />
              </div>
            </div>

            {/* Diagnostic Steps Log */}
            <div className="w-full space-y-2 font-mono text-left max-w-md mx-auto">
              {phases.map((phase, idx) => (
                <div 
                  key={idx}
                  className={`flex items-center gap-3 p-2.5 rounded-lg border text-xs transition-all duration-300 ${
                    idx === scanPhase 
                      ? "border-cyan-400/50 bg-[#0c2a21] text-cyan-200 shadow-md shadow-cyan-950/40" 
                      : idx < scanPhase
                      ? "border-emerald-900/40 bg-[#051510]/60 text-emerald-400/80"
                      : "border-transparent text-emerald-800"
                  }`}
                >
                  <span className={`w-1.5 h-1.5 rounded-full ${idx <= scanPhase ? "bg-cyan-400" : "bg-emerald-950"}`} />
                  <div className="flex flex-col truncate">
                    <span className="font-bold tracking-wider">{phase.label}</span>
                    <span className="text-[10px] opacity-70 truncate">{phase.detail}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : error ? (
          <div className="bg-[#1f0a0e] border border-rose-500/40 text-rose-200 px-6 py-6 rounded-2xl max-w-md mx-auto text-center shadow-2xl">
            <AlertCircle className="w-10 h-10 mx-auto mb-3 text-rose-400" />
            <h3 className="font-bold text-lg mb-1 text-white font-display">Analysis Protocol Failed</h3>
            <p className="text-xs text-rose-300/80 mb-5 font-mono">{error}</p>
            <button 
              onClick={analyzeClaim}
              className="inline-flex items-center px-5 py-2.5 bg-rose-600 hover:bg-rose-500 text-white rounded-xl transition-all text-xs font-mono font-bold uppercase tracking-wider shadow-lg shadow-rose-950/50 cursor-pointer"
            >
              <RotateCcw className="w-3.5 h-3.5 mr-2" /> Retry Verification
            </button>
          </div>
        ) : null}

      </div>
    </main>
  );
}
