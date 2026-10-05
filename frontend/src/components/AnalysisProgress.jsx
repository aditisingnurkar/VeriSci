import { cn } from '../lib/utils';
import { CheckCircle2, Circle, Loader2 } from 'lucide-react';

export default function AnalysisProgress({ currentStep }) {
  const steps = [
    { id: 1, name: 'Claim Received', desc: 'Parsing your claim...' },
    { id: 2, name: 'Searching Evidence', desc: 'Querying scientific corpus (SciFact)' },
    { id: 3, name: 'Analyzing Evidence', desc: 'Running ML classifier on retrieved papers' },
    { id: 4, name: 'Preparing Verdict', desc: 'Aggregating results and generating explanation' },
  ];

  return (
    <div className="max-w-2xl mx-auto w-full p-8 bg-white rounded-3xl border border-slate-200 shadow-sm">
      <h2 className="text-2xl font-bold text-slate-900 mb-8 text-center">Verifying Claim</h2>
      
      <div className="space-y-6 relative before:absolute before:inset-0 before:ml-4 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-slate-200 before:to-transparent">
        {steps.map((step) => {
          const isComplete = currentStep > step.id;
          const isCurrent = currentStep === step.id;
          const isPending = currentStep < step.id;

          return (
            <div key={step.id} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
              
              <div className={cn(
                "flex items-center justify-center w-8 h-8 rounded-full border-2 bg-white shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2",
                isComplete ? "border-green-500 text-green-500" : 
                isCurrent ? "border-blue-600 text-blue-600" : 
                "border-slate-300 text-slate-300"
              )}>
                {isComplete ? <CheckCircle2 className="w-5 h-5" /> : 
                 isCurrent ? <Loader2 className="w-5 h-5 animate-spin" /> : 
                 <Circle className="w-5 h-5" />}
              </div>
              
              <div className="w-[calc(100%-3rem)] md:w-[calc(50%-2rem)] p-4 rounded-xl border border-slate-200 bg-slate-50 shadow-sm transition-all">
                <div className="flex items-center justify-between mb-1">
                  <h3 className={cn("font-bold text-sm", isCurrent ? "text-blue-600" : "text-slate-900")}>
                    {step.name}
                  </h3>
                </div>
                <div className="text-slate-500 text-xs">{step.desc}</div>
              </div>
              
            </div>
          );
        })}
      </div>
    </div>
  );
}
