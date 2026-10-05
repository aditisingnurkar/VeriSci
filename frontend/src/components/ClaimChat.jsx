import { useState } from 'react';
import { Send, Loader2, AlertCircle, MessageSquare, BookOpen } from 'lucide-react';

export default function ClaimChat({ verificationId, verdict }) {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Evidence inquest active. Ask any specific question regarding the methodology, participants, or findings in the retrieved papers.', citations: [] }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const getSuggestedQuestions = () => {
    let questions = ["Explain this in plain language."];
    if (verdict === "CONTRADICTED") {
      questions.unshift("Why does the evidence refute this claim?");
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
      el.classList.add('ring-2', 'ring-teal-400', 'bg-teal-950/40');
      setTimeout(() => {
        el.classList.remove('ring-2', 'ring-teal-400', 'bg-teal-950/40');
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
            className="inline-flex items-center justify-center px-1.5 py-0.5 mx-1 rounded text-xs font-mono font-bold bg-teal-950 text-teal-300 border border-teal-500/40 hover:bg-teal-400 hover:text-slate-950 transition-all cursor-pointer"
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
    <div className="science-card rounded-2xl flex flex-col h-[520px] overflow-hidden">
      {/* Top Header */}
      <div className="p-4 border-b border-slate-800/80 flex items-center justify-between bg-slate-950/60">
        <div className="flex items-center gap-2">
          <MessageSquare className="w-4 h-4 text-teal-400" />
          <h3 className="text-sm font-semibold text-white font-sans tracking-wide">
            Literature Inquest & Q&A
          </h3>
        </div>
        <span className="text-[10px] font-mono text-slate-400 uppercase">Strictly Grounded</span>
      </div>
      
      {/* Messages Scroll View */}
      <div className="flex-1 p-4 overflow-y-auto flex flex-col gap-3 font-sans">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`px-4 py-2.5 rounded-2xl max-w-[88%] text-xs sm:text-sm leading-relaxed ${
              msg.role === 'user' 
                ? 'bg-gradient-to-r from-teal-500 to-emerald-500 text-slate-950 font-medium rounded-br-none shadow-sm' 
                : 'bg-slate-950/80 border border-slate-800 text-slate-200 rounded-bl-none'
            }`}>
              {msg.role === 'assistant' ? renderTextWithCitations(msg.content, msg.citations) : msg.content}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
             <div className="px-4 py-2.5 rounded-2xl bg-slate-950/80 border border-slate-800 text-teal-300 rounded-bl-none flex items-center gap-2 text-xs font-mono">
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
      <div className="p-3.5 border-t border-slate-800/80 bg-slate-950/90">
        <div className="flex flex-wrap gap-1.5 mb-2.5">
          {getSuggestedQuestions().map((q, i) => (
            <button 
              key={i}
              onClick={() => handleSend(null, q)}
              disabled={loading}
              className="text-[11px] font-sans bg-slate-900 border border-slate-700/60 text-slate-300 hover:border-teal-500/50 hover:bg-slate-800 hover:text-white px-2.5 py-1 rounded-lg transition-all text-left disabled:opacity-40 cursor-pointer"
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
            placeholder="Ask question regarding the retrieved evidence..."
            className="w-full bg-slate-900/90 border border-slate-700/60 rounded-xl py-2.5 pl-4 pr-11 text-xs sm:text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-teal-400 focus:ring-1 focus:ring-teal-400/30 disabled:opacity-40"
          />
          <button 
            type="submit" 
            disabled={!input.trim() || loading}
            className="absolute right-1.5 top-1.5 p-2 bg-gradient-to-r from-teal-400 to-emerald-400 text-slate-950 rounded-lg hover:brightness-105 active:scale-95 disabled:opacity-30 disabled:scale-100 transition-all cursor-pointer"
          >
            <Send className="w-3.5 h-3.5" />
          </button>
        </form>
      </div>
    </div>
  );
}

