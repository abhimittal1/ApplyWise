import { MessageSquare, Plus, Trash2 } from 'lucide-react';
import type { ConversationInfo } from '@/lib/api/knowledge';

interface ConversationListProps {
  conversations: ConversationInfo[];
  activeId: string | null;
  onSelect: (id: string) => void;
  onDelete: (id: string) => void;
  onNewChat: () => void;
}

export default function ConversationList({
  conversations,
  activeId,
  onSelect,
  onDelete,
  onNewChat,
}: ConversationListProps) {
  return (
    <div className="flex h-full flex-col">
      <div className="p-3">
        <button
          onClick={onNewChat}
          className="flex w-full items-center justify-center gap-2 rounded-lg bg-primary px-3 py-2.5 text-sm font-medium text-primary-foreground shadow-sm transition-colors hover:bg-primary/90"
        >
          <Plus className="h-4 w-4" />
          New Chat
        </button>
      </div>

      <div className="flex-1 overflow-y-auto px-2 pb-2">
        {conversations.length === 0 && (
          <div className="flex flex-col items-center py-8 text-center">
            <MessageSquare className="h-8 w-8 text-muted-foreground/40" />
            <p className="mt-2 text-xs text-muted-foreground">
              No conversations yet
            </p>
          </div>
        )}
        {conversations.map((conv) => (
          <div
            key={conv.id}
            onClick={() => onSelect(conv.id)}
            className={`group mb-1 flex cursor-pointer items-start gap-2.5 rounded-lg px-3 py-2.5 text-sm transition-colors ${
              activeId === conv.id
                ? 'bg-primary/10 text-primary'
                : 'text-foreground hover:bg-muted'
            }`}
          >
            <MessageSquare className={`mt-0.5 h-4 w-4 shrink-0 ${
              activeId === conv.id ? 'text-primary' : 'text-muted-foreground'
            }`} />
            <div className="min-w-0 flex-1">
              <p className="truncate font-medium">{conv.title}</p>
              <p className={`text-xs ${
                activeId === conv.id ? 'text-primary/60' : 'text-muted-foreground'
              }`}>
                {new Date(conv.created_at).toLocaleDateString()}
              </p>
            </div>
            <button
              onClick={(e) => {
                e.stopPropagation();
                onDelete(conv.id);
              }}
              className="shrink-0 rounded-md p-1 opacity-0 transition-all hover:bg-destructive/10 hover:text-destructive group-hover:opacity-100"
            >
              <Trash2 className="h-3.5 w-3.5" />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
