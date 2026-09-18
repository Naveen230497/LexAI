import { create } from 'zustand';
import type { FullAnalysisResult, ChatMessage } from '../lib/api';

/** The three available workspace tabs. */
export type WorkspaceTab = 'simplification' | 'risks' | 'chat';

interface WorkspaceState {
  /** Server-assigned session ID for the currently loaded document. */
  sessionId: string | null;
  /** Original filename of the uploaded document. */
  fileName: string | null;
  /** Full analysis result once the AI has processed the document. */
  analysis: FullAnalysisResult | null;
  /** Accumulated chat conversation history. */
  chatHistory: ChatMessage[];
  /** Currently visible workspace tab. */
  activeTab: WorkspaceTab;

  /** Stores the session data returned immediately after upload. */
  setSession: (sessionId: string, fileName: string) => void;
  /** Stores the AI analysis result after the analysis endpoint resolves. */
  setAnalysis: (analysis: FullAnalysisResult) => void;
  /** Appends a single chat message (user or assistant) to the history. */
  addChatMessage: (message: ChatMessage) => void;
  /** Switches the visible workspace tab. */
  setActiveTab: (tab: WorkspaceTab) => void;
  /** Resets all workspace state (called when user uploads a new document). */
  reset: () => void;
}

const initialState = {
  sessionId: null,
  fileName: null,
  analysis: null,
  chatHistory: [] as ChatMessage[],
  activeTab: 'simplification' as WorkspaceTab,
};

/**
 * useWorkspaceStore — global Zustand store for LexAI workspace state.
 * Persists across route changes within a single browser session.
 */
export const useWorkspaceStore = create<WorkspaceState>((set) => ({
  ...initialState,

  setSession: (sessionId, fileName) =>
    set({ sessionId, fileName }),

  setAnalysis: (analysis) =>
    set({ analysis }),

  addChatMessage: (message) =>
    set((state) => ({ chatHistory: [...state.chatHistory, message] })),

  setActiveTab: (activeTab) =>
    set({ activeTab }),

  reset: () =>
    set({ ...initialState, chatHistory: [] }),
}));
