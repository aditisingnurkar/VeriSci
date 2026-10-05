import { cn } from '../lib/utils';
import { AlertCircle, AlertTriangle, CheckCircle2, ShieldCheck, HelpCircle } from 'lucide-react';

export default function VerdictCard({ verdict, claim, strength, reason }) {
  let theme = {
    bg: "bg-slate-900/80",
    border: "border-emerald-500/30",
    iconColor: "text-emerald-400",
    badgeBg: "bg-emerald-950/80 text-emerald-300 border-emerald-500/40",
    headline: "Evidence Supports Claim",
    subtitle: "Empirical scientific literature corroborates this hypothesis.",
    Icon: CheckCircle2,
    accentBorder: "border-l-emerald-400",
    strengthDot: "bg-emerald-400"
  };

  if (verdict === "SUPPORTED") {
    theme = {
      bg: "bg-[#081512]/85",
      border: "border-emerald-500/40",
      iconColor: "text-emerald-300",
      badgeBg: "bg-emerald-950/90 text-emerald-300 border-emerald-400/50",
      headline: "Evidence Supports This Claim",
      subtitle: "The retrieved peer-reviewed scientific literature affirms this hypothesis.",
      Icon: CheckCircle2,
      accentBorder: "border-l-emerald-400",
      strengthDot: "bg-emerald-400"
    };
  } else if (verdict === "CONTRADICTED") {
    theme = {
      bg: "bg-[#18090d]/85",
      border: "border-rose-500/40",
      iconColor: "text-rose-400",
      badgeBg: "bg-rose-950/90 text-rose-300 border-rose-500/50",
      headline: "Evidence Contradicts This Claim",
      subtitle: "The retrieved scientific literature directly refutes this claim.",
      Icon: AlertCircle,
      accentBorder: "border-l-rose-400",
      strengthDot: "bg-rose-400"
    };
  } else if (verdict === "INSUFFICIENT") {
    theme = {
      bg: "bg-[#181308]/85",
      border: "border-amber-500/40",
      iconColor: "text-amber-400",
      badgeBg: "bg-amber-950/90 text-amber-300 border-amber-500/40",
      headline: "Insufficient Evidence Identified",
      subtitle: "Not enough high-relevance scientific evidence was found to verify or refute this claim.",
      Icon: HelpCircle,
      accentBorder: "border-l-amber-400",
      strengthDot: "bg-amber-400"
    };
  } else if (verdict === "MIXED") {
    theme = {
      bg: "bg-[#171408]/85",
      border: "border-amber-400/40",
      iconColor: "text-amber-300",
      badgeBg: "bg-amber-950/90 text-amber-200 border-amber-400/40",
      headline: "Conflicting Evidence Detected",
      subtitle: "Literature presents conflicting findings across distinct studies.",
      Icon: AlertTriangle,
      accentBorder: "border-l-amber-400",
      strengthDot: "bg-amber-400"
    };
  }

  const { Icon } = theme;

  return (
    <div 
      className={cn(
        "relative rounded-2xl border p-6 sm:p-8 shadow-xl backdrop-blur-xl overflow-hidden transition-all duration-300",
        theme.bg,
        theme.border
      )} 
      role="status" 
      aria-live="polite"
    >
      <div className="relative z-10">
        {/* Top Status Line */}
        <div className="flex flex-wrap items-center justify-between gap-3 mb-5">
          <div className={cn("inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full border text-xs font-mono font-bold tracking-wide shadow-sm", theme.badgeBg)}>
            <Icon className="w-4 h-4 shrink-0" />
            <span>VERDICT: {verdict}</span>
          </div>

          {strength && verdict !== "INSUFFICIENT" && (
            <div className="flex items-center gap-2 font-mono text-xs text-slate-300 bg-slate-950/80 border border-slate-800 px-3 py-1 rounded-full">
              <span className="text-slate-400 uppercase text-[10px] tracking-wider">Confidence:</span>
              <span className="font-semibold text-white">{strength}</span>
              <span className={cn("w-2 h-2 rounded-full", theme.strengthDot)} />
            </div>
          )}
        </div>

        {/* Verdict Headline & Subtitle */}
        <div className="mb-6">
          <h1 className="text-2xl sm:text-3xl lg:text-4xl font-serif font-normal text-white leading-tight mb-2">
            {theme.headline}
          </h1>
          <p className="text-sm sm:text-base text-slate-300 font-sans leading-relaxed">
            {reason || theme.subtitle}
          </p>
        </div>
        
        {/* Claim Target Quote Block */}
        <div className="p-4 sm:p-5 rounded-xl bg-slate-950/70 border border-slate-800/80 shadow-inner">
          <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider mb-1.5">
            Evaluated Claim
          </div>
          <div className={cn("text-base sm:text-lg font-serif italic text-slate-100 pl-3 border-l-2", theme.accentBorder)}>
            "{claim}"
          </div>
        </div>

      </div>
    </div>
  );
}

