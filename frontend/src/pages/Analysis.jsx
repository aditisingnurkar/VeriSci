import { useEffect, useState } from 'react';
import { useNavigate, useLocation, Navigate } from 'react-router-dom';
import AnalysisProgress from '../components/AnalysisProgress';

export default function Analysis() {
  const [step, setStep] = useState(1);
  const navigate = useNavigate();
  const location = useLocation();
  const claim = location.state?.claim;

  useEffect(() => {
    if (!claim) return;

    let isMounted = true;

    async function analyzeClaim() {
      try {
        setStep(1); // Received
        await new Promise(r => setTimeout(r, 600));
        
        setStep(2); // Searching
        // Call backend API for full verification
        const response = await fetch('http://127.0.0.1:8000/api/verify', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ claim, top_k: 5 })
        });
        
        if (!response.ok) {
           throw new Error("Failed to verify claim");
        }
        
        const data = await response.json();
        
        if (!isMounted) return;

        setStep(3); // Analyzing
        setStep(4); // Preparing verdict

        // Format evidence for results page, matching what UI expects
        const formattedEvidence = data.evidence.map((ev) => ({
           id: ev.document_id + "_" + Math.random().toString(36).substr(2, 9),
           title: ev.title,
           snippet: ev.evidence_text,
           prediction: ev.prediction,
           confidence: Math.round(ev.confidence * 100),
           relevanceScore: ev.relevance_score,
           source: ev.source
        }));

        navigate('/results', { 
           state: { 
             claim,
             verdict: data.verdict,
             confidence: data.confidence,
             supportingCount: data.supportingCount,
             contradictingCount: data.contradictingCount,
             neutralCount: data.neutralCount,
             evidence: formattedEvidence 
           } 
        });

      } catch (error) {
        console.error(error);
        if (isMounted) {
           alert("Error retrieving evidence. Is the backend running at port 8000?");
           navigate('/');
        }
      }
    }

    analyzeClaim();

    return () => { isMounted = false; };
  }, [claim, navigate]);

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
      <AnalysisProgress currentStep={step} />
    </main>
  );
}
