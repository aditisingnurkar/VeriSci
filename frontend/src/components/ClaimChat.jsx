import { useState } from 'react';
import { Send, Sparkles, Loader2, AlertCircle } from 'lucide-react';

export default function ClaimChat({ verificationId, verdict }) {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'I can help you understand this claim based on the retrieved evidence. What would you like to know?', citations: [] }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const getSuggestedQuestions = () => {
    let questions = ["Explain this in simple language."];
    if (verdict === "CONTRADICTED") {
      questions.unshift("Why is this claim considered contradicted?");
      questions.push("What evidence supports the claim?");
    } else if (verdict === "SUPPORTED") {
      questions.unshift("What evidence supports the claim?");
      questions.push("What evidence contradicts it?");
    } else if (verdict === "MIXED") {
      questions.unshift("Why is the evidence conflicting?");
      questions.push("Which study is the strongest?");
    } else {
      questions.push("Is there any relevant information?");
    }
    return questions.slice(0, 3);
  };

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
            className="inline-flex items-center justify-center px-1.5 py-0.5 mx-1 rounded text-xs font-bold bg-blue-100 text-blue-700 hover:bg-blue-200 transition-colors"
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
      setError("AI assistant unavailable.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm flex flex-col h-[500px]">
      <div className="p-4 border-b border-slate-100 flex items-center justify-between bg-slate-50 rounded-t-2xl">
        <div className="flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-blue-600" />
          <h3 className="font-semibold text-slate-900">Ask about this claim</h3>
        </div>
        <span className="text-xs text-slate-500 italic">Answered from evidence only</span>
      </div>
      
      <div className="flex-1 p-4 overflow-y-auto flex flex-col gap-4">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`px-4 py-2 rounded-2xl max-w-[85%] text-sm ${
              msg.role === 'user' ? 'bg-blue-600 text-white rounded-br-sm' : 'bg-slate-100 text-slate-800 rounded-bl-sm'
            }`}>
              {msg.role === 'assistant' ? renderTextWithCitations(msg.content, msg.citations) : msg.content}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
             <div className="px-4 py-3 rounded-2xl bg-slate-100 text-slate-500 rounded-bl-sm flex items-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin" /> <span className="text-xs">Thinking...</span>
             </div>
          </div>
        )}
        {error && (
          <div className="flex justify-center">
            <span className="text-xs text-red-500 bg-red-50 px-2 py-1 rounded flex items-center gap-1">
              <AlertCircle className="w-3 h-3"/> {error}
            </span>
          </div>
        )}
      </div>

      <div className="p-4 border-t border-slate-100 bg-white rounded-b-2xl">
        <div className="flex flex-wrap gap-2 mb-3">
          {getSuggestedQuestions().map((q, i) => (
            <button 
              key={i}
              onClick={() => handleSend(null, q)}
              disabled={loading}
              className="text-xs bg-slate-50 border border-slate-200 text-slate-600 hover:bg-blue-50 hover:text-blue-700 px-3 py-1.5 rounded-full transition-colors text-left disabled:opacity-50"
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
            placeholder="Ask a question..."
            className="w-full bg-slate-50 border border-slate-200 rounded-full py-2.5 pl-4 pr-10 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50"
          />
          <button 
            type="submit" 
            disabled={!input.trim() || loading}
            className="absolute right-1.5 top-1.5 p-1.5 bg-blue-600 text-white rounded-full hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Send className="w-3.5 h-3.5" />
          </button>
        </form>
      </div>
    </div>
  );
}
