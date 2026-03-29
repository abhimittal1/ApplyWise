import api from './client';

export interface SourceChunk {
  chunk_id: string;
  content: string;
  filename: string | null;
  score: number;
}

export interface ChatResponseData {
  answer: string;
  sources: SourceChunk[];
  conversation_id: string;
}

export interface ConversationInfo {
  id: string;
  title: string;
  created_at: string;
}

export interface ChatMessageInfo {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources: { chunks?: SourceChunk[] } | null;
  created_at: string;
}

export async function sendChatMessage(
  message: string,
  conversationId?: string
): Promise<ChatResponseData> {
  const { data } = await api.post('/knowledge/chat', {
    message,
    conversation_id: conversationId,
  });
  return data;
}

export async function listConversations(): Promise<ConversationInfo[]> {
  const { data } = await api.get('/knowledge/conversations');
  return data;
}

export async function getConversationMessages(conversationId: string): Promise<ChatMessageInfo[]> {
  const { data } = await api.get(`/knowledge/conversations/${conversationId}/messages`);
  return data;
}

export async function deleteConversation(conversationId: string): Promise<void> {
  await api.delete(`/knowledge/conversations/${conversationId}`);
}
