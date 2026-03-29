import { useState, useEffect, useCallback } from 'react';
import { Plus, Briefcase, MousePointerClick } from 'lucide-react';
import JobCard from '@/components/jobs/JobCard';
import MatchReport from '@/components/jobs/MatchReport';
import AddJobModal from '@/components/jobs/AddJobModal';
import { listJobs, deleteJob, matchJob, type JobInfo, type MatchResult } from '@/lib/api/jobs';
import { listApplications, createApplication } from '@/lib/api/tracker';

export default function JobsPage() {
  const [jobs, setJobs] = useState<JobInfo[]>([]);
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedJobId, setSelectedJobId] = useState<string | null>(null);
  const [matchResult, setMatchResult] = useState<MatchResult | null>(null);
  const [matchLoading, setMatchLoading] = useState(false);
  const [trackedJobIds, setTrackedJobIds] = useState<Set<string>>(new Set());

  const loadJobs = useCallback(async () => {
    try {
      const data = await listJobs();
      setJobs(data);
    } catch {
      // ignore
    }
  }, []);

  const loadTrackedApps = useCallback(async () => {
    try {
      const apps = await listApplications();
      setTrackedJobIds(new Set(apps.map((a) => a.job_id)));
    } catch {
      // ignore
    }
  }, []);

  useEffect(() => {
    loadJobs();
    loadTrackedApps();
  }, [loadJobs, loadTrackedApps]);

  const handleDelete = async (id: string) => {
    try {
      await deleteJob(id);
      setJobs((prev) => prev.filter((j) => j.id !== id));
      if (selectedJobId === id) {
        setSelectedJobId(null);
        setMatchResult(null);
      }
    } catch {
      // ignore
    }
  };

  const handleSelect = async (id: string) => {
    setSelectedJobId(id);
    setMatchResult(null);
    setMatchLoading(true);
    try {
      const result = await matchJob(id);
      setMatchResult(result);
    } catch {
      setMatchResult(null);
    } finally {
      setMatchLoading(false);
    }
  };

  const handleTrack = async (jobId: string) => {
    try {
      await createApplication(jobId, 'SAVED');
      setTrackedJobIds((prev) => new Set(prev).add(jobId));
    } catch {
      // ignore — likely already tracked
    }
  };

  const selectedJob = jobs.find((j) => j.id === selectedJobId);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground">Jobs</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Manage your job listings and match scores.
          </p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-primary px-4 py-2.5 text-sm font-medium text-primary-foreground shadow-sm transition-colors hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50"
        >
          <Plus className="h-4 w-4" />
          Add Job
        </button>
      </div>

      {/* Main content — stacks on mobile, side-by-side on large */}
      <div className="flex flex-col gap-6 lg:grid lg:grid-cols-5">
        {/* Job list */}
        <div className="lg:col-span-3 space-y-3">
          {jobs.length === 0 ? (
            <div className="rounded-xl border border-dashed border-border bg-card p-12 text-center shadow-sm">
              <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
                <Briefcase className="h-6 w-6 text-primary" />
              </div>
              <h3 className="text-sm font-medium text-foreground">No jobs yet</h3>
              <p className="mt-1 text-sm text-muted-foreground">
                Add your first job to get started with match scoring.
              </p>
            </div>
          ) : (
            jobs.map((job) => (
              <JobCard
                key={job.id}
                job={job}
                onDelete={handleDelete}
                onSelect={handleSelect}
                onTrack={handleTrack}
                isTracked={trackedJobIds.has(job.id)}
                matchScore={selectedJobId === job.id && matchResult ? matchResult.score : undefined}
              />
            ))
          )}
        </div>

        {/* Match report panel */}
        <div className="lg:col-span-2">
          {selectedJob ? (
            <div className="rounded-xl border border-border bg-card p-5 shadow-sm">
              <h2 className="text-base font-semibold text-foreground">{selectedJob.title}</h2>
              <p className="mt-0.5 text-sm text-muted-foreground">{selectedJob.company}</p>
              <div className="mt-5">
                <MatchReport match={matchResult} loading={matchLoading} />
              </div>
            </div>
          ) : (
            <div className="rounded-xl border border-dashed border-border bg-card p-12 text-center shadow-sm">
              <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-muted">
                <MousePointerClick className="h-6 w-6 text-muted-foreground" />
              </div>
              <h3 className="text-sm font-medium text-foreground">No job selected</h3>
              <p className="mt-1 text-sm text-muted-foreground">
                Select a job to see the match report.
              </p>
            </div>
          )}
        </div>
      </div>

      <AddJobModal isOpen={showAddModal} onClose={() => setShowAddModal(false)} onJobAdded={loadJobs} />
    </div>
  );
}
