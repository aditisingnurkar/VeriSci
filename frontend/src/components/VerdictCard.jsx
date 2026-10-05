import { cn } from '../lib/utils';
import { AlertCircle, AlertTriangle, CheckCircle, ShieldCheck, Zap, Info } from 'lucide-react';

export default function VerdictCard({ verdict, claim, strength, reason }) {
  let theme = {
    bg: "bg-[#061e17]",
    border: "border-emerald-500/30",
    glow: "glow-emerald",
    iconColor: "text-emerald-400",
    badgeBg: "bg-emerald-500/20 text-emerald-300 border-emerald-500/40",
    headline: "Evidence Supports Claim",
    subtitle: "Empirical scientific literature corroborates this hypothesis.",
    Icon: CheckCircle,
    accentGlow: "from-emerald-500/20 via-emerald-500/5 to-transparent",
    barColor: "bg-emerald-400"
  };

  if (verdict === "SUPPORTED") {
    theme = {
      bg: "bg-[#051f18]",
      border: "border-emerald-400/40",
      glow: "glow-emerald",
      iconColor: "text-emerald-300",
      badgeBg: "bg-emerald-500/20 text-emerald-300 border-emerald-400/50",
      headline: "Evidence Supports This Claim",
      subtitle: "The retrieved peer-reviewed scientific literature affirms this claim.",
      Icon: CheckCircle,
      accentGlow: "from-emerald-500/25 via-emerald-900/10 to-transparent",
      barColor: "bg-emerald-400"
    };
  } else if (verdict === "CONTRADICTED") {
    theme = {
      bg: "bg-[#20090e]",
      border: "border-rose-500/50",
      glow: "glow-crimson",
      iconColor: "text-rose-400",
      badgeBg: "bg-rose-500/20 text-rose-300 border-rose-500/50",
      headline: "Evidence Contradicts This Claim",
      subtitle: "The retrieved scientific literature directly refutes this claim.",
      Icon: AlertCircle,
      accentGlow: "from-rose-500/25 via-rose-950/20 to-transparent",
      barColor: "bg-rose-400"
    };
  } else if (verdict === "INSUFFICIENT") {
    theme = {
      bg: "bg-[#201506]",
      border: "border-amber-500/40",
      glow: "glow-amber",
      iconColor: "text-amber-400",
      badgeBg: "bg-amber-500/20 text-amber-300 border-amber-500/40",
      headline: "Insufficient Evidence Identified",
      subtitle: "Not enough high-relevance scientific evidence was found to verify or refute this claim.",
      Icon: AlertTriangle,
      accentGlow: "from-amber-500/20 via-amber-950/20 to-transparent",
      barColor: "bg-amber-400"
    };
  } else if (verdict === "MIXED") {
    theme = {
      bg: "bg-[#1c1806]",
      border: "border-amber-400/40",
      glow: "glow-amber",
      iconColor: "text-amber-300",
      badgeBg: "bg-amber-500/20 text-amber-200 border-amber-400/40",
      headline: "Conflicting Evidence Detected",
      subtitle: "Literature presents conflicting findings across distinct studies.",
      Icon: AlertTriangle,
      accentGlow: "from-amber-400/20 via-amber-950/20 to-transparent",
      barColor: "bg-amber-400"
    };
  }

  const { Icon } = theme;

  return (
    <div 
      className={cn(
        "relative rounded-3xl border p-7 sm:p-10 shadow-2xl backdrop-blur-xl overflow-hidden transition-all duration-300",
        theme.bg,
        theme.border,
        theme.glow
      )} 
      role="status" 
      aria-live="polite"
    >
      {/* Background Gradient Slash */}
      <div className={cn("absolute inset-0 bg-gradient-to-br opacity-50 pointer-events-none", theme.accentGlow)} />

      <div className="relative z-10">
        {/* Top Status Line */}
        <div className="flex flex-wrap items-center justify-between gap-3 mb-6">
          <div className={cn("inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full border text-xs font-mono font-bold uppercase tracking-wider", theme.badgeBg)}>
            <Icon className="w-4 h-4 shrink-0" />
            <span>VERDICT // {verdict}</span>
          </div>

          {strength && verdict !== "INSUFFICIENT" && (
            <div className="flex items-center gap-2 font-mono text-xs text-emerald-300/80 bg-[#040e0b]/80 border border-emerald-900/60 px-3.5 py-1.5 rounded-full">
              <span className="text-emerald-500 uppercase tracking-widest text-[10px]">Confidence Strength:</span>
              <span className="font-bold text-white uppercase">{strength}</span>
              <span className={cn("w-2 h-2 rounded-full", theme.barColor)} />
            </div>
          )}
        </div>

        {/* Big Verdict Headline */}
        <div className="flex items-start gap-4 mb-6">
          <div>
            <h1 className="text-2xl sm:text-4xl font-extrabold text-[#F0FDF9] leading-tight font-display mb-2">
              {theme.headline}
            </h1>
            <p className="text-sm sm:text-base text-emerald-100/80 font-sans leading-relaxed">
              {reason || theme.subtitle}
            </p>
          </div>
        </div>
        
        {/* Claim Prompt Block */}
        <div className="mt-6 p-4 sm:p-5 rounded-2xl bg-[#030d09]/90 border border-emerald-900/50 shadow-inner">
          <div className="flex items-center justify-between text-[11px] font-mono text-emerald-400/60 uppercase tracking-wider mb-2">
            <span>CLAIM_VERIFICATION_TARGET</span>
            <span className="text-cyan-400/70">NLP_GROUNDED</span>
          </div>
          <div className="text-base sm:text-lg font-medium text-emerald-50 italic border-l-2 border-cyan-400 pl-3.5 font-sans">
            "{claim}"
          </div>
        </div>

      </div>
    </div>
  );
}
