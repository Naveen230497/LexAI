import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { uploadDocument } from '../lib/api';
import { useWorkspaceStore } from '../stores/workspace';
import { useAnalysis } from './useAnalysis';

interface UseDocumentUploadReturn {
  upload: (file: File) => Promise<void>;
  isUploading: boolean;
  error: string | null;
}

/**
 * useDocumentUpload — handles file upload flow including:
 * 1. POST /api/v1/documents/upload
 * 2. Stores session into Zustand
 * 3. Navigates to /workspace
 * 4. Automatically triggers full analysis
 */
export function useDocumentUpload(): UseDocumentUploadReturn {
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const navigate = useNavigate();
  const setSession = useWorkspaceStore((s) => s.setSession);
  const { analyze } = useAnalysis();

  const upload = useCallback(
    async (file: File): Promise<void> => {
      setIsUploading(true);
      setError(null);

      try {
        const result = await uploadDocument(file);
        setSession(result.session_id, result.filename);
        navigate('/workspace');
        // Kick off analysis in the background — Workspace page will show the
        // loading state via the store's analysis === null check.
        void analyze(result.session_id);
      } catch (err: unknown) {
        const message =
          err instanceof Error ? err.message : 'Upload failed. Please try again.';
        setError(message);
      } finally {
        setIsUploading(false);
      }
    },
    [setSession, navigate, analyze],
  );

  return { upload, isUploading, error };
}
