import { cn } from '../lib/utils';
import { AlertCircle, AlertTriangle, CheckCircle, Info } from 'lucide-react';

export default function VerdictCard({ verdict, claim, strength, reason }) {
  let colorClass = "from-slate-100 to-slate-200 text-slate-800 border-slate-300";
  let iconClass = "text-slate-500";
  let Icon = Info;
  let headline = "Analysis Complete";

  if (verdict === "SUPPORTED") {
    colorClass = "bg-green-50 border-green-200 text-green-900";
    iconClass = "text-green-600";
    Icon = CheckCircle;
    headline = "Evidence supports this claim.";
  } else if (verdict === "CONTRADICTED") {
    colorClass = "bg-red-50 border-red-200 text-red-900";
    iconClass = "text-red-600";
    Icon = AlertCircle;
    headline = "This claim is not supported — the evidence contradicts it.";
  } else if (verdict === "INSUFFICIENT") {
    colorClass = "bg-amber-50 border-amber-200 text-amber-900";
    iconClass = "text-amber-600";
    Icon = AlertTriangle;
    headline = "Not enough evidence to support or reject this claim.";
  } else if (verdict === "MIXED") {
    colorClass = "bg-amber-50 border-amber-200 text-amber-900";
    iconClass = "text-amber-600";
    Icon = AlertTriangle;
    headline = "The evidence is conflicting.";
  }

  return (
    <div className={cn("rounded-2xl border p-8 sm:p-12 shadow-sm mb-10", colorClass)} role="status" aria-live="polite">
      <div className="flex flex-col sm:flex-row items-start sm:items-center gap-6 mb-8">
        <Icon className={cn("w-16 h-16 shrink-0", iconClass)} />
        <div>
          <h1 className="text-3xl sm:text-4xl font-bold leading-tight mb-2">
            {headline}
          </h1>
          <p className="text-lg opacity-90 font-medium">
            {reason}
          </p>
        </div>
      </div>
      
      <div className="bg-white/60 p-6 rounded-xl border border-black/5 mt-6">
        <h2 className="text-sm font-bold uppercase tracking-widest opacity-60 mb-2 flex items-center gap-2">
          Claim Under Verification
        </h2>
        <div className="text-2xl font-semibold italic border-l-4 border-current pl-4 py-1">
          "{claim}"
        </div>
      </div>
      
      {verdict !== "INSUFFICIENT" && (
        <div className="mt-6 flex items-center gap-2">
          <span className="text-sm font-semibold uppercase tracking-widest opacity-70">Evidence Strength:</span>
          <span className="font-bold uppercase bg-white/80 px-3 py-1 rounded-md text-sm shadow-sm">{strength}</span>
        </div>
      )}
    </div>
  );
}
