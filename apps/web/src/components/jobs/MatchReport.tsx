import { Loader2, TrendingUp, AlertTriangle, MessageSquare } from 'lucide-react';
import type { MatchResult } from '@/lib/api/jobs';

interface MatchReportProps {
  match: MatchResult | null;
  loading: boolean;
}

function getScoreColor(score: number): string {
  if (score >= 75) return 'text-emerald-600 dark:text-emerald-400';
  if (score >= 50) return 'text-amber-600 dark:text-amber-400';
  return 'text-red-600 dark:text-red-400';
}

function getScoreBg(score: number): string {
  if (score >= 75) return 'stroke-emerald-500';
  if (score >= 50) return 'stroke-amber-500';
  return 'stroke-red-500';
}

export default function MatchReport({ match, loading }: MatchReportProps) {
  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-12">
        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10">
          <Loader2 className="h-5 w-5 animate-spin text-primary" />
        </div>
        <span className="mt-3 text-sm text-muted-foreground">Computing match score...</span>
      </div>
    );
  }

  if (!match) return null;

  const circumference = 2 * Math.PI * 40;
  const offset = circumference - (match.score / 100) * circumference;

  return (
    <div className="space-y-5">
      {/* Score Ring */}
      <div className="flex items-center gap-5 rounded-xl bg-muted/50 p-4">
        <div className="relative h-24 w-24 shrink-0">
          <svg className="h-24 w-24 -rotate-90" viewBox="0 0 100 100">
            <circle
              cx="50" cy="50" r="40" fill="none" stroke="currentColor" strokeWidth="8"
              className="text-border"
            />
            <circle
              cx="50" cy="50" r="40" fill="none" strokeWidth="8" strokeLinecap="round"
              className={getScoreBg(match.score)}
              strokeDasharray={circumference}
              strokeDashoffset={offset}
              style={{ transition: 'stroke-dashoffset 0.6s ease' }}
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <span className={`text-2xl font-bold ${getScoreColor(match.score)}`}>
              {Math.round(match.score)}
            </span>
          </div>
        </div>
        <div>
          <h3 className="text-lg font-semibold text-foreground">Match Score</h3>
          <p className="mt-0.5 text-sm text-muted-foreground">
            {match.score >= 75 ? 'Strong match' : match.score >= 50 ? 'Moderate match' : 'Weak match'}
          </p>
        </div>
      </div>

      {/* Strong Points */}
      {match.strong_points.length > 0 && (
        <div className="rounded-xl border border-border bg-card p-4">
          <h4 className="flex items-center gap-2 text-sm font-semibold text-foreground">
            <div className="flex h-6 w-6 items-center justify-center rounded-md bg-emerald-500/10">
              <TrendingUp className="h-3.5 w-3.5 text-emerald-500" />
            </div>
            Strong Points
          </h4>
          <div className="mt-3 flex flex-wrap gap-2">
            {match.strong_points.map((point, i) => (
              <span
                key={i}
                className="rounded-full border border-emerald-500/20 bg-emerald-500/10 px-3 py-1 text-xs font-medium text-emerald-600 dark:text-emerald-400"
              >
                {point}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Skill Gaps */}
      {match.skill_gaps.length > 0 && (
        <div className="rounded-xl border border-border bg-card p-4">
          <h4 className="flex items-center gap-2 text-sm font-semibold text-foreground">
            <div className="flex h-6 w-6 items-center justify-center rounded-md bg-amber-500/10">
              <AlertTriangle className="h-3.5 w-3.5 text-amber-500" />
            </div>
            Skill Gaps
          </h4>
          <div className="mt-3 flex flex-wrap gap-2">
            {match.skill_gaps.map((gap, i) => (
              <span
                key={i}
                className="rounded-full border border-amber-500/20 bg-amber-500/10 px-3 py-1 text-xs font-medium text-amber-600 dark:text-amber-400"
              >
                {gap}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Reasoning */}
      {match.reasoning && (
        <div className="rounded-xl border border-border bg-card p-4">
          <h4 className="flex items-center gap-2 text-sm font-semibold text-foreground">
            <div className="flex h-6 w-6 items-center justify-center rounded-md bg-primary/10">
              <MessageSquare className="h-3.5 w-3.5 text-primary" />
            </div>
            Analysis
          </h4>
          <p className="mt-3 text-sm leading-relaxed text-muted-foreground">{match.reasoning}</p>
        </div>
      )}
    </div>
  );
}
