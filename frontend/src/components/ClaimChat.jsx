import { useState } from 'react';
import { Send, Sparkles, Loader2, AlertCircle, MessageSquare, Terminal } from 'lucide-react';

export default function ClaimChat({ verificationId, verdict }) {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Neural query interface active. Ask any specific question regarding the retrieved scientific papers or statistical evidence.', citations: [] }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const getSuggestedQuestions = () => {
    let questions = ["Explain this in simple language."];
    if (verdict === "CONTRADICTED") {
      questions.unshift("Why is this claim contradicted?");
      questions.push("What do the strongest studies state?");
    } else if (verdict === "SUPPORTED") {
      questions.unshift("What evidence supports the claim?");
      questions.push("Are there any conflicting findings?");
    } else if (verdict === "MIXED") {
      questions.unshift("Why is the evidence conflicting?");
      questions.push("Which study is the most conclusive?");
    } else {
      questions.push("What related studies were found?");
    }
    return questions.slice(0, 3);
  };

  const highlightEvidence = (cid) => {
    const el = document.getElementById(`evidence-${cid}`);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'center' });
      el.classList.add('ring-2', 'ring-cyan-400', 'bg-[#0e352a]');
      setTimeout(() => {
        el.classList.remove('ring-2', 'ring-cyan-400', 'bg-[#0e352a]');
      }, 2500);
    }
  };

  const renderTextWithCitations = (text, citationsObj) => {
    if (!text) return null;
    
    // Create a set of valid citation IDs
    const validCids = citationsObj ? citationsObj.map(c => c.evidence_id) : [];
    
    // Split by [E#]
    const parts = text.split(/(\[E\d+\])/g);
    return parts.map((part, i) => {
      const match = part.match(/^\[(E\d+)\]$/);
      if (match && validCids.includes(match[1])) {
        const citeObj = citationsObj.find(c => c.evidence_id === match[1]);
        return (
          <button 
            key={i} 
            title={citeObj?.title}
            onClick={() => highlightEvidence(match[1])}
            className="inline-flex items-center justify-center px-1.5 py-0.5 mx-1 rounded text-xs font-mono font-bold bg-cyan-950 text-cyan-300 border border-cyan-400/50 hover:bg-cyan-400 hover:text-black transition-all cursor-pointer"
          >
            {match[1]}
          </button>
        );
      }
      return <span key={i}>{part}</span>;
    });
  };

  const handleSend = async (e, text = input) => {
    if (e) e.preventDefault();
    if (!text.trim() || !verificationId || loading) return;
    
    const userMsg = { role: 'user', content: text };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);
    setError(null);
    
    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
      const historyToSend = messages.filter(m => m.role !== 'system').map(m => ({ role: m.role, content: m.content }));
      
      const response = await fetch(`${apiUrl}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          verification_id: verificationId,
          message: text,
          history: historyToSend
        }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to get answer');
      }
      
      const data = await response.json();
      setMessages(prev => [...prev, { role: 'assistant', content: data.answer, citations: data.citations }]);
    } catch (err) {
      console.error(err);
      setError("AI assistant consultation offline.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-[#061813]/90 rounded-3xl border border-emerald-500/20 shadow-2xl backdrop-blur-xl flex flex-col h-[520px] overflow-hidden">
      {/* Top Header */}
      <div className="p-4 border-b border-emerald-900/40 flex items-center justify-between bg-[#04100d]/90">
        <div className="flex items-center gap-2">
          <Terminal className="w-4 h-4 text-cyan-400" />
          <h3 className="text-sm font-bold text-white font-display uppercase tracking-wider">
            Evidence Inquest Chat
          </h3>
        </div>
        <span className="text-[10px] font-mono text-emerald-400/60 uppercase">Strictly Grounded</span>
      </div>
      
      {/* Messages Scroll View */}
      <div className="flex-1 p-4 overflow-y-auto flex flex-col gap-3 font-sans">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`px-4 py-2.5 rounded-2xl max-w-[88%] text-xs sm:text-sm leading-relaxed ${
              msg.role === 'user' 
                ? 'bg-gradient-to-r from-emerald-600 to-cyan-500 text-black font-semibold rounded-br-none shadow-md shadow-cyan-950/50' 
                : 'bg-[#030d09]/80 border border-emerald-900/40 text-emerald-100 rounded-bl-none'
            }`}>
              {msg.role === 'assistant' ? renderTextWithCitations(msg.content, msg.citations) : msg.content}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
             <div className="px-4 py-2.5 rounded-2xl bg-[#030d09]/80 border border-emerald-900/40 text-cyan-300 rounded-bl-none flex items-center gap-2 text-xs font-mono">
                <Loader2 className="w-3.5 h-3.5 animate-spin" /> <span>Consulting evidence corpus...</span>
             </div>
          </div>
        )}
        {error && (
          <div className="flex justify-center">
            <span className="text-xs text-rose-400 bg-rose-950/60 border border-rose-900/50 px-3 py-1 rounded-full flex items-center gap-1.5 font-mono">
              <AlertCircle className="w-3 h-3"/> {error}
            </span>
          </div>
        )}
      </div>

      {/* Suggested Inquiries & Input */}
      <div className="p-3.5 border-t border-emerald-900/40 bg-[#04100d]/95">
        <div className="flex flex-wrap gap-1.5 mb-2.5">
          {getSuggestedQuestions().map((q, i) => (
            <button 
              key={i}
              onClick={() => handleSend(null, q)}
              disabled={loading}
              className="text-[11px] font-mono bg-[#061e17] border border-emerald-500/20 text-emerald-300 hover:border-cyan-400/50 hover:bg-[#0c2a21] hover:text-white px-2.5 py-1 rounded-lg transition-all text-left disabled:opacity-40 cursor-pointer"
            >
              {q}
            </button>
          ))}
        </div>
        <form onSubmit={handleSend} className="relative">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
            placeholder="Ask question regarding evidence papers..."
            className="w-full bg-[#030d09] border border-emerald-500/20 rounded-xl py-2.5 pl-4 pr-11 text-xs sm:text-sm text-[#E6FFF8] placeholder:text-emerald-400/30 focus:outline-none focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400/40 disabled:opacity-40"
          />
          <button 
            type="submit" 
            disabled={!input.trim() || loading}
            className="absolute right-1.5 top-1.5 p-2 bg-gradient-to-r from-emerald-500 to-cyan-400 text-black rounded-lg hover:brightness-110 active:scale-95 disabled:opacity-30 disabled:scale-100 transition-all cursor-pointer"
          >
            <Send className="w-3.5 h-3.5" />
          </button>
        </form>
      </div>
    </div>
  );
}
