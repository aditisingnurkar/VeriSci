export default function Footer() {
  return (
    <footer className="bg-white border-t border-slate-200 py-8 mt-auto">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-slate-500 text-sm">
        <p>&copy; {new Date().getFullYear()} VeriSci. Evidence-Based Scientific Claim Verification.</p>
        <p className="mt-2">Uses Machine Learning, NLP, and Retrieval on Scientific Corpora.</p>
      </div>
    </footer>
  );
}
