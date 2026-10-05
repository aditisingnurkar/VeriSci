import { useState, useEffect } from 'react';
import { BookOpen, AlertCircle, Loader2 } from 'lucide-react';
import { cn } from '../lib/utils';

export default function ExplanationCard({ verificationId }) {
  const [explanation, setExplanation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!verificationId) return;
    
    const fetchExplanation = async () => {
      setLoading(true);
      setError(null);
      try {
        const apiUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
        const response = await fetch(`${apiUrl}/api/explain`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ verification_id: verificationId }),
        });
        
        if (!response.ok) {
          throw new Error('Failed to load explanation');
        }
        
        const data = await response.json();
        setExplanation(data);
      } catch (err) {
        console.error(err);
        setError("AI explanation unavailable.");
      } finally {
        setLoading(false);
      }
    };
    
    fetchExplanation();
  }, [verificationId]);

  const highlightEvidence = (cid) => {
    const el = document.getElementById(`evidence-${cid}`);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'center' });
      el.classList.add('ring-2', 'ring-blue-500', 'bg-blue-50');
      setTimeout(() => {
        el.classList.remove('ring-2', 'ring-blue-500', 'bg-blue-50');
      }, 2000);
    }
  };

  const renderTextWithCitations = (text, citations) => {
    if (!text) return null;
    
    // Split by [E#]
    const parts = text.split(/(\[E\d+\])/g);
    return parts.map((part, i) => {
      const match = part.match(/^\[(E\d+)\]$/);
      if (match && citations?.includes(match[1])) {
        return (
          <button 
            key={i} 
            onClick={() => highlightEvidence(match[1])}
            className="inline-flex items-center justify-center px-1.5 py-0.5 mx-1 rounded text-xs font-bold bg-blue-100 text-blue-700 hover:bg-blue-200 transition-colors"
          >
            {match[1]}
          </button>
        );
      }
      return <span key={i}>{part}</span>;
    });
  };

  return (
    <div className="bg-slate-900 text-slate-50 p-6 rounded-2xl shadow-sm w-full relative overflow-hidden">
      <div className="absolute top-0 right-0 p-8 opacity-5 pointer-events-none">
        <BookOpen className="w-48 h-48" />
      </div>
      
      <div className="relative z-10">
        <div className="flex items-center gap-2 mb-4 border-b border-slate-700 pb-4">
          <BookOpen className="w-5 h-5 text-blue-400" />
          <h3 className="text-lg font-semibold text-white">Analysis & Explanation</h3>
        </div>
        
        {loading && (
          <div className="flex items-center gap-3 text-slate-400 py-4">
            <Loader2 className="w-5 h-5 animate-spin text-blue-400" />
            <span>Generating evidence-based explanation...</span>
          </div>
        )}
        
        {error && !loading && (
          <div className="flex items-center gap-2 text-slate-400 py-2">
            <AlertCircle className="w-4 h-4 text-amber-500" />
            <span className="text-sm italic">{error}</span>
          </div>
        )}
        
        {explanation && !loading && (
          <div className="space-y-4">
            <p className="text-slate-300 leading-relaxed text-sm">
              {renderTextWithCitations(explanation.explanation, explanation.citations)}
            </p>
            
            {explanation.limitations && explanation.limitations.length > 0 && (
              <div className="mt-4 pt-4 border-t border-slate-800">
                <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">Limitations</h4>
                <ul className="list-disc list-inside text-xs text-slate-400 space-y-1">
                  {explanation.limitations.map((lim, i) => (
                    <li key={i}>{lim}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
