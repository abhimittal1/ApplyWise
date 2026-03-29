import { useState, useEffect, useCallback } from 'react';
import DocumentUpload from '@/components/knowledge/DocumentUpload';
import DocumentList from '@/components/knowledge/DocumentList';
import KnowledgeChat from '@/components/knowledge/KnowledgeChat';
import ConversationList from '@/components/knowledge/ConversationList';
import {
  listDocuments,
  deleteDocument,
  getDocumentStatus,
  type DocumentInfo,
} from '@/lib/api/documents';
import {
  listConversations,
  deleteConversation,
  type ConversationInfo,
} from '@/lib/api/knowledge';

export default function KnowledgePage() {
  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [conversations, setConversations] = useState<ConversationInfo[]>([]);
  const [activeTab, setActiveTab] = useState<'documents' | 'chat'>('documents');

  const loadDocuments = useCallback(async () => {
    try {
      const docs = await listDocuments();
      setDocuments(docs);
    } catch {
      // ignore
    }
  }, []);

  const loadConversations = useCallback(async () => {
    try {
      const convs = await listConversations();
      setConversations(convs);
    } catch {
      // ignore
    }
  }, []);

  useEffect(() => {
    loadDocuments();
  }, [loadDocuments]);

  useEffect(() => {
    if (activeTab === 'chat') {
      loadConversations();
    }
  }, [activeTab, loadConversations]);

  const handleUploadComplete = (doc: DocumentInfo) => {
    setDocuments((prev) => [doc, ...prev]);
    const interval = setInterval(async () => {
      try {
        const status = await getDocumentStatus(doc.id);
        setDocuments((prev) =>
          prev.map((d) => (d.id === doc.id ? { ...d, status: status.status as DocumentInfo['status'] } : d))
        );
        if (status.status === 'READY' || status.status === 'FAILED') {
          clearInterval(interval);
        }
      } catch {
        clearInterval(interval);
      }
    }, 2000);
  };

  const handleDelete = async (id: string) => {
    try {
      await deleteDocument(id);
      setDocuments((prev) => prev.filter((d) => d.id !== id));
    } catch {
      // ignore
    }
  };

  const handleDeleteConversation = async (id: string) => {
    try {
      await deleteConversation(id);
      setConversations((prev) => prev.filter((c) => c.id !== id));
      if (conversationId === id) {
        setConversationId(null);
      }
    } catch {
      // ignore
    }
  };

  const handleConversationCreated = (id: string) => {
    setConversationId(id);
    loadConversations();
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-foreground">
          Knowledge Base
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Upload documents and chat with your career knowledge.
        </p>
      </div>

      {/* Tabs */}
      <div className="inline-flex rounded-lg bg-muted p-1">
        <button
          onClick={() => setActiveTab('documents')}
          className={`rounded-md px-4 py-2 text-sm font-medium transition-all ${
            activeTab === 'documents'
              ? 'bg-background text-foreground shadow-sm'
              : 'text-muted-foreground hover:text-foreground'
          }`}
        >
          Documents ({documents.length})
        </button>
        <button
          onClick={() => setActiveTab('chat')}
          className={`rounded-md px-4 py-2 text-sm font-medium transition-all ${
            activeTab === 'chat'
              ? 'bg-background text-foreground shadow-sm'
              : 'text-muted-foreground hover:text-foreground'
          }`}
        >
          Knowledge Chat
        </button>
      </div>

      {activeTab === 'documents' ? (
        <div className="space-y-6">
          <div className="rounded-xl border border-border bg-card p-6 shadow-sm">
            <DocumentUpload onUploadComplete={handleUploadComplete} />
          </div>
          <div className="rounded-xl border border-border bg-card p-6 shadow-sm">
            <h2 className="mb-4 text-sm font-semibold uppercase tracking-wider text-muted-foreground">
              Your Documents
            </h2>
            <DocumentList documents={documents} onDelete={handleDelete} />
          </div>
        </div>
      ) : (
        <div className="flex flex-col gap-4 min-h-[500px] lg:h-[calc(100vh-12rem)] lg:flex-row">
          <div className="w-full shrink-0 rounded-xl border border-border bg-card shadow-sm lg:w-72">
            <ConversationList
              conversations={conversations}
              activeId={conversationId}
              onSelect={setConversationId}
              onDelete={handleDeleteConversation}
              onNewChat={() => setConversationId(null)}
            />
          </div>
          <div className="flex-1 rounded-xl border border-border bg-card shadow-sm overflow-hidden">
            <KnowledgeChat
              conversationId={conversationId}
              onConversationCreated={handleConversationCreated}
            />
          </div>
        </div>
      )}
    </div>
  );
}
