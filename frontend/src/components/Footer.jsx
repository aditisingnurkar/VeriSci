import { ShieldCheck, Cpu, Database } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="border-t border-slate-800/80 bg-[#060a0e]/95 backdrop-blur-md py-8 mt-auto text-slate-400 text-xs font-sans">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-2 font-mono text-[11px]">
          <span className="w-1.5 h-1.5 rounded-full bg-teal-400" />
          <span className="text-slate-200 font-semibold">VeriSci</span>
          <span className="text-slate-600">/</span>
          <span>Empirical Biomedical Verification</span>
        </div>
        
        <div className="flex items-center gap-4 text-slate-400 font-mono text-[11px]">
          <span className="flex items-center gap-1.5">
            <Database className="w-3.5 h-3.5 text-teal-400" /> SciFact + PubMed Live
          </span>
          <span className="text-slate-700">•</span>
          <span className="flex items-center gap-1.5">
            <Cpu className="w-3.5 h-3.5 text-teal-400" /> Transformer NLI
          </span>
        </div>

        <div className="text-slate-400 text-[11px] font-sans">
          &copy; {new Date().getFullYear()} VeriSci. Open-access research & literature synthesis.
        </div>
      </div>
    </footer>
  );
}

