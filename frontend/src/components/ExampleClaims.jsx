import { BookOpen, ArrowUpRight } from 'lucide-react';

const exampleClaims = [
  { text: "Mice lacking c-rel are protected against experimental autoimmune encephalomyelitis.", category: "Genetics & Neuroimmunology", source: "SciFact Benchmark" },
  { text: "Vaccines cause infertility.", category: "Public Health / Clinical", source: "PubMed Direct" },
  { text: "Autophagy promotes cell survival in nutrient-deprived conditions.", category: "Cellular Biology", source: "SciFact Benchmark" },
  { text: "Regular vitamin C supplementation reduces the duration of common cold episodes.", category: "Meta-Analysis / Nutrition", source: "Cochrane Review" }
];

export default function ExampleClaims({ onSelect }) {
  return (
    <div className="mt-8 max-w-3xl mx-auto w-full text-left">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2 text-slate-400 text-xs font-mono uppercase tracking-wider">
          <BookOpen className="w-3.5 h-3.5 text-teal-400" />
          <span>Curated Empirical Inquiries:</span>
        </div>
        <span className="text-[11px] text-slate-400 hidden sm:inline">Click to load into verifier</span>
      </div>
      
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {exampleClaims.map((item, idx) => (
          <button
            key={idx}
            onClick={() => onSelect(item.text)}
            className="group text-left bg-slate-900/60 hover:bg-slate-800/80 border border-slate-800 hover:border-teal-500/40 text-slate-200 rounded-xl p-3.5 transition-all duration-200 flex items-start justify-between gap-3 cursor-pointer shadow-sm hover:shadow-md hover:shadow-teal-950/30"
          >
            <div className="flex flex-col gap-1.5">
              <div className="flex items-center gap-2">
                <span className="text-[10px] font-mono font-semibold uppercase tracking-wider text-teal-400">
                  {item.category}
                </span>
                <span className="text-[9px] font-mono text-slate-400">
                  • {item.source}
                </span>
              </div>
              <span className="text-xs sm:text-[13px] leading-relaxed font-serif text-slate-200 group-hover:text-white line-clamp-2">
                "{item.text}"
              </span>
            </div>
            <ArrowUpRight className="w-4 h-4 text-slate-500 group-hover:text-teal-300 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-all shrink-0 mt-1" />
          </button>
        ))}
      </div>
    </div>
  );
}

