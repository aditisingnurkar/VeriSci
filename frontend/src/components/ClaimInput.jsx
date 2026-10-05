import { useState } from 'react';
import { Search } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function ClaimInput({ initialClaim = "", onExampleClick }) {
  const [claim, setClaim] = useState(initialClaim);
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!claim.trim()) return;
    // In a real app, we'd encode this or pass it in state.
    // We pass it via state to the analysis page.
    navigate('/analyze', { state: { claim } });
  };

  // Re-sync if initialClaim changes (e.g. example clicked)
  if (initialClaim !== claim && document.activeElement !== document.getElementById('claim-input') && initialClaim) {
     setClaim(initialClaim);
  }

  return (
    <div className="w-full max-w-3xl mx-auto">
      <form onSubmit={handleSubmit} className="relative">
        <div className="overflow-hidden rounded-2xl border border-slate-300 shadow-sm bg-white focus-within:border-blue-500 focus-within:ring-1 focus-within:ring-blue-500 transition-all">
          <textarea
            id="claim-input"
            rows={4}
            className="block w-full resize-none border-0 py-4 px-5 text-slate-900 placeholder:text-slate-400 focus:ring-0 sm:text-lg sm:leading-relaxed"
            placeholder="Enter a scientific or health-related claim to verify..."
            value={claim}
            onChange={(e) => setClaim(e.target.value)}
          />
          <div className="flex items-center justify-between border-t border-slate-100 bg-slate-50 px-5 py-3">
            <span className="text-xs text-slate-500 font-medium">
              Powered by SciFact and Machine Learning
            </span>
            <button
              type="submit"
              disabled={!claim.trim()}
              className="inline-flex items-center rounded-xl bg-blue-600 px-6 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              <Search className="w-4 h-4 mr-2" />
              Verify Claim
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}
