import { cn } from '../lib/utils';
import { CheckCircle2, Circle, Loader2 } from 'lucide-react';

export default function AnalysisProgress({ currentStep }) {
  const steps = [
    { id: 1, name: 'Claim Received', desc: 'Parsing target claim syntax & query tokens' },
    { id: 2, name: 'Searching Evidence', desc: 'Querying SciFact 5.1k corpus & live PubMed' },
    { id: 3, name: 'Inference Classification', desc: 'Running Cross-Encoder NLI transformer' },
    { id: 4, name: 'Verdict Aggregation', desc: 'Synthesizing evidence strength and grounded citations' },
  ];

  return (
    <div className="max-w-2xl mx-auto w-full p-8 bg-[#061813]/90 rounded-3xl border border-emerald-500/20 shadow-2xl backdrop-blur-xl">
      <h2 className="text-xl font-bold text-white mb-8 text-center font-display uppercase tracking-wider">
        Verifying Claim Protocol
      </h2>
      
      <div className="space-y-6 relative before:absolute before:inset-0 before:ml-4 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-emerald-500/30 before:to-transparent">
        {steps.map((step) => {
          const isComplete = currentStep > step.id;
          const isCurrent = currentStep === step.id;

          return (
            <div key={step.id} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group">
              
              <div className={cn(
                "flex items-center justify-center w-8 h-8 rounded-full border-2 bg-[#040e0b] shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 transition-colors",
                isComplete ? "border-emerald-400 text-emerald-400" : 
                isCurrent ? "border-cyan-400 text-cyan-400 animate-pulse" : 
                "border-emerald-950 text-emerald-800"
              )}>
                {isComplete ? <CheckCircle2 className="w-4 h-4" /> : 
                 isCurrent ? <Loader2 className="w-4 h-4 animate-spin" /> : 
                 <Circle className="w-3.5 h-3.5" />}
              </div>
              
              <div className={cn(
                "w-[calc(100%-3rem)] md:w-[calc(50%-2rem)] p-4 rounded-2xl border transition-all",
                isCurrent ? "border-cyan-400/50 bg-[#0c2a21] shadow-lg shadow-cyan-950/30" :
                isComplete ? "border-emerald-900/50 bg-[#051712]" :
                "border-emerald-950/40 bg-[#030d09]"
              )}>
                <div className="flex items-center justify-between mb-1">
                  <h3 className={cn("font-bold text-xs font-mono uppercase tracking-wider", isCurrent ? "text-cyan-300" : isComplete ? "text-emerald-200" : "text-emerald-700")}>
                    {step.name}
                  </h3>
                </div>
                <div className="text-emerald-400/70 text-xs font-sans">{step.desc}</div>
              </div>
              
            </div>
          );
        })}
      </div>
    </div>
  );
}
