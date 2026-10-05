import { BookOpen } from 'lucide-react';

export default function ExplanationCard({ explanation }) {
  return (
    <div className="bg-slate-900 text-slate-50 p-6 rounded-2xl shadow-sm w-full relative overflow-hidden">
      <div className="absolute top-0 right-0 p-8 opacity-5">
        <BookOpen className="w-48 h-48" />
      </div>
      
      <div className="relative z-10">
        <div className="flex items-center gap-2 mb-4 border-b border-slate-700 pb-4">
          <BookOpen className="w-5 h-5 text-blue-400" />
          <h3 className="text-lg font-semibold text-white">Explanation (Phase 5 RAG Placeholder)</h3>
        </div>
        
        <p className="text-slate-300 leading-relaxed text-sm">
          {explanation}
        </p>
      </div>
    </div>
  );
}
