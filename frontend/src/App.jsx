import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import Home from './pages/Home';
import Analysis from './pages/Analysis';
import Results from './pages/Results';

function App() {
  return (
    <Router>
      <div className="flex flex-col min-h-screen relative text-slate-100">
        {/* Atmospheric Scientific Background Canvas with Soft Masking */}
        <div className="bg-canvas-container" aria-hidden="true">
          <img 
            src="/scientific_bg.jpg" 
            alt="Scientific cellular and molecular background" 
            className="bg-canvas-image" 
          />
          <div className="bg-canvas-gradient" />
          <div className="absolute inset-0 bg-subtle-dots opacity-40" />
        </div>

        {/* Foreground Content */}
        <div className="relative z-10 flex flex-col min-h-screen">
          <Navbar />
          <div className="flex-grow flex flex-col">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/analyze" element={<Analysis />} />
              <Route path="/results" element={<Results />} />
            </Routes>
          </div>
          <Footer />
        </div>
      </div>
    </Router>
  );
}

export default App;

