import { useState } from 'react';
import { MessageSquare, Send, Sparkles } from 'lucide-react';

export default function ClaimChat() {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'I can help you understand this claim based on the retrieved evidence. What would you like to know?' }
  ]);
  const [input, setInput] = useState('');

  const suggestedQuestions = [
    "Why is this claim considered contradicted?",
    "What evidence supports the claim?",
    "Which study is the strongest?",
    "Explain this in simple language."
  ];

  const handleSend = (e, text = input) => {
    if (e) e.preventDefault();
    if (!text.trim()) return;
    
    setMessages([...messages, { role: 'user', content: text }]);
    setInput('');
    
    // Mock response for UI
    setTimeout(() => {
      setMessages(prev => [...prev, { role: 'assistant', content: "This is a UI placeholder. In Phase 5, this will be connected to the RAG system to provide evidence-grounded answers." }]);
    }, 1000);
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm flex flex-col h-[500px]">
      <div className="p-4 border-b border-slate-100 flex items-center gap-2 bg-slate-50 rounded-t-2xl">
        <Sparkles className="w-5 h-5 text-blue-600" />
        <h3 className="font-semibold text-slate-900">Ask about this claim</h3>
      </div>
      
      <div className="flex-1 p-4 overflow-y-auto flex flex-col gap-4">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`px-4 py-2 rounded-2xl max-w-[85%] text-sm ${
              msg.role === 'user' ? 'bg-blue-600 text-white rounded-br-sm' : 'bg-slate-100 text-slate-800 rounded-bl-sm'
            }`}>
              {msg.content}
            </div>
          </div>
        ))}
      </div>

      <div className="p-4 border-t border-slate-100 bg-white rounded-b-2xl">
        <div className="flex flex-wrap gap-2 mb-3">
          {suggestedQuestions.map((q, i) => (
            <button 
              key={i}
              onClick={() => handleSend(null, q)}
              className="text-xs bg-slate-50 border border-slate-200 text-slate-600 hover:bg-blue-50 hover:text-blue-700 px-3 py-1.5 rounded-full transition-colors text-left"
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
            placeholder="Ask a question..."
            className="w-full bg-slate-50 border border-slate-200 rounded-full py-2.5 pl-4 pr-10 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <button 
            type="submit" 
            disabled={!input.trim()}
            className="absolute right-1.5 top-1.5 p-1.5 bg-blue-600 text-white rounded-full hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Send className="w-3.5 h-3.5" />
          </button>
        </form>
      </div>
    </div>
  );
}
