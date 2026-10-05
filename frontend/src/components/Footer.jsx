import { ShieldCheck, Cpu, Database } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="border-t border-emerald-950/80 bg-[#030c09]/90 backdrop-blur-md py-8 mt-auto text-emerald-100/60 text-xs font-mono">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
          <span className="text-emerald-300 font-semibold uppercase tracking-wider font-display">VeriSci Core // v2.4</span>
          <span className="text-emerald-600">|</span>
          <span>Automated Evidence Verification System</span>
        </div>
        
        <div className="flex items-center gap-4 text-emerald-400/70">
          <span className="flex items-center gap-1.5 hover:text-emerald-300 transition-colors">
            <Database className="w-3.5 h-3.5 text-cyan-400" /> SciFact + PubMed
          </span>
          <span className="text-emerald-800">•</span>
          <span className="flex items-center gap-1.5 hover:text-emerald-300 transition-colors">
            <Cpu className="w-3.5 h-3.5 text-emerald-400" /> NLI Cross-Encoder
          </span>
        </div>

        <div className="text-emerald-500/50 text-[11px]">
          &copy; {new Date().getFullYear()} VeriSci Engine. For academic & research evaluation.
        </div>
      </div>
    </footer>
  );
}
