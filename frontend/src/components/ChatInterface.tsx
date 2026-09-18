import {
  useState,
  useRef,
  useEffect,
  useCallback,
  type KeyboardEvent,
  type FormEvent,
} from 'react';
import ReactMarkdown from 'react-markdown';
import { Send, Bot, AlertCircle } from 'lucide-react';
import { useWorkspaceStore } from '../stores/workspace';
import { useStreamingChat } from '../hooks/useStreamingChat';

export default function ChatInterface(): JSX.Element {
  const [inputValue, setInputValue] = useState('');
  const chatHistory = useWorkspaceStore((s) => s.chatHistory);
  const { sendMessage, isStreaming, error } = useStreamingChat();

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory, isStreaming]);

  const handleSubmit = useCallback(
    async (e?: FormEvent) => {
      e?.preventDefault();
      const trimmed = inputValue.trim();
      if (!trimmed || isStreaming) return;

      setInputValue('');
      textareaRef.current?.focus();
      await sendMessage(trimmed);
    },
    [inputValue, isStreaming, sendMessage],
  );

  const handleKeyDown = useCallback(
    (e: KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        void handleSubmit();
      }
    },
    [handleSubmit],
  );

  return (
    <div className="flex h-full flex-col bg-slate-50/50">
      {/* Message log */}
      <div
        role="log"
        aria-live="polite"
        className="flex-1 overflow-y-auto space-y-6 px-6 py-6"
      >
        {chatHistory.length === 0 && !isStreaming && (
          <div className="flex h-full flex-col items-center justify-center text-center px-4">
            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-4">
              <Bot className="w-8 h-8 text-blue-600" />
            </div>
            <p className="text-slate-800 font-bold mb-2">How can I help you?</p>
            <p className="text-sm text-slate-500 max-w-xs leading-relaxed">
              Ask any question about your document — for example:
              <br />
              <span className="italic font-medium text-slate-600 mt-2 block">"What are my obligations under this contract?"</span>
            </p>
          </div>
        )}

        {chatHistory.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {msg.role === 'user' ? (
              <div className="flex flex-col items-end gap-1.5 max-w-[85%]">
                <div className="flex items-center gap-2 px-1">
                  <span className="text-xs font-bold text-slate-500 uppercase">You</span>
                </div>
                <div className="rounded-2xl rounded-tr-sm bg-blue-600 px-5 py-3 text-[15px] text-white shadow-sm font-medium leading-relaxed">
                  {msg.content}
                </div>
              </div>
            ) : (
              <div className="flex flex-col items-start gap-1.5 max-w-[90%]">
                <div className="flex items-center gap-2 px-1">
                  <Bot className="w-4 h-4 text-blue-500" />
                  <span className="text-xs font-bold text-slate-500 uppercase">Copilot</span>
                </div>
                <div className="rounded-2xl rounded-tl-sm bg-white px-5 py-4 text-[15px] text-slate-700 shadow-sm ring-1 ring-slate-200 prose prose-slate prose-p:leading-relaxed">
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                </div>
              </div>
            )}
          </div>
        ))}

        {isStreaming && (
          <div className="flex justify-start">
            <div className="flex flex-col items-start gap-1.5 max-w-[90%]">
                <div className="flex items-center gap-2 px-1">
                  <Bot className="w-4 h-4 text-blue-500" />
                  <span className="text-xs font-bold text-slate-500 uppercase">Copilot</span>
                </div>
              <div className="flex items-center gap-1.5 rounded-2xl rounded-tl-sm bg-white px-5 py-4 shadow-sm ring-1 ring-slate-200">
                <span className="h-2 w-2 animate-bounce rounded-full bg-blue-400 [animation-delay:-0.3s]" />
                <span className="h-2 w-2 animate-bounce rounded-full bg-blue-400 [animation-delay:-0.15s]" />
                <span className="h-2 w-2 animate-bounce rounded-full bg-blue-400" />
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} aria-hidden="true" />
      </div>

      <div className="px-6 shrink-0 bg-white border-t border-slate-100 py-4 shadow-[0_-10px_20px_rgba(0,0,0,0.02)] z-10 relative">
        {error && (
          <p role="alert" className="mb-3 text-xs font-bold text-red-500 flex items-center gap-1">
            <AlertCircle className="w-3 h-3" />
            {error}
          </p>
        )}
        
        <form onSubmit={(e) => void handleSubmit(e)} className="relative">
          <label htmlFor="chat-input" className="sr-only">Ask a question</label>
          <textarea
            ref={textareaRef}
            id="chat-input"
            rows={2}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isStreaming}
            placeholder="Ask anything..."
            className="w-full resize-none rounded-2xl border-0 bg-slate-100 pl-5 pr-14 py-3.5 text-[15px] font-medium text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/50 disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={isStreaming || !inputValue.trim()}
            className="absolute right-2 top-2 bottom-2 flex w-10 items-center justify-center rounded-xl bg-blue-600 text-white shadow-sm transition-transform hover:scale-105 active:scale-95 disabled:hover:scale-100 disabled:opacity-50"
          >
            <Send className="h-4 w-4" />
          </button>
        </form>
        <p className="text-[10px] text-center text-slate-400 mt-2 font-medium">AI can make mistakes. Check important information.</p>
      </div>
    </div>
  );
}
