import { Link } from 'react-router-dom';
import { Microscope } from 'lucide-react';

export default function Navbar() {
  return (
    <nav className="bg-white border-b border-slate-200 sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          <Link to="/" className="flex items-center space-x-2">
            <Microscope className="h-8 w-8 text-blue-600" />
            <span className="font-bold text-xl tracking-tight text-slate-900">VeriSci</span>
          </Link>
          <div className="hidden sm:flex space-x-8">
            <Link to="/" className="text-slate-600 hover:text-blue-600 transition-colors font-medium">
              Home
            </Link>
            <a href="#" className="text-slate-600 hover:text-blue-600 transition-colors font-medium">
              About
            </a>
            <a href="#" className="text-slate-600 hover:text-blue-600 transition-colors font-medium">
              Methodology
            </a>
          </div>
        </div>
      </div>
    </nav>
  );
}
