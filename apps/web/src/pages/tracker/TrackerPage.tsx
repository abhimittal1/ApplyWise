import { useState, useEffect, useCallback, useMemo } from 'react';
import { Trash2, MessageSquare, Briefcase, TrendingUp, Trophy, X, Clock } from 'lucide-react';
import {
  listApplications,
  updateApplicationStatus,
  addNote,
  deleteApplication,
  type ApplicationInfo,
  type AppStatus,
} from '@/lib/api/tracker';

const STAGES: { key: AppStatus; label: string; color: string; dotColor: string }[] = [
  { key: 'SAVED', label: 'Saved', color: 'bg-gray-500', dotColor: 'bg-gray-400' },
  { key: 'APPLIED', label: 'Applied', color: 'bg-blue-500', dotColor: 'bg-blue-400' },
  { key: 'OA', label: 'OA / Test', color: 'bg-purple-500', dotColor: 'bg-violet-400' },
  { key: 'INTERVIEW', label: 'Interview', color: 'bg-yellow-500', dotColor: 'bg-amber-400' },
  { key: 'OFFER', label: 'Offer', color: 'bg-green-500', dotColor: 'bg-emerald-400' },
  { key: 'REJECTED', label: 'Rejected', color: 'bg-red-500', dotColor: 'bg-red-400' },
];

function getTotalNoteCount(app: ApplicationInfo): number {
  if (!app.notes) return 0;
  return Object.values(app.notes).reduce((sum, arr) => sum + arr.length, 0);
}

function getNotesForStage(app: ApplicationInfo, stage: string): { content: string; created_at: string }[] {
  if (!app.notes) return [];
  return app.notes[stage] || [];
}

function formatNoteDate(dateStr: string): string {
  try {
    const d = new Date(dateStr);
    return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' }) +
      ' at ' +
      d.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' });
  } catch {
    return dateStr;
  }
}

export default function TrackerPage() {
  const [applications, setApplications] = useState<ApplicationInfo[]>([]);
  const [noteModal, setNoteModal] = useState<{ appId: string; stage: string } | null>(null);
  const [noteText, setNoteText] = useState('');

  const loadApps = useCallback(async () => {
    try {
      const data = await listApplications();
      setApplications(data);
    } catch {
      // ignore
    }
  }, []);

  useEffect(() => {
    loadApps();
  }, [loadApps]);

  const handleStatusChange = async (appId: string, newStatus: AppStatus) => {
    try {
      const updated = await updateApplicationStatus(appId, newStatus);
      setApplications((prev) => prev.map((a) => (a.id === appId ? updated : a)));
    } catch {
      // ignore
    }
  };

  const handleDelete = async (appId: string) => {
    try {
      await deleteApplication(appId);
      setApplications((prev) => prev.filter((a) => a.id !== appId));
    } catch {
      // ignore
    }
  };

  const handleAddNote = async () => {
    if (!noteModal || !noteText.trim()) return;
    try {
      const updated = await addNote(noteModal.appId, noteModal.stage, noteText.trim());
      setApplications((prev) => prev.map((a) => (a.id === noteModal.appId ? updated : a)));
      setNoteModal(null);
      setNoteText('');
    } catch {
      // ignore
    }
  };

  const grouped = STAGES.map((stage) => ({
    ...stage,
    apps: applications.filter((a) => a.status === stage.key),
  }));

  const totalApplied = applications.filter((a) => a.status !== 'SAVED').length;
  const totalOffers = applications.filter((a) => a.status === 'OFFER').length;

  // For the note modal, find the application being noted
  const noteModalApp = useMemo(() => {
    if (!noteModal) return null;
    return applications.find((a) => a.id === noteModal.appId) || null;
  }, [noteModal, applications]);

  const existingNotes = useMemo(() => {
    if (!noteModalApp || !noteModal) return [];
    return getNotesForStage(noteModalApp, noteModal.stage).slice().sort(
      (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    );
  }, [noteModalApp, noteModal]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-foreground">Application Tracker</h1>
        <p className="text-muted-foreground">Track your applications through every stage.</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        <div className="rounded-xl border border-border bg-card px-5 py-4 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
              <Briefcase className="h-5 w-5 text-primary" />
            </div>
            <div>
              <p className="text-xs font-medium text-muted-foreground">Total</p>
              <p className="text-2xl font-bold text-foreground">{applications.length}</p>
            </div>
          </div>
        </div>
        <div className="rounded-xl border border-border bg-card px-5 py-4 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-500/10">
              <TrendingUp className="h-5 w-5 text-blue-500" />
            </div>
            <div>
              <p className="text-xs font-medium text-muted-foreground">Applied</p>
              <p className="text-2xl font-bold text-foreground">{totalApplied}</p>
            </div>
          </div>
        </div>
        <div className="rounded-xl border border-border bg-card px-5 py-4 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-500/10">
              <Trophy className="h-5 w-5 text-emerald-500" />
            </div>
            <div>
              <p className="text-xs font-medium text-muted-foreground">Offers</p>
              <p className="text-2xl font-bold text-foreground">{totalOffers}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Kanban */}
      <div className="flex gap-4 overflow-x-auto pb-4 snap-x snap-mandatory md:snap-none">
        {grouped.map((stage) => (
          <div key={stage.key} className="min-w-[260px] flex-shrink-0 snap-start">
            {/* Column Header */}
            <div className="mb-3 flex items-center gap-2.5 px-1">
              <div className={`h-2.5 w-2.5 rounded-full ${stage.dotColor} ring-2 ring-offset-2 ring-offset-background ${stage.dotColor.replace('bg-', 'ring-')}/30`} />
              <h3 className="text-sm font-semibold text-foreground">{stage.label}</h3>
              <span className="flex h-5 min-w-5 items-center justify-center rounded-full bg-muted px-1.5 text-xs font-medium text-muted-foreground">
                {stage.apps.length}
              </span>
            </div>

            {/* Column Body */}
            <div className="space-y-2.5 rounded-xl bg-muted/40 p-2.5 min-h-[220px] border border-border/50">
              {stage.apps.map((app) => {
                const noteCount = getTotalNoteCount(app);
                return (
                  <div
                    key={app.id}
                    className="rounded-xl border border-border bg-card p-3.5 shadow-sm transition-shadow hover:shadow-md"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="min-w-0 flex-1">
                        <p className="text-sm font-semibold text-foreground truncate">
                          {app.job_title || 'Unknown'}
                        </p>
                        <p className="text-xs text-muted-foreground truncate mt-0.5">
                          {app.job_company || ''}
                        </p>
                      </div>
                      <div className="flex items-center gap-0.5 shrink-0">
                        <button
                          onClick={() => setNoteModal({ appId: app.id, stage: stage.key })}
                          className="relative rounded-lg p-1.5 text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground"
                          title="Notes"
                        >
                          <MessageSquare className="h-3.5 w-3.5" />
                          {noteCount > 0 && (
                            <span className="absolute -right-1 -top-1 flex h-4 min-w-4 items-center justify-center rounded-full bg-primary px-1 text-[10px] font-bold text-primary-foreground">
                              {noteCount}
                            </span>
                          )}
                        </button>
                        <button
                          onClick={() => handleDelete(app.id)}
                          className="rounded-lg p-1.5 text-muted-foreground transition-colors hover:bg-red-500/10 hover:text-red-500"
                          title="Delete"
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </button>
                      </div>
                    </div>

                    {/* Move dropdown */}
                    <div className="mt-3">
                      <select
                        value={app.status}
                        onChange={(e) => handleStatusChange(app.id, e.target.value as AppStatus)}
                        className="w-full rounded-lg border border-input bg-background px-2.5 py-1.5 text-xs font-medium text-foreground transition-colors focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
                      >
                        {STAGES.map((s) => (
                          <option key={s.key} value={s.key}>{s.label}</option>
                        ))}
                      </select>
                    </div>
                  </div>
                );
              })}

              {stage.apps.length === 0 && (
                <div className="flex h-[180px] items-center justify-center">
                  <p className="text-xs text-muted-foreground/60">No applications</p>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Note Modal */}
      {noteModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
          <div className="w-full max-w-lg mx-4 rounded-xl border border-border bg-background p-6 shadow-2xl">
            {/* Modal Header */}
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-lg font-semibold text-foreground">Notes</h3>
                {noteModalApp && (
                  <p className="text-sm text-muted-foreground mt-0.5">
                    {noteModalApp.job_title} {noteModalApp.job_company ? `at ${noteModalApp.job_company}` : ''} &mdash;{' '}
                    <span className="font-medium">{STAGES.find((s) => s.key === noteModal.stage)?.label ?? noteModal.stage}</span>
                  </p>
                )}
              </div>
              <button
                onClick={() => { setNoteModal(null); setNoteText(''); }}
                className="rounded-lg p-1.5 text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            {/* Existing notes for this stage */}
            {existingNotes.length > 0 && (
              <div className="mb-4 max-h-56 space-y-2 overflow-y-auto rounded-lg border border-border bg-muted/30 p-3">
                <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2">
                  Previous Notes ({existingNotes.length})
                </p>
                {existingNotes.map((note, idx) => (
                  <div
                    key={idx}
                    className="rounded-lg border border-border bg-card p-3 shadow-sm"
                  >
                    <p className="text-sm text-foreground whitespace-pre-wrap">{note.content}</p>
                    <div className="mt-2 flex items-center gap-1.5 text-[11px] text-muted-foreground">
                      <Clock className="h-3 w-3" />
                      {formatNoteDate(note.created_at)}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {existingNotes.length === 0 && (
              <div className="mb-4 rounded-lg border border-dashed border-border bg-muted/20 p-4 text-center">
                <p className="text-sm text-muted-foreground">No notes yet for this stage.</p>
              </div>
            )}

            {/* Add new note */}
            <div>
              <label className="block text-sm font-medium text-foreground mb-1.5">Add a note</label>
              <textarea
                value={noteText}
                onChange={(e) => setNoteText(e.target.value)}
                rows={3}
                className="block w-full rounded-xl border border-input bg-background px-4 py-3 text-sm text-foreground placeholder:text-muted-foreground transition-colors focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary resize-none"
                placeholder="Write a note..."
              />
            </div>

            {/* Modal Actions */}
            <div className="mt-4 flex justify-end gap-2">
              <button
                onClick={() => { setNoteModal(null); setNoteText(''); }}
                className="rounded-lg border border-border bg-background px-4 py-2 text-sm font-medium text-foreground transition-colors hover:bg-accent"
              >
                Cancel
              </button>
              <button
                onClick={handleAddNote}
                disabled={!noteText.trim()}
                className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground shadow-sm transition-colors hover:bg-primary/90 disabled:opacity-50"
              >
                Save Note
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
