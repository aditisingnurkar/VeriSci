import { useEffect, useState } from 'react';
import { useNavigate, useLocation, Navigate } from 'react-router-dom';
import { AlertCircle, RotateCcw } from 'lucide-react';

export default function Analysis() {
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const location = useLocation();
  const claim = location.state?.claim;

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
      
      navigate('/results', { 
         state: { 
           claim: data.claim,
           verdict: data.verdict,
           strength: data.strength,
           score: data.score,
           reason: data.reason,
           counts: data.counts,
           evidence: data.evidence,
           model: data.model
         } 
      });

    } catch (err) {
      console.error(err);
      setError(err.message || "Failed to connect to the backend.");
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
    <main className="flex-grow flex flex-col items-center justify-center px-4 py-12 sm:px-6 lg:px-8 bg-slate-50/50">
      <div className="w-full text-center mb-8">
        <p className="text-sm font-medium text-slate-500 uppercase tracking-wider mb-2">Analyzing</p>
        <h1 className="text-xl sm:text-2xl font-semibold text-slate-900 max-w-3xl mx-auto italic">
          "{claim}"
        </h1>
      </div>
      
      {loading ? (
        <div className="flex flex-col items-center space-y-4">
          <div className="w-12 h-12 border-4 border-slate-200 border-t-blue-600 rounded-full animate-spin"></div>
          <p className="text-slate-600">Cross-referencing scientific literature...</p>
        </div>
      ) : error ? (
        <div className="bg-red-50 border border-red-200 text-red-700 px-6 py-4 rounded-xl max-w-md text-center">
          <AlertCircle className="w-8 h-8 mx-auto mb-3 text-red-500" />
          <h3 className="font-bold mb-2">Analysis Failed</h3>
          <p className="text-sm mb-4">{error}</p>
          <button 
            onClick={analyzeClaim}
            className="inline-flex items-center px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-sm font-medium"
          >
            <RotateCcw className="w-4 h-4 mr-2" /> Retry Analysis
          </button>
        </div>
      ) : null}
    </main>
  );
}
