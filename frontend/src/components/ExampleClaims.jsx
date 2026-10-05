import { Sparkles, ArrowUpRight } from 'lucide-react';

const exampleClaims = [
  { text: "Mice lacking c-rel are protected against experimental autoimmune encephalomyelitis.", category: "Genetics" },
  { text: "Vaccines cause infertility.", category: "Immunology" },
  { text: "Vaccines do not cause infertility.", category: "Clinical" },
  { text: "Autophagy promotes cell survival in nutrient-deprived conditions.", category: "Cell Biology" }
];

export default function ExampleClaims({ onSelect }) {
  return (
    <div className="mt-8 max-w-3xl mx-auto w-full">
      <div className="flex items-center gap-2 text-emerald-400/80 mb-3 text-xs font-mono uppercase tracking-wider">
        <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
        <span>Sample Evaluation Benchmarks:</span>
      </div>
      
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
        {exampleClaims.map((item, idx) => (
          <button
            key={idx}
            onClick={() => onSelect(item.text)}
            className="group text-left bg-[#071d17]/80 hover:bg-[#0c2a21] border border-emerald-500/20 hover:border-cyan-400/50 text-emerald-100/90 rounded-xl p-3.5 text-xs sm:text-sm transition-all duration-200 flex items-start justify-between gap-2 cursor-pointer shadow-sm hover:shadow-cyan-900/20"
          >
            <div className="flex flex-col gap-1">
              <span className="text-[10px] font-mono font-semibold uppercase tracking-wider text-cyan-400/80 group-hover:text-cyan-300">
                {item.category}
              </span>
              <span className="leading-snug font-sans text-emerald-50/90 group-hover:text-white line-clamp-2">
                "{item.text}"
              </span>
            </div>
            <ArrowUpRight className="w-4 h-4 text-emerald-500/50 group-hover:text-cyan-400 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-all shrink-0 mt-0.5" />
          </button>
        ))}
      </div>
    </div>
  );
}
