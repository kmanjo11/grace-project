import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { ChatApi } from '../api/apiClient';

export interface Conversation {
  id: string;
  title?: string;
  created?: string;
  updated?: string;
  message_count?: number;
  metadata?: Record<string, any>;
  // compatibility fields seen in current UI
  session_id?: string;
  name?: string;
  topic?: string;
  lastActivity?: string;
}

const SESSIONS_KEY = ['chat', 'sessions'] as const;

export function useConversations() {
  const qc = useQueryClient();

  const sessionsQuery = useQuery({
    queryKey: SESSIONS_KEY,
    queryFn: async () => {
      const { sessions } = await ChatApi.getSessions();
      // Normalize shape for current UI expectations
      const normalized = sessions.map((s) => ({
        id: (s as any).id ?? (s as any).session_id,
        session_id: (s as any).session_id ?? (s as any).id,
        name: (s as any).title ?? (s as any).name ?? (s as any).topic ?? 'New Conversation',
        topic: (s as any).topic ?? (s as any).title ?? (s as any).name ?? 'New Conversation',
        lastActivity: (s as any).updated ?? (s as any).lastActivity ?? new Date().toISOString(),
        message_count: (s as any).message_count,
        metadata: (s as any).metadata,
      })) as Conversation[];
      // Sort newest first
      normalized.sort((a, b) => new Date(b.lastActivity || '').getTime() - new Date(a.lastActivity || '').getTime());
      return normalized;
    },
    staleTime: 30_000,
  });

  const createMutation = useMutation({
    mutationFn: async (title?: string) => ChatApi.createSession(title),
    onMutate: async (title?: string) => {
      // Optimistically add a placeholder session to the top of the list
      const tempId = `temp_${Date.now()}`;
      const now = new Date().toISOString();
      const prev = qc.getQueryData<Conversation[]>(SESSIONS_KEY) || [];
      const optimistic: Conversation = {
        id: tempId,
        session_id: tempId,
        name: title || 'New Conversation',
        topic: title || 'New Conversation',
        lastActivity: now,
      } as Conversation;

      qc.setQueryData<Conversation[]>(SESSIONS_KEY, [optimistic, ...prev]);

      return { prev, tempId };
    },
    onError: (_err, _vars, ctx) => {
      // Rollback optimistic update
      if (!ctx) return;
      qc.setQueryData<Conversation[]>(SESSIONS_KEY, ctx.prev);
    },
    onSuccess: async ({ session_id }, _vars, ctx) => {
      // Replace placeholder with actual session id and invalidate to sync
      qc.setQueryData<Conversation[]>(SESSIONS_KEY, (old) => {
        if (!old) return old as any;
        return old.map((s) =>
          s.id === ctx?.tempId || s.session_id === ctx?.tempId
            ? { ...s, id: session_id, session_id }
            : s
        );
      });
      await qc.invalidateQueries({ queryKey: SESSIONS_KEY });
      return session_id;
    },
  });

  // Local-only rename for now (optimistic UI); no server endpoint hooked
  const rename = async (sessionId: string, newTitle: string) => {
    qc.setQueryData<Conversation[]>(SESSIONS_KEY, (old) => {
      if (!old) return old as any;
      return old.map((s) =>
        (s.session_id === sessionId || s.id === sessionId)
          ? { ...s, name: newTitle, topic: newTitle }
          : s
      );
    });
  };

  return {
    sessions: sessionsQuery.data || [],
    isLoading: sessionsQuery.isLoading,
    isFetching: sessionsQuery.isFetching,
    error: sessionsQuery.error as Error | null,
    refetch: sessionsQuery.refetch,
    create: createMutation.mutateAsync,
    isCreating: createMutation.isPending,
    rename,
  };
}
