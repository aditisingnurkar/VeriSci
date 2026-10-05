import { Link } from 'react-router-dom';
import { Microscope, Activity, Sparkles, BookOpen } from 'lucide-react';

export default function Navbar() {
  return (
    <header className="sticky top-0 z-50 bg-[#051410]/80 backdrop-blur-xl border-b border-[#00F5D4]/15">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          
          {/* Logo & Brand */}
          <Link to="/" className="flex items-center gap-3 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#00F5D4]/20 to-[#10B981]/10 border border-[#00F5D4]/40 flex items-center justify-center shadow-[0_0_15px_-3px_rgba(0,245,212,0.3)] group-hover:border-[#00F5D4] group-hover:shadow-[0_0_20px_0_rgba(0,245,212,0.5)] transition-all duration-300">
              <Microscope className="h-5 w-5 text-[#00F5D4]" />
            </div>
            <div className="flex flex-col">
              <div className="flex items-center gap-1.5">
                <span className="font-display font-bold text-xl tracking-tight text-white group-hover:text-[#00F5D4] transition-colors">
                  Veri<span className="text-[#00F5D4]">Sci</span>
                </span>
                <span className="text-[10px] font-mono uppercase px-1.5 py-0.5 rounded bg-[#00F5D4]/10 text-[#00F5D4] border border-[#00F5D4]/30 font-semibold">
                  v2.0
                </span>
              </div>
              <span className="text-[10px] font-mono text-[#809D94] uppercase tracking-widest hidden sm:block">
                Evidence Intelligence Engine
              </span>
            </div>
          </Link>

          {/* Center / Right Meta */}
          <div className="flex items-center gap-6">
            {/* Live Engine Indicator */}
            <div className="hidden md:flex items-center gap-2 px-3 py-1 rounded-full bg-[#0B251E] border border-[#00F5D4]/20 text-xs font-mono text-[#809D94]">
              <span className="w-2 h-2 rounded-full bg-[#00F5D4] animate-pulse"></span>
              <span className="text-[#E6FFF8]">SciFact</span>
              <span className="text-[#809D94]">+</span>
              <span className="text-[#00F5D4] font-semibold">PubMed Live</span>
            </div>

            {/* Navigation Links */}
            <nav className="flex items-center space-x-1 sm:space-x-3 text-sm font-medium">
              <Link 
                to="/" 
                className="px-3 py-1.5 rounded-lg text-[#E6FFF8] hover:text-[#00F5D4] hover:bg-[#0C2D24] transition-all font-mono text-xs uppercase tracking-wider"
              >
                Verifier
              </Link>
              <a 
                href="https://github.com/allenai/scifact" 
                target="_blank" 
                rel="noopener noreferrer"
                className="px-3 py-1.5 rounded-lg text-[#809D94] hover:text-[#00F5D4] hover:bg-[#0C2D24] transition-all font-mono text-xs uppercase tracking-wider hidden sm:flex items-center gap-1.5"
              >
                <BookOpen className="w-3.5 h-3.5 text-[#00F5D4]" />
                Corpus Docs
              </a>
            </nav>
          </div>

        </div>
      </div>
    </header>
  );
}
