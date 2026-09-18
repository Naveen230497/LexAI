import axios from 'axios';

/** Axios instance pre-configured with the API base URL. */
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
  headers: {
    'Content-Type': 'application/json',
  },
});

// ─── Response interfaces ────────────────────────────────────────────────────

export interface DocumentUploadResponse {
  session_id: string;
  filename: string;
  size_bytes: number;
  status: string;
}

export type RiskSeverity = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'INFO';

export interface RiskEntry {
  id: string;
  severity: RiskSeverity;
  clause_text: string;
  section: string;
  explanation: string;
  recommendation: string;
  category: string;
}

export interface SimplificationResult {
  plain_english: string;
  key_points: string[];
  unusual_clauses: string[];
  document_type: string;
}

export interface RiskAnalysisResult {
  risks: RiskEntry[];
  overall_risk_score: number;
  summary: string;
}

export interface FullAnalysisResult {
  simplification: SimplificationResult;
  risk_analysis: RiskAnalysisResult;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

// ─── API functions ───────────────────────────────────────────────────────────

/**
 * Uploads a document file via multipart form data.
 * Returns the server-assigned session ID and file metadata.
 */
export const uploadDocument = async (file: File): Promise<DocumentUploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await apiClient.post<DocumentUploadResponse>(
    '/api/v1/documents/upload',
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    },
  );

  return response.data;
};

/**
 * Triggers full AI analysis (simplification + risk) for an uploaded document.
 * This may take several seconds; callers should show a loading indicator.
 */
export const analyzeDocument = async (sessionId: string): Promise<FullAnalysisResult> => {
  const response = await apiClient.post<FullAnalysisResult>(
    `/api/v1/analysis/${sessionId}/full`,
  );
  return response.data;
};

// Note: Streaming chat is handled directly via the Fetch API in useStreamingChat
// because SSE requires a POST body, which EventSource does not support.

export default apiClient;
