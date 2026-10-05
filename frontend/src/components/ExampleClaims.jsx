import { Lightbulb } from 'lucide-react';

const exampleClaims = [
  "Mice lacking c-rel are protected against experimental autoimmune encephalomyelitis.",
  "Vaccines cause infertility.",
  "Vaccines do not cause infertility.",
  "The moon is made of cheese and pasta."
];

export default function ExampleClaims({ onSelect }) {
  return (
    <div className="mt-8 max-w-3xl mx-auto">
      <div className="flex items-center text-slate-500 mb-3 text-sm font-medium">
        <Lightbulb className="w-4 h-4 mr-2" />
        Try an example claim:
      </div>
      <div className="flex flex-wrap gap-2">
        {exampleClaims.map((claim, idx) => (
          <button
            key={idx}
            onClick={() => onSelect(claim)}
            className="text-left bg-white border border-slate-200 hover:border-blue-300 hover:bg-blue-50 text-slate-700 rounded-full px-4 py-2 text-sm transition-colors"
          >
            {claim}
          </button>
        ))}
      </div>
    </div>
  );
}
