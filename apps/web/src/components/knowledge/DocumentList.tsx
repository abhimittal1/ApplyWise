import { FileText, Trash2, Loader2, CheckCircle, AlertCircle } from 'lucide-react';
import type { DocumentInfo } from '@/lib/api/documents';

interface DocumentListProps {
  documents: DocumentInfo[];
  onDelete: (id: string) => void;
}

const statusConfig = {
  UPLOADING: {
    icon: Loader2,
    label: 'Uploading',
    iconClass: 'animate-spin text-muted-foreground',
    pillClass: 'bg-muted text-muted-foreground',
  },
  PROCESSING: {
    icon: Loader2,
    label: 'Processing',
    iconClass: 'animate-spin text-amber-500 dark:text-amber-400',
    pillClass: 'bg-amber-500/10 text-amber-600 dark:text-amber-400',
  },
  READY: {
    icon: CheckCircle,
    label: 'Ready',
    iconClass: 'text-emerald-500 dark:text-emerald-400',
    pillClass: 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400',
  },
  FAILED: {
    icon: AlertCircle,
    label: 'Failed',
    iconClass: 'text-destructive',
    pillClass: 'bg-destructive/10 text-destructive',
  },
};

export default function DocumentList({ documents, onDelete }: DocumentListProps) {
  if (documents.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <div className="flex h-12 w-12 items-center justify-center rounded-full bg-muted">
          <FileText className="h-6 w-6 text-muted-foreground" />
        </div>
        <p className="mt-3 text-sm text-muted-foreground">
          No documents uploaded yet. Upload your resume, transcripts, or project notes to get started.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {documents.map((doc) => {
        const status = statusConfig[doc.status];
        const StatusIcon = status.icon;
        return (
          <div
            key={doc.id}
            className="group flex items-center justify-between rounded-xl border border-border bg-card p-4 shadow-sm transition-shadow hover:shadow-md"
          >
            <div className="flex items-center gap-3 min-w-0">
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10">
                <FileText className="h-5 w-5 text-primary" />
              </div>
              <div className="min-w-0">
                <p className="truncate text-sm font-medium text-foreground">{doc.filename}</p>
                <p className="text-xs text-muted-foreground">
                  {doc.file_type.toUpperCase()} &middot; {new Date(doc.created_at).toLocaleDateString()}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3 shrink-0 ml-4">
              <span className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium ${status.pillClass}`}>
                <StatusIcon className={`h-3.5 w-3.5 ${status.iconClass}`} />
                {status.label}
              </span>
              <button
                onClick={() => onDelete(doc.id)}
                className="rounded-lg p-1.5 text-muted-foreground opacity-0 transition-all hover:bg-destructive/10 hover:text-destructive group-hover:opacity-100"
              >
                <Trash2 className="h-4 w-4" />
              </button>
            </div>
          </div>
        );
      })}
    </div>
  );
}
