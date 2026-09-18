import { useState, useCallback } from 'react';
import { analyzeDocument } from '../lib/api';
import { useWorkspaceStore } from '../stores/workspace';

interface UseAnalysisReturn {
  analyze: (sessionId: string) => Promise<void>;
  isAnalyzing: boolean;
  error: string | null;
}

/**
 * useAnalysis — triggers the full AI analysis for an uploaded document.
 * Stores the result into the workspace Zustand store on success.
 */
export function useAnalysis(): UseAnalysisReturn {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const setAnalysis = useWorkspaceStore((s) => s.setAnalysis);

  const analyze = useCallback(
    async (sessionId: string): Promise<void> => {
      setIsAnalyzing(true);
      setError(null);

      try {
        const result = await analyzeDocument(sessionId);
        setAnalysis(result);
      } catch (err: any) {
        let message = 'Analysis failed. Please try again.';
        if (err.response?.data?.detail) {
          message = err.response.data.detail;
        } else if (err instanceof Error) {
          message = err.message;
        }
        setError(message);
      } finally {
        setIsAnalyzing(false);
      }
    },
    [setAnalysis],
  );

  return { analyze, isAnalyzing, error };
}
