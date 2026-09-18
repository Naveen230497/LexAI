import ReactMarkdown from 'react-markdown';
import { FileText, AlertTriangle, CheckCircle, Sparkles, AlertCircle } from 'lucide-react';
import type { SimplificationResult } from '../lib/api';

interface AnalysisPanelProps {
  simplification: SimplificationResult;
}

export default function AnalysisPanel({ simplification }: AnalysisPanelProps): JSX.Element {
  const { plain_english, key_points, unusual_clauses, document_type } = simplification;

  return (
    <article className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
      
      {/* Header Card */}
      <section className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-blue-600 to-indigo-700 p-8 sm:p-10 text-white shadow-lg">
        <div className="absolute top-0 right-0 -mt-8 -mr-8 opacity-10">
          <FileText className="w-64 h-64" />
        </div>
        <div className="relative z-10">
          <div className="inline-flex items-center gap-2 rounded-full bg-white/20 px-4 py-1.5 text-sm font-bold backdrop-blur-md mb-6 border border-white/20">
            <Sparkles className="h-4 w-4 text-blue-100" />
            <span className="text-blue-50 tracking-wide uppercase">AI Summary</span>
          </div>
          <h2 className="text-3xl font-black tracking-tight mb-2">
            {document_type}
          </h2>
          <p className="text-blue-100/90 text-lg max-w-2xl font-medium">
            We've read the document and translated the legalese into plain English. Here is what you need to know.
          </p>
        </div>
      </section>

      {/* Plain English summary */}
      <section aria-labelledby="plain-english-heading" className="rounded-3xl bg-white p-8 sm:p-10 shadow-sm ring-1 ring-slate-200">
        <h2 id="plain-english-heading" className="mb-6 text-xl font-bold text-slate-900 tracking-tight flex items-center gap-3">
          <FileText className="h-6 w-6 text-blue-600" />
          The Plain English Version
        </h2>
        <div className="prose prose-slate prose-lg max-w-none text-slate-700 leading-relaxed">
          <ReactMarkdown>{plain_english}</ReactMarkdown>
        </div>
      </section>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Key points */}
        <section aria-labelledby="key-points-heading" className="flex flex-col">
          <h2 id="key-points-heading" className="mb-6 text-xl font-bold text-slate-900 tracking-tight flex items-center gap-3">
            <CheckCircle className="h-6 w-6 text-green-500" />
            Key Takeaways
          </h2>
          {key_points.length > 0 ? (
            <ul className="space-y-3 flex-1">
              {key_points.map((point, idx) => (
                <li
                  key={idx}
                  className="flex items-start gap-4 rounded-2xl bg-white p-5 shadow-sm ring-1 ring-slate-200 hover:ring-green-200 hover:bg-green-50/30 transition-colors"
                >
                  <div className="rounded-full bg-green-100 p-1 shrink-0 mt-0.5">
                    <CheckCircle aria-hidden="true" className="h-4 w-4 text-green-600" />
                  </div>
                  <span className="text-base text-slate-700 font-medium leading-relaxed">{point}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-slate-500 italic">No specific key takeaways identified.</p>
          )}
        </section>

        {/* Unusual clauses */}
        <section aria-labelledby="unusual-clauses-heading" className="flex flex-col">
          <h2 id="unusual-clauses-heading" className="mb-6 text-xl font-bold text-slate-900 tracking-tight flex items-center gap-3">
            <AlertCircle className="h-6 w-6 text-amber-500" />
            Unusual Clauses
          </h2>
          {unusual_clauses.length > 0 ? (
            <div className="flex-1 rounded-3xl border-2 border-amber-200 bg-amber-50/50 p-6 sm:p-8">
              <div className="mb-6 flex items-start gap-3">
                <AlertTriangle aria-hidden="true" className="h-6 w-6 text-amber-600 shrink-0 mt-0.5" />
                <p className="text-base font-bold text-amber-900 leading-snug">
                  The following clauses are non-standard and warrant your attention:
                </p>
              </div>
              <ul className="space-y-4">
                {unusual_clauses.map((clause, idx) => (
                  <li key={idx} className="flex items-start gap-3 text-base text-amber-900/90 font-medium leading-relaxed">
                    <span aria-hidden="true" className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-500" />
                    <span>{clause}</span>
                  </li>
                ))}
              </ul>
            </div>
          ) : (
            <div className="flex-1 rounded-3xl border border-slate-200 bg-slate-50 p-8 flex flex-col items-center justify-center text-center">
              <CheckCircle className="h-10 w-10 text-green-400 mb-3" />
              <p className="text-slate-600 font-medium">No unusual clauses found.</p>
              <p className="text-sm text-slate-400 mt-1">This document appears to use standard formatting.</p>
            </div>
          )}
        </section>
      </div>
    </article>
  );
}
