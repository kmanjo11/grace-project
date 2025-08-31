import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { ChatApi } from '../api/apiClient';

export type UIChatMessage = {
  sender: 'user' | 'grace';
  text: string;
  timestamp?: string;
  id?: string;
};

const messagesKey = (sessionId?: string) => ['chat', 'messages', sessionId] as const;

export function useMessages(sessionId?: string | null) {
  const qc = useQueryClient();

  const historyQuery = useQuery({
    queryKey: messagesKey(sessionId || undefined),
    enabled: !!sessionId,
    queryFn: async () => {
      if (!sessionId) return [] as UIChatMessage[];
      const { messages } = await ChatApi.getHistory(sessionId);
      // Normalize from API format {role/content} to UIChatMessage
      const normalized: UIChatMessage[] = messages.map((m: any) => {
        // Newer/quart backend shape: { sender: 'user' | 'grace', text, timestamp }
        if (m.sender && (m.text !== undefined || m.content !== undefined)) {
          const sender = m.sender === 'user' ? 'user' : 'grace';
          return { sender, text: String(m.text ?? m.content ?? ''), timestamp: m.timestamp, id: m.id };
        }
        // OpenAI-like shape: { role: 'user' | 'assistant', content }
        if (m.role === 'user') return { sender: 'user', text: m.content, timestamp: m.timestamp, id: m.id };
        if (m.role === 'assistant') return { sender: 'grace', text: m.content, timestamp: m.timestamp, id: m.id };
        // Legacy shape: { user: '...', bot: '...' }
        if (m.user) return { sender: 'user', text: m.user, timestamp: m.timestamp, id: m.id } as UIChatMessage;
        if (m.bot) return { sender: 'grace', text: m.bot, timestamp: m.timestamp, id: m.id } as UIChatMessage;
        // Fallback (best-effort)
        return { sender: 'grace', text: String(m.content ?? m.text ?? ''), timestamp: m.timestamp, id: m.id };
      });
      return normalized;
    },
    staleTime: 15_000,
  });

  const sendMutation = useMutation({
    mutationFn: async (payload: { sessionId: string; message: string }) => {
      const res = await ChatApi.sendMessage(payload.sessionId, payload.message);
      return res;
    },
    onMutate: async ({ sessionId, message }) => {
      await qc.cancelQueries({ queryKey: messagesKey(sessionId) });
      const prev = qc.getQueryData<UIChatMessage[]>(messagesKey(sessionId));
      const optimistic: UIChatMessage = { sender: 'user', text: message, timestamp: new Date().toISOString(), id: `tmp_${Date.now()}` };
      qc.setQueryData<UIChatMessage[]>(messagesKey(sessionId), (old) => [ ...(old || []), optimistic ]);
      return { prev };
    },
    onError: (_err, { sessionId }, ctx) => {
      if (ctx?.prev) qc.setQueryData(messagesKey(sessionId), ctx.prev);
    },
    onSuccess: (data, { sessionId }) => {
      // Append assistant response
      const assistant: UIChatMessage = { sender: 'grace', text: data.response, timestamp: data.timestamp };
      qc.setQueryData<UIChatMessage[]>(messagesKey(sessionId), (old) => [ ...(old || []), assistant ]);
    },
    onSettled: (_data, _err, { sessionId }) => {
      qc.invalidateQueries({ queryKey: messagesKey(sessionId) });
    }
  });

  const send = (message: string) => {
    if (!sessionId) return Promise.reject(new Error('No session selected'));
    return sendMutation.mutateAsync({ sessionId, message });
  };

  return {
    messages: historyQuery.data || [],
    isLoading: historyQuery.isLoading,
    isFetching: historyQuery.isFetching,
    error: historyQuery.error as Error | null,
    refetch: historyQuery.refetch,
    send,
    isSending: sendMutation.isPending,
  };
}
