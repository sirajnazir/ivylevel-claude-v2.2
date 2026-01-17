/**
 * useExecutionChat Hook v5.3
 * ==========================
 *
 * React hook for Execution Agent streaming chat.
 * Provides a ChatGPT/Claude-like experience with real-time message streaming.
 *
 * Features:
 * - Server-Sent Events (SSE) streaming
 * - Message history management
 * - Context linking (projects, crises, weekly plans)
 * - Thread management
 * - Auto-reconnect on failure
 *
 * Usage:
 * ```tsx
 * const { messages, sendMessage, isStreaming, error } = useExecutionChat(profileId);
 *
 * // Send a message
 * await sendMessage("I'm stuck on my project", {
 *   contextType: 'project',
 *   contextId: projectId,
 * });
 * ```
 */

'use client';

import { useState, useCallback, useRef, useEffect } from 'react';
import { getSupabaseClient } from '@/lib/supabase/client';

// =====================================================
// Types
// =====================================================

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  contextType?: string;
  contextId?: string;
  isProactive: boolean;
  createdAt: string;
  isStreaming?: boolean;
}

export interface SendMessageOptions {
  contextType?: 'project' | 'crisis' | 'weekly_plan' | 'step' | 'general' | 'nudge' | 'onboarding';
  contextId?: string;
}

export interface UseExecutionChatOptions {
  threadId?: string;
  autoLoadHistory?: boolean;
  historyLimit?: number;
}

export interface UseExecutionChatReturn {
  messages: ChatMessage[];
  sendMessage: (content: string, options?: SendMessageOptions) => Promise<void>;
  isStreaming: boolean;
  error: string | null;
  threadId: string | null;
  clearMessages: () => void;
  loadHistory: () => Promise<void>;
  isLoadingHistory: boolean;
}

// =====================================================
// Hook Implementation
// =====================================================

export function useExecutionChat(
  profileId: string | null,
  options: UseExecutionChatOptions = {}
): UseExecutionChatReturn {
  const { threadId: initialThreadId, autoLoadHistory = true, historyLimit = 50 } = options;

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [threadId, setThreadId] = useState<string | null>(initialThreadId || null);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);

  const abortControllerRef = useRef<AbortController | null>(null);

  // Load conversation history
  const loadHistory = useCallback(async () => {
    if (!profileId) return;

    setIsLoadingHistory(true);
    try {
      const supabase = getSupabaseClient();

      let query = supabase
        .from('conversations')
        .select('id, role, content, context_type, context_id, is_proactive, created_at')
        .eq('profile_id', profileId)
        .eq('agent_type', 'execution')
        .is('deleted_at', null)
        .order('created_at', { ascending: true })
        .limit(historyLimit);

      // If we have a thread ID, filter by it
      if (threadId) {
        query = query.eq('thread_id', threadId);
      }

      const { data, error: fetchError } = await query;

      if (fetchError) {
        console.error('[useExecutionChat] Error loading history:', fetchError);
        return;
      }

      if (data) {
        // Type for Supabase message record
        interface DBMessage {
          id: string;
          role: string;
          content: string;
          context_type?: string;
          context_id?: string;
          is_proactive?: boolean;
          created_at: string;
        }
        const loadedMessages: ChatMessage[] = (data as DBMessage[]).map((msg: DBMessage) => ({
          id: msg.id,
          role: msg.role as 'user' | 'assistant' | 'system',
          content: msg.content,
          contextType: msg.context_type || undefined,
          contextId: msg.context_id || undefined,
          isProactive: msg.is_proactive || false,
          createdAt: msg.created_at,
        }));

        setMessages(loadedMessages);
      }
    } catch (err) {
      console.error('[useExecutionChat] Exception loading history:', err);
    } finally {
      setIsLoadingHistory(false);
    }
  }, [profileId, threadId, historyLimit]);

  // Auto-load history on mount
  useEffect(() => {
    if (autoLoadHistory && profileId) {
      loadHistory();
    }
  }, [autoLoadHistory, profileId, loadHistory]);

  // Send a message
  const sendMessage = useCallback(
    async (content: string, sendOptions: SendMessageOptions = {}) => {
      if (!profileId || !content.trim()) return;

      setError(null);

      // Add user message immediately
      const userMessageId = `temp-user-${Date.now()}`;
      const userMessage: ChatMessage = {
        id: userMessageId,
        role: 'user',
        content: content.trim(),
        contextType: sendOptions.contextType,
        contextId: sendOptions.contextId,
        isProactive: false,
        createdAt: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, userMessage]);

      // Add placeholder for assistant message
      const assistantMessageId = `temp-assistant-${Date.now()}`;
      const assistantMessage: ChatMessage = {
        id: assistantMessageId,
        role: 'assistant',
        content: '',
        contextType: sendOptions.contextType,
        contextId: sendOptions.contextId,
        isProactive: false,
        createdAt: new Date().toISOString(),
        isStreaming: true,
      };

      setMessages((prev) => [...prev, assistantMessage]);
      setIsStreaming(true);

      // Abort any existing request
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      abortControllerRef.current = new AbortController();

      try {
        const response = await fetch('/api/agents/execution/chat/stream', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            profile_id: profileId,
            message: content.trim(),
            context_type: sendOptions.contextType || 'general',
            context_id: sendOptions.contextId,
            thread_id: threadId,
          }),
          signal: abortControllerRef.current.signal,
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body?.getReader();
        const decoder = new TextDecoder();
        let assistantContent = '';
        let finalConversationId: string | null = null;
        let finalThreadId: string | null = null;

        if (reader) {
          while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value, { stream: true });
            const lines = chunk.split('\n').filter((line) => line.startsWith('data: '));

            for (const line of lines) {
              const data = line.slice(6).trim();

              if (data === '[DONE]') {
                continue;
              }

              try {
                const parsed = JSON.parse(data);

                if (parsed.error) {
                  setError(parsed.error);
                  continue;
                }

                if (parsed.content) {
                  assistantContent += parsed.content;

                  // Update assistant message in real-time
                  setMessages((prev) => {
                    const updated = [...prev];
                    const lastIdx = updated.length - 1;

                    if (updated[lastIdx]?.id === assistantMessageId) {
                      updated[lastIdx] = {
                        ...updated[lastIdx],
                        content: assistantContent,
                      };
                    }

                    return updated;
                  });
                }

                if (parsed.done) {
                  finalConversationId = parsed.conversation_id;
                  finalThreadId = parsed.thread_id;
                }
              } catch {
                // Ignore parse errors for incomplete chunks
              }
            }
          }
        }

        // Update final message state
        setMessages((prev) => {
          const updated = [...prev];
          const lastIdx = updated.length - 1;

          if (updated[lastIdx]?.id === assistantMessageId) {
            updated[lastIdx] = {
              ...updated[lastIdx],
              id: finalConversationId || assistantMessageId,
              content: assistantContent,
              isStreaming: false,
            };
          }

          return updated;
        });

        // Update thread ID if we got one
        if (finalThreadId && !threadId) {
          setThreadId(finalThreadId);
        }
      } catch (err) {
        if (err instanceof Error && err.name === 'AbortError') {
          // Request was aborted, don't show error
          return;
        }

        console.error('[useExecutionChat] Error:', err);
        setError(err instanceof Error ? err.message : 'Failed to send message');

        // Remove failed assistant message
        setMessages((prev) => prev.filter((msg) => msg.id !== assistantMessageId));
      } finally {
        setIsStreaming(false);
        abortControllerRef.current = null;
      }
    },
    [profileId, threadId]
  );

  // Clear messages
  const clearMessages = useCallback(() => {
    // Abort any ongoing stream
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    setMessages([]);
    setError(null);
    setThreadId(null);
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  return {
    messages,
    sendMessage,
    isStreaming,
    error,
    threadId,
    clearMessages,
    loadHistory,
    isLoadingHistory,
  };
}

export default useExecutionChat;
