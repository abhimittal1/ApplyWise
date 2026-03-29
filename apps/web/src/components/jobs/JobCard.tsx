import { Trash2, ExternalLink, MapPin, Briefcase, ClipboardPlus, Check } from 'lucide-react';
import type { JobInfo } from '@/lib/api/jobs';

interface JobCardProps {
  job: JobInfo;
  onDelete: (id: string) => void;
  onSelect: (id: string) => void;
  onTrack: (id: string) => void;
  isTracked: boolean;
  matchScore?: number | null;
}

function getScoreColor(score: number): string {
  if (score >= 75) return 'text-emerald-600 dark:text-emerald-400 bg-emerald-500/10';
  if (score >= 50) return 'text-amber-600 dark:text-amber-400 bg-amber-500/10';
  return 'text-red-600 dark:text-red-400 bg-red-500/10';
}

export default function JobCard({ job, onDelete, onSelect, onTrack, isTracked, matchScore }: JobCardProps) {
  const score = matchScore ?? job.match_score;

  return (
    <div
      className="group cursor-pointer rounded-xl border border-border bg-card p-4 shadow-sm transition-all hover:shadow-md hover:border-primary/30"
      onClick={() => onSelect(job.id)}
    >
      <div className="flex items-start justify-between gap-3">
        {/* Left: Job info */}
        <div className="min-w-0 flex-1">
          <h3 className="font-medium text-foreground truncate">{job.title}</h3>
          <p className="mt-0.5 text-sm text-muted-foreground">{job.company}</p>

          <div className="mt-2.5 flex flex-wrap items-center gap-2">
            {job.location && (
              <span className="inline-flex items-center gap-1 rounded-md bg-muted px-2 py-0.5 text-xs text-muted-foreground">
                <MapPin className="h-3 w-3" />
                {job.location}
              </span>
            )}
            {job.job_type && (
              <span className="inline-flex items-center gap-1 rounded-md bg-muted px-2 py-0.5 text-xs text-muted-foreground">
                <Briefcase className="h-3 w-3" />
                {job.job_type}
              </span>
            )}
            {job.remote && (
              <span className="inline-flex items-center rounded-full bg-primary/10 px-2.5 py-0.5 text-xs font-medium text-primary">
                Remote
              </span>
            )}
          </div>
        </div>

        {/* Right: Score + actions */}
        <div className="flex shrink-0 items-center gap-2">
          {score != null && (
            <div className={`rounded-full px-2.5 py-1 text-sm font-semibold ${getScoreColor(score)}`}>
              {Math.round(score)}%
            </div>
          )}

          <button
            onClick={(e) => { e.stopPropagation(); if (!isTracked) onTrack(job.id); }}
            disabled={isTracked}
            className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-medium transition-colors ${
              isTracked
                ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 cursor-default'
                : 'border border-primary/30 text-primary hover:bg-primary/10'
            }`}
            title={isTracked ? 'Already tracked' : 'Track application'}
          >
            {isTracked ? <Check className="h-3.5 w-3.5" /> : <ClipboardPlus className="h-3.5 w-3.5" />}
            {isTracked ? 'Tracked' : 'Track'}
          </button>

          {job.url && (
            <a
              href={job.url}
              target="_blank"
              rel="noopener noreferrer"
              onClick={(e) => e.stopPropagation()}
              className="rounded-lg p-1.5 text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
            >
              <ExternalLink className="h-4 w-4" />
            </a>
          )}

          <button
            onClick={(e) => { e.stopPropagation(); onDelete(job.id); }}
            className="rounded-lg p-1.5 text-muted-foreground transition-colors hover:bg-red-500/10 hover:text-red-500"
          >
            <Trash2 className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
