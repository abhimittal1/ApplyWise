import { useState, useEffect } from 'react';
import { useAuth } from '@/lib/auth/AuthContext';
import { listDocuments, type DocumentInfo } from '@/lib/api/documents';
import { listJobs, type JobInfo } from '@/lib/api/jobs';
import { listApplications, type ApplicationInfo } from '@/lib/api/tracker';
import { FileText, Briefcase, ClipboardList, TrendingUp, ArrowRight, Upload } from 'lucide-react';
import { Link } from 'react-router-dom';

function statusBadge(status: string) {
  const config: Record<string, { bg: string; text: string; label: string }> = {
    READY: { bg: 'bg-green-500/10', text: 'text-green-600 dark:text-green-400', label: 'Ready' },
    PROCESSING: { bg: 'bg-yellow-500/10', text: 'text-yellow-600 dark:text-yellow-400', label: 'Processing' },
    FAILED: { bg: 'bg-red-500/10', text: 'text-red-600 dark:text-red-400', label: 'Failed' },
  };
  const c = config[status] || { bg: 'bg-muted', text: 'text-muted-foreground', label: status };
  return <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${c.bg} ${c.text}`}>{c.label}</span>;
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

export default function DashboardPage() {
  const { user } = useAuth();
  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [jobs, setJobs] = useState<JobInfo[]>([]);
  const [applications, setApplications] = useState<ApplicationInfo[]>([]);

  useEffect(() => {
    listDocuments().then(setDocuments).catch(() => {});
    listJobs().then(setJobs).catch(() => {});
    listApplications().then(setApplications).catch(() => {});
  }, []);

  const avgMatchScore = (() => {
    const scored = jobs.filter((j) => j.match_score != null);
    return scored.length > 0
      ? Math.round(scored.reduce((s, j) => s + (j.match_score ?? 0), 0) / scored.length)
      : null;
  })();

  const stats = [
    { label: 'Documents', value: documents.length, icon: FileText, color: 'text-blue-500', bg: 'bg-blue-500/10' },
    { label: 'Jobs Saved', value: jobs.length, icon: Briefcase, color: 'text-primary', bg: 'bg-primary/10' },
    { label: 'Applications', value: applications.length, icon: ClipboardList, color: 'text-emerald-500', bg: 'bg-emerald-500/10' },
    { label: 'Avg Match', value: avgMatchScore != null ? `${avgMatchScore}%` : '—', icon: TrendingUp, color: 'text-amber-500', bg: 'bg-amber-500/10' },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">
          Welcome back, {user?.name?.split(' ')[0]}
        </h1>
        <p className="text-muted-foreground">Your AI career intelligence dashboard.</p>
      </div>

      {/* Stat cards */}
      <div className="grid gap-4 grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <div key={stat.label} className="rounded-xl border border-border bg-card p-5 shadow-sm transition-shadow hover:shadow-md">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium text-muted-foreground">{stat.label}</p>
              <div className={`flex h-9 w-9 items-center justify-center rounded-lg ${stat.bg}`}>
                <stat.icon className={`h-[18px] w-[18px] ${stat.color}`} />
              </div>
            </div>
            <p className="mt-3 text-3xl font-bold">{stat.value}</p>
          </div>
        ))}
      </div>

      {/* Recent sections */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Recent Documents */}
        <div className="rounded-xl border border-border bg-card shadow-sm">
          <div className="flex items-center justify-between border-b border-border px-5 py-4">
            <h2 className="font-semibold">Recent Documents</h2>
            <Link to="/knowledge" className="flex items-center gap-1 text-xs font-medium text-primary hover:underline">
              View all <ArrowRight className="h-3 w-3" />
            </Link>
          </div>
          <div className="p-5">
            {documents.length === 0 ? (
              <Link to="/knowledge" className="flex flex-col items-center gap-3 rounded-lg border-2 border-dashed border-border py-8 text-center transition-colors hover:border-primary/50 hover:bg-accent/50">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                  <Upload className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <p className="text-sm font-medium">Upload your first document</p>
                  <p className="text-xs text-muted-foreground">Resume, cover letter, or project notes</p>
                </div>
              </Link>
            ) : (
              <div className="space-y-3">
                {documents.slice(0, 5).map((doc) => (
                  <div key={doc.id} className="flex items-center justify-between rounded-lg p-2 transition-colors hover:bg-accent/50">
                    <div className="flex items-center gap-3">
                      <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-blue-500/10">
                        <FileText className="h-4 w-4 text-blue-500" />
                      </div>
                      <div>
                        <p className="text-sm font-medium">{doc.filename}</p>
                        <p className="text-xs text-muted-foreground">{formatDate(doc.created_at)}</p>
                      </div>
                    </div>
                    {statusBadge(doc.status)}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Recent Jobs */}
        <div className="rounded-xl border border-border bg-card shadow-sm">
          <div className="flex items-center justify-between border-b border-border px-5 py-4">
            <h2 className="font-semibold">Recent Jobs</h2>
            <Link to="/jobs" className="flex items-center gap-1 text-xs font-medium text-primary hover:underline">
              View all <ArrowRight className="h-3 w-3" />
            </Link>
          </div>
          <div className="p-5">
            {jobs.length === 0 ? (
              <Link to="/jobs" className="flex flex-col items-center gap-3 rounded-lg border-2 border-dashed border-border py-8 text-center transition-colors hover:border-primary/50 hover:bg-accent/50">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                  <Briefcase className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <p className="text-sm font-medium">Add your first job</p>
                  <p className="text-xs text-muted-foreground">Manual, paste, URL import, or search</p>
                </div>
              </Link>
            ) : (
              <div className="space-y-3">
                {jobs.slice(0, 5).map((job) => (
                  <div key={job.id} className="flex items-center justify-between rounded-lg p-2 transition-colors hover:bg-accent/50">
                    <div>
                      <p className="text-sm font-medium">{job.title}</p>
                      <p className="text-xs text-muted-foreground">{job.company}</p>
                    </div>
                    {job.match_score != null && (
                      <span className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${
                        job.match_score >= 75 ? 'bg-green-500/10 text-green-600 dark:text-green-400' :
                        job.match_score >= 50 ? 'bg-yellow-500/10 text-yellow-600 dark:text-yellow-400' :
                        'bg-red-500/10 text-red-600 dark:text-red-400'
                      }`}>
                        {Math.round(job.match_score)}%
                      </span>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
