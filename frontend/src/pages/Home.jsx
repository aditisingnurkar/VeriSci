import { useState } from 'react';
import ClaimInput from '../components/ClaimInput';
import ExampleClaims from '../components/ExampleClaims';
import { ShieldCheck } from 'lucide-react';

export default function Home() {
  const [selectedClaim, setSelectedClaim] = useState("");

  return (
    <main className="flex-grow flex flex-col items-center justify-center px-4 py-12 sm:px-6 lg:px-8">
      <div className="text-center w-full max-w-4xl mx-auto mb-12">
        <div className="inline-flex items-center justify-center p-3 bg-blue-100 rounded-full mb-6">
          <ShieldCheck className="w-12 h-12 text-blue-600" />
        </div>
        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-slate-900 tracking-tight mb-6">
          Verify Scientific Claims <br className="hidden sm:block" />
          <span className="text-blue-600">With Evidence</span>
        </h1>
        <p className="text-lg sm:text-xl text-slate-600 max-w-2xl mx-auto mb-10 leading-relaxed">
          VeriSci retrieves real scientific literature and uses machine learning to evaluate whether a claim is supported, contradicted, or lacks sufficient evidence.
        </p>
        
        <ClaimInput initialClaim={selectedClaim} />
        <ExampleClaims onSelect={setSelectedClaim} />
      </div>
    </main>
  );
}
