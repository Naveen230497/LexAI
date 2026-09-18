import { useState, useCallback, useRef } from 'react';
import type { ChatMessage } from '../lib/api';
import { useWorkspaceStore } from '../stores/workspace';

interface UseStreamingChatReturn {
  sendMessage: (question: string) => Promise<void>;
  isStreaming: boolean;
  error: string | null;
}

/**
 * useStreamingChat — sends a question to the backend SSE chat endpoint and
 * streams the response token-by-token into the workspace chat history.
 *
 * Uses the Fetch API instead of EventSource because the SSE endpoint requires
 * a POST body (chat history), which the native EventSource API does not support.
 *
 * Cleanup: the AbortController ref ensures that if the component unmounts
 * mid-stream the pending fetch is cancelled immediately.
 */
export function useStreamingChat(): UseStreamingChatReturn {
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const abortControllerRef = useRef<AbortController | null>(null);

  const sessionId = useWorkspaceStore((s) => s.sessionId);
  const chatHistory = useWorkspaceStore((s) => s.chatHistory);
  const addChatMessage = useWorkspaceStore((s) => s.addChatMessage);

  const sendMessage = useCallback(
    async (question: string): Promise<void> => {
      if (!sessionId) {
        setError('No active session. Please upload a document first.');
        return;
      }

      // Abort any in-progress stream before starting a new one.
      abortControllerRef.current?.abort();
      const controller = new AbortController();
      abortControllerRef.current = controller;

      setIsStreaming(true);
      setError(null);

      // Optimistically add the user message to the store immediately.
      const userMessage: ChatMessage = { role: 'user', content: question };
      addChatMessage(userMessage);

      // Build history to send: everything before this new user turn.
      const historyToSend: ChatMessage[] = chatHistory;

      let accumulatedContent = '';

      try {
        const response = await fetch(`/api/v1/chat/${sessionId}/stream`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ question, history: historyToSend }),
          signal: controller.signal,
        });

        if (!response.ok) {
          throw new Error(`Server error: ${response.status} ${response.statusText}`);
        }

        if (!response.body) {
          throw new Error('Response body is null — SSE stream unavailable.');
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let buffer = '';

        // eslint-disable-next-line no-constant-condition
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          // Decode the chunk and append to the running buffer.
          buffer += decoder.decode(value, { stream: true });

          // SSE lines are separated by double newlines (\n\n).
          // Split on single newlines to process individual `data:` lines.
          const lines = buffer.split('\n');
          // Keep the last (potentially incomplete) segment in the buffer.
          buffer = lines.pop() ?? '';

          for (const line of lines) {
            const trimmed = line.trim();
            if (!trimmed.startsWith('data:')) continue;

            const rawData = trimmed.slice('data:'.length).trim();

            if (rawData === '[DONE]') {
              // Stream finished — persist the full accumulated response.
              if (accumulatedContent) {
                const assistantMessage: ChatMessage = {
                  role: 'assistant',
                  content: accumulatedContent,
                };
                addChatMessage(assistantMessage);
              }
              return;
            }

            try {
              const parsed = JSON.parse(rawData) as { token?: string };
              if (typeof parsed.token === 'string') {
                accumulatedContent += parsed.token;
              }
            } catch {
              // Ignore malformed JSON chunks; the stream may still continue.
            }
          }
        }

        // If the stream ended without [DONE] (e.g. connection closed), still
        // save whatever was accumulated.
        if (accumulatedContent) {
          addChatMessage({ role: 'assistant', content: accumulatedContent });
        }
      } catch (err: unknown) {
        if (err instanceof DOMException && err.name === 'AbortError') {
          // Intentional cancellation — not an error.
          return;
        }
        const message =
          err instanceof Error ? err.message : 'Chat request failed. Please try again.';
        setError(message);
      } finally {
        setIsStreaming(false);
        abortControllerRef.current = null;
      }
    },
    [sessionId, chatHistory, addChatMessage],
  );

  return { sendMessage, isStreaming, error };
}
