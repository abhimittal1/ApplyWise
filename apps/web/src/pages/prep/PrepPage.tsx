import { useState } from 'react';
import { Loader2, Eye, EyeOff, Brain, Users, Server, Sparkles } from 'lucide-react';
import { getPrepQuestions, type PrepQuestion, type PrepResponse } from '@/lib/api/generate';
import { listJobs, type JobInfo } from '@/lib/api/jobs';
import { useEffect } from 'react';

const TABS = [
  { key: 'technical' as const, label: 'Technical', icon: Brain },
  { key: 'behavioral' as const, label: 'Behavioral', icon: Users },
  { key: 'system_design' as const, label: 'System Design', icon: Server },
];

export default function PrepPage() {
  const [jobs, setJobs] = useState<JobInfo[]>([]);
  const [selectedJobId, setSelectedJobId] = useState<string | null>(null);
  const [prep, setPrep] = useState<PrepResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'technical' | 'behavioral' | 'system_design'>('technical');
  const [revealedAnswers, setRevealedAnswers] = useState<Set<number>>(new Set());

  useEffect(() => {
    listJobs().then(setJobs).catch(() => {});
  }, []);

  const handleGenerate = async () => {
    if (!selectedJobId) return;
    setLoading(true);
    setPrep(null);
    setRevealedAnswers(new Set());
    try {
      const result = await getPrepQuestions(selectedJobId);
      setPrep(result);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  };

  const toggleAnswer = (index: number) => {
    setRevealedAnswers((prev) => {
      const next = new Set(prev);
      if (next.has(index)) next.delete(index);
      else next.add(index);
      return next;
    });
  };

  const getQuestions = (): PrepQuestion[] => {
    if (!prep) return [];
    return prep[activeTab] || [];
  };

  const questions = getQuestions();

  const difficultyConfig = {
    hard: { bg: 'bg-red-500/10 dark:bg-red-500/20', text: 'text-red-600 dark:text-red-400', dot: 'bg-red-500' },
    medium: { bg: 'bg-amber-500/10 dark:bg-amber-500/20', text: 'text-amber-600 dark:text-amber-400', dot: 'bg-amber-500' },
    easy: { bg: 'bg-emerald-500/10 dark:bg-emerald-500/20', text: 'text-emerald-600 dark:text-emerald-400', dot: 'bg-emerald-500' },
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-foreground">Interview Prep</h1>
        <p className="text-muted-foreground">AI-generated practice questions tailored to each role.</p>
      </div>

      {/* Job selector */}
      <div className="rounded-xl border border-border bg-card p-5 shadow-sm">
        <label className="block text-sm font-semibold text-foreground mb-2">Select a job</label>
        <div className="flex gap-3 items-end">
          <div className="flex-1">
            <select
              value={selectedJobId || ''}
              onChange={(e) => setSelectedJobId(e.target.value || null)}
              className="w-full rounded-lg border border-input bg-background px-3.5 py-2.5 text-sm text-foreground transition-colors focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
            >
              <option value="">Choose a job...</option>
              {jobs.map((job) => (
                <option key={job.id} value={job.id}>{job.title} — {job.company}</option>
              ))}
            </select>
          </div>
          <button
            onClick={handleGenerate}
            disabled={!selectedJobId || loading}
            className="inline-flex items-center gap-2 rounded-lg bg-primary px-5 py-2.5 text-sm font-medium text-primary-foreground shadow-sm transition-colors hover:bg-primary/90 disabled:opacity-50"
          >
            {loading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Sparkles className="h-4 w-4" />
            )}
            {loading ? 'Generating...' : 'Generate Questions'}
          </button>
        </div>
      </div>

      {prep && (
        <>
          {/* Tabs */}
          <div className="flex gap-1 rounded-lg bg-muted p-1">
            {TABS.map((tab) => {
              const Icon = tab.icon;
              const count = (prep[tab.key] || []).length;
              return (
                <button
                  key={tab.key}
                  onClick={() => { setActiveTab(tab.key); setRevealedAnswers(new Set()); }}
                  className={`flex flex-1 items-center justify-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-all ${
                    activeTab === tab.key
                      ? 'bg-background text-foreground shadow-sm'
                      : 'text-muted-foreground hover:text-foreground'
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  <span>{tab.label}</span>
                  <span className={`flex h-5 min-w-5 items-center justify-center rounded-full px-1.5 text-xs font-semibold ${
                    activeTab === tab.key
                      ? 'bg-primary/10 text-primary'
                      : 'bg-muted-foreground/10 text-muted-foreground'
                  }`}>
                    {count}
                  </span>
                </button>
              );
            })}
          </div>

          {/* Questions */}
          <div className="space-y-3">
            {questions.map((q, i) => {
              const difficulty = (q.difficulty || 'medium') as keyof typeof difficultyConfig;
              const dc = difficultyConfig[difficulty] || difficultyConfig.medium;
              return (
                <div
                  key={i}
                  className="rounded-xl border border-border bg-card p-5 shadow-sm transition-shadow hover:shadow-md"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-xs font-semibold text-muted-foreground">Q{i + 1}</span>
                        {q.difficulty && (
                          <span className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-semibold ${dc.bg} ${dc.text}`}>
                            <span className={`h-1.5 w-1.5 rounded-full ${dc.dot}`} />
                            {q.difficulty.charAt(0).toUpperCase() + q.difficulty.slice(1)}
                          </span>
                        )}
                      </div>
                      <p className="text-[15px] font-medium text-foreground leading-relaxed">{q.question}</p>
                    </div>
                    <button
                      onClick={() => toggleAnswer(i)}
                      className={`shrink-0 rounded-lg p-2 transition-colors ${
                        revealedAnswers.has(i)
                          ? 'bg-primary/10 text-primary'
                          : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                      }`}
                      title={revealedAnswers.has(i) ? 'Hide answer' : 'Show answer'}
                    >
                      {revealedAnswers.has(i) ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>

                  {revealedAnswers.has(i) && q.suggested_answer && (
                    <div className="mt-4 rounded-lg border border-primary/20 bg-primary/5 p-4">
                      <p className="text-xs font-semibold uppercase tracking-wider text-primary mb-2">
                        Suggested Answer
                      </p>
                      <p className="text-sm text-foreground leading-relaxed whitespace-pre-wrap">
                        {q.suggested_answer}
                      </p>
                    </div>
                  )}
                </div>
              );
            })}
            {questions.length === 0 && (
              <div className="rounded-xl border border-dashed border-border bg-card/50 py-12 text-center">
                <p className="text-sm text-muted-foreground">No questions generated for this category.</p>
              </div>
            )}
          </div>
        </>
      )}

      {!prep && !loading && (
        <div className="rounded-xl border border-dashed border-border bg-card/50 py-16 text-center">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-primary/10 mb-4">
            <Sparkles className="h-7 w-7 text-primary" />
          </div>
          <p className="text-foreground font-medium">Ready to practice?</p>
          <p className="mt-1 text-sm text-muted-foreground">
            Select a job and click "Generate Questions" to get started.
          </p>
        </div>
      )}

      {loading && !prep && (
        <div className="rounded-xl border border-border bg-card py-16 text-center shadow-sm">
          <Loader2 className="mx-auto h-8 w-8 animate-spin text-primary mb-4" />
          <p className="text-foreground font-medium">Generating questions...</p>
          <p className="mt-1 text-sm text-muted-foreground">This may take a moment.</p>
        </div>
      )}
    </div>
  );
}
