import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Scale, UploadCloud, Loader2, AlertCircle, Sparkles, ShieldAlert, MessageSquare } from 'lucide-react';
import { useWorkspaceStore } from '../stores/workspace';
import { useAnalysis } from '../hooks/useAnalysis';
import DisclaimerBanner from '../components/DisclaimerBanner';
import AnalysisPanel from '../components/AnalysisPanel';
import RiskDashboard from '../components/RiskDashboard';
import ChatInterface from '../components/ChatInterface';
import { motion, AnimatePresence } from 'framer-motion';

type DocTab = 'simplification' | 'risks';

export default function Workspace(): JSX.Element {
  const navigate = useNavigate();
  const sessionId = useWorkspaceStore((s) => s.sessionId);
  const fileName = useWorkspaceStore((s) => s.fileName);
  const analysis = useWorkspaceStore((s) => s.analysis);
  const reset = useWorkspaceStore((s) => s.reset);

  const [activeDocTab, setActiveDocTab] = useState<DocTab>('simplification');
  const { analyze, isAnalyzing, error: analysisError } = useAnalysis();

  useEffect(() => {
    if (!sessionId) {
      navigate('/', { replace: true });
    }
  }, [sessionId, navigate]);

  useEffect(() => {
    if (sessionId && !analysis && !isAnalyzing) {
      void analyze(sessionId);
    }
  }, [sessionId]);

  const handleNewUpload = (): void => {
    reset();
    navigate('/');
  };

  if (isAnalyzing || (!analysis && !analysisError)) {
    return (
      <div className="flex min-h-screen flex-col bg-[#f8fafc]">
        <WorkspaceHeader fileName={fileName} onNewUpload={handleNewUpload} />
        <DisclaimerBanner />
        <main className="flex flex-1 flex-col items-center justify-center gap-6 px-6 py-20 relative overflow-hidden">
          <div className="absolute inset-0 flex items-center justify-center opacity-30 pointer-events-none">
            <div className="w-[600px] h-[600px] bg-blue-400 rounded-full blur-[120px] mix-blend-multiply" />
            <div className="w-[600px] h-[600px] bg-indigo-400 rounded-full blur-[120px] mix-blend-multiply -ml-[200px]" />
          </div>
          <motion.div 
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="z-10 flex flex-col items-center glass-panel p-12 rounded-3xl"
          >
            <Loader2 className="h-16 w-16 animate-spin text-blue-600 mb-6" />
            <h2 className="text-2xl font-black text-slate-800 tracking-tight mb-2">Analyzing Intelligence</h2>
            <p className="text-slate-500 font-medium text-center max-w-sm">
              Our AI is extracting clauses, modeling legal risks, and embedding the text for semantic search.
            </p>
          </motion.div>
        </main>
      </div>
    );
  }

  if (analysisError) {
    return (
      <div className="flex min-h-screen flex-col bg-slate-50">
        <WorkspaceHeader fileName={fileName} onNewUpload={handleNewUpload} />
        <DisclaimerBanner />
        <main className="flex flex-1 flex-col items-center justify-center gap-6 px-6 py-20">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass-panel p-10 rounded-3xl max-w-md text-center flex flex-col items-center"
          >
            <div className="w-20 h-20 bg-red-50 rounded-full flex items-center justify-center mb-6">
              <AlertCircle className="h-10 w-10 text-red-500" />
            </div>
            <p className="text-2xl font-black text-slate-800 tracking-tight">Analysis Failed</p>
            <p className="mt-3 text-sm text-slate-500 font-medium leading-relaxed">{analysisError}</p>
            <button
              onClick={() => sessionId && void analyze(sessionId)}
              className="mt-8 rounded-xl bg-slate-900 px-8 py-3.5 text-sm font-bold text-white shadow-xl hover:bg-slate-800 transition-all hover:-translate-y-1 hover:shadow-2xl"
            >
              Retry Analysis
            </button>
          </motion.div>
        </main>
      </div>
    );
  }

  return (
    <div className="flex h-screen flex-col overflow-hidden bg-slate-50/50">
      <WorkspaceHeader fileName={fileName} onNewUpload={handleNewUpload} />
      <DisclaimerBanner />

      <div className="flex flex-1 overflow-hidden relative">
        <div className="flex-1 flex flex-col h-full bg-transparent">
          <div className="px-10 pt-8 pb-0 shrink-0">
            <div className="flex space-x-8 border-b border-slate-200">
              <button
                onClick={() => setActiveDocTab('simplification')}
                className={`pb-4 text-sm font-bold tracking-wide transition-all relative ${activeDocTab === 'simplification' ? 'text-blue-600' : 'text-slate-400 hover:text-slate-600'}`}
              >
                <span className="flex items-center gap-2.5"><Sparkles className="w-4 h-4" /> AI Summary</span>
                {activeDocTab === 'simplification' && (
                  <motion.span layoutId="activeTab" className="absolute bottom-0 left-0 w-full h-0.5 bg-blue-600 rounded-t-full" />
                )}
              </button>
              <button
                onClick={() => setActiveDocTab('risks')}
                className={`pb-4 text-sm font-bold tracking-wide transition-all relative ${activeDocTab === 'risks' ? 'text-indigo-600' : 'text-slate-400 hover:text-slate-600'}`}
              >
                <span className="flex items-center gap-2.5"><ShieldAlert className="w-4 h-4" /> Risk Analysis</span>
                {activeDocTab === 'risks' && (
                  <motion.span layoutId="activeTab" className="absolute bottom-0 left-0 w-full h-0.5 bg-indigo-600 rounded-t-full" />
                )}
              </button>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto px-10 py-8 relative">
            <AnimatePresence mode="wait">
              <motion.div
                key={activeDocTab}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.2 }}
                className="h-full"
              >
                {activeDocTab === 'simplification' && analysis && (
                  <AnalysisPanel simplification={analysis.simplification} />
                )}
                {activeDocTab === 'risks' && analysis && (
                  <RiskDashboard riskAnalysis={analysis.risk_analysis} />
                )}
              </motion.div>
            </AnimatePresence>
          </div>
        </div>

        <div className="w-[480px] shrink-0 h-[calc(100vh-6.5rem)] my-4 mr-4 glass-panel rounded-2xl flex flex-col overflow-hidden z-10 relative">
          <div className="px-6 py-5 border-b border-white/50 shrink-0 bg-white/40">
            <h2 className="text-sm font-black text-slate-800 tracking-wider uppercase flex items-center gap-2.5">
              <MessageSquare className="w-4 h-4 text-indigo-500" />
              AI Copilot
            </h2>
          </div>
          <div className="flex-1 overflow-hidden bg-white/20">
            <ChatInterface />
          </div>
        </div>
      </div>
    </div>
  );
}

interface WorkspaceHeaderProps {
  fileName: string | null;
  onNewUpload: () => void;
}

function WorkspaceHeader({ fileName, onNewUpload }: WorkspaceHeaderProps): JSX.Element {
  return (
    <header className="bg-white border-b border-slate-200 shrink-0 shadow-sm z-20 relative">
      <div className="mx-auto flex w-full items-center justify-between gap-4 px-8 py-3.5">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-xl shadow-md">
            <Scale aria-hidden="true" className="h-5 w-5 text-white" />
          </div>
          <span className="text-xl font-black tracking-tight text-slate-800">
            Lex<span className="premium-gradient-text">AI</span>
          </span>
          {fileName && (
            <>
              <span aria-hidden="true" className="text-slate-300 ml-3 text-lg">/</span>
              <span
                className="max-w-[200px] sm:max-w-xs truncate text-xs font-bold text-slate-600 ml-3 bg-slate-100 px-3.5 py-1.5 rounded-full border border-slate-200 shadow-sm"
                title={fileName}
              >
                {fileName}
              </span>
            </>
          )}
        </div>
        <button
          onClick={onNewUpload}
          className="flex items-center gap-2.5 rounded-full bg-slate-900 px-5 py-2.5 text-xs font-bold text-white shadow-md hover:bg-slate-800 transition-all hover:shadow-lg hover:-translate-y-0.5"
        >
          <UploadCloud aria-hidden="true" className="h-4 w-4" />
          New Document
        </button>
      </div>
    </header>
  );
}
