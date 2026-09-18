import { Scale, FileSearch, ShieldCheck, MessageSquare } from 'lucide-react';
import DisclaimerBanner from '../components/DisclaimerBanner';
import DocumentUpload from '../components/DocumentUpload';
import { motion } from 'framer-motion';

interface FeatureCardProps {
  icon: JSX.Element;
  title: string;
  description: string;
  delay: number;
}

function FeatureCard({ icon, title, description, delay }: FeatureCardProps): JSX.Element {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
      className="flex flex-col items-start gap-4 rounded-3xl glass-card p-8 text-left group"
    >
      <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-50 to-indigo-100 text-indigo-600 shadow-inner group-hover:scale-110 transition-transform duration-300">
        {icon}
      </div>
      <div>
        <h2 className="text-lg font-black text-slate-800 tracking-tight mb-2">{title}</h2>
        <p className="text-sm text-slate-500 font-medium leading-relaxed">{description}</p>
      </div>
    </motion.div>
  );
}

const FEATURES = [
  {
    icon: <FileSearch aria-hidden="true" className="h-6 w-6" />,
    title: 'Instant Simplification',
    description: 'Transform dense, archaic legal jargon into clear, plain English with key points automatically highlighted.',
  },
  {
    icon: <ShieldCheck aria-hidden="true" className="h-6 w-6" />,
    title: 'Deep Risk Modeling',
    description: 'Our proprietary engine scans for predatory clauses and unlimited liability, ranking risks by severity.',
  },
  {
    icon: <MessageSquare aria-hidden="true" className="h-6 w-6" />,
    title: 'Semantic Copilot',
    description: 'Chat directly with your contract. Vector embeddings map meaning so you can ask natural questions.',
  },
];

export default function Home(): JSX.Element {
  return (
    <div className="flex min-h-screen flex-col overflow-hidden relative">
      <div className="absolute inset-0 flex items-center justify-center opacity-40 pointer-events-none -z-10">
        <div className="w-[800px] h-[800px] bg-blue-300 rounded-full blur-[150px] mix-blend-multiply absolute top-[-200px] left-[-200px]" />
        <div className="w-[600px] h-[600px] bg-indigo-300 rounded-full blur-[150px] mix-blend-multiply absolute bottom-[-100px] right-[-100px]" />
      </div>

      <header className="w-full shrink-0 z-20">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-8 py-6">
          <div className="flex items-center gap-3.5">
            <div className="p-2.5 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-2xl shadow-lg">
              <Scale aria-hidden="true" className="h-6 w-6 text-white" />
            </div>
            <div>
              <span className="text-2xl font-black tracking-tight text-slate-800">
                Lex<span className="premium-gradient-text">AI</span>
              </span>
              <p className="text-[11px] font-bold text-slate-400 tracking-widest uppercase mt-0.5">
                Legal Intelligence
              </p>
            </div>
          </div>
          <div className="hidden sm:flex items-center gap-6">
            <span className="text-sm font-bold text-slate-400">Secure</span>
            <span className="text-sm font-bold text-slate-400">Private</span>
            <span className="text-sm font-bold text-slate-400">Local</span>
          </div>
        </div>
      </header>

      <DisclaimerBanner />

      <main className="flex flex-1 flex-col items-center px-6 py-12 z-10 relative">
        <div className="w-full max-w-3xl">
          <motion.div 
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
            className="mb-12 text-center"
          >
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-50/50 border border-blue-100 mb-6">
              <span className="flex h-2 w-2 rounded-full bg-blue-600 animate-pulse"></span>
              <span className="text-xs font-bold text-blue-800 tracking-wide uppercase">Powered by Gemini 2.5 Flash</span>
            </div>
            <h1 className="text-4xl font-black tracking-tight text-slate-900 sm:text-6xl mb-6">
              Decode contracts in <br/>
              <span className="premium-gradient-text">seconds, not hours.</span>
            </h1>
            <p className="text-lg text-slate-500 font-medium max-w-xl mx-auto leading-relaxed">
              Upload any legal document to generate an instant plain-English translation, extract critical risk vectors, and unlock an AI Q&A Copilot.
            </p>
          </motion.div>

          <motion.div 
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="w-full"
          >
            <DocumentUpload />
          </motion.div>
        </div>

        <div className="mt-24 grid w-full max-w-5xl grid-cols-1 gap-6 sm:grid-cols-3 px-4">
          {FEATURES.map((feat, i) => (
            <FeatureCard key={feat.title} {...feat} delay={0.4 + (i * 0.1)} />
          ))}
        </div>
      </main>

      <footer className="py-8 text-center z-10 relative mt-auto">
        <p className="text-xs font-bold text-slate-400 uppercase tracking-widest">
          Built for AI Legal Assistance Challenge &middot; 2026
        </p>
      </footer>
    </div>
  );
}
