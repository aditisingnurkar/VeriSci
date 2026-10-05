import { Link } from 'react-router-dom';
import { Microscope, BookOpen, Sparkles, ShieldCheck } from 'lucide-react';

export default function Navbar() {
  return (
    <header className="sticky top-0 z-50 bg-[#070d13]/85 backdrop-blur-xl border-b border-slate-800/60 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          
          {/* Logo & Brand */}
          <Link to="/" className="flex items-center gap-3 group">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-teal-500/20 to-emerald-500/10 border border-teal-500/30 flex items-center justify-center text-teal-400 group-hover:border-teal-400/60 group-hover:text-teal-300 transition-all duration-300 shadow-inner">
              <Microscope className="h-4 w-4" />
            </div>
            <div className="flex flex-col">
              <div className="flex items-center gap-2">
                <span className="font-display font-bold text-lg tracking-tight text-white group-hover:text-teal-300 transition-colors">
                  Veri<span className="text-teal-400">Sci</span>
                </span>
                <span className="text-[10px] font-mono font-medium px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700/60">
                  Research Edition
                </span>
              </div>
              <span className="text-[10px] font-mono text-slate-400 tracking-wider hidden sm:block">
                Biomedical Evidence Verification System
              </span>
            </div>
          </Link>

          {/* Center / Right Meta */}
          <div className="flex items-center gap-4 sm:gap-6">
            {/* Live Data Badge */}
            <div className="hidden md:flex items-center gap-2 px-3 py-1 rounded-full bg-slate-900/90 border border-slate-800 text-xs font-mono text-slate-400">
              <span className="w-1.5 h-1.5 rounded-full bg-teal-400 animate-pulse"></span>
              <span className="text-slate-200">SciFact</span>
              <span className="text-slate-600">/</span>
              <span className="text-teal-300 font-medium">PubMed Live</span>
            </div>

            {/* Navigation Links */}
            <nav className="flex items-center space-x-1 sm:space-x-2 text-sm">
              <Link 
                to="/" 
                className="px-3 py-1.5 rounded-lg text-slate-200 hover:text-white hover:bg-slate-800/70 transition-all font-sans text-xs font-semibold"
              >
                Verification Desk
              </Link>
              <a 
                href="https://github.com/allenai/scifact" 
                target="_blank" 
                rel="noopener noreferrer"
                className="px-3 py-1.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800/70 transition-all font-sans text-xs flex items-center gap-1.5"
              >
                <BookOpen className="w-3.5 h-3.5 text-teal-400" />
                <span className="hidden sm:inline">Corpus</span> Docs
              </a>
            </nav>
          </div>

        </div>
      </div>
    </header>
  );
}

