import api from './client';

export interface JobInfo {
  id: string;
  title: string;
  company: string;
  location: string | null;
  description: string | null;
  url: string | null;
  source: string;
  remote: boolean;
  job_type: string | null;
  posted_at: string | null;
  deadline: string | null;
  match_score: number | null;
  created_at: string;
}

export interface JobPreview {
  title: string;
  company: string;
  location: string | null;
  description: string | null;
  requirements: string[];
  url: string | null;
}

export interface MatchResult {
  score: number;
  strong_points: string[];
  skill_gaps: string[];
  reasoning: string;
  component_scores: Record<string, number>;
}

export async function createJob(job: {
  title: string;
  company: string;
  location?: string;
  description?: string;
  url?: string;
  remote?: boolean;
  job_type?: string;
}): Promise<JobInfo> {
  const { data } = await api.post('/jobs', job);
  return data;
}

export async function importJobFromText(rawText: string): Promise<JobPreview> {
  const { data } = await api.post('/jobs/import-text', { raw_text: rawText });
  return data;
}

export async function confirmTextImport(job: {
  title: string;
  company: string;
  location?: string;
  description?: string;
}): Promise<JobInfo> {
  const { data } = await api.post('/jobs/import-text/confirm', job);
  return data;
}

export async function importJobFromURL(url: string): Promise<JobPreview> {
  const { data } = await api.post('/jobs/import-url', { url });
  return data;
}

export async function confirmUrlImport(job: {
  title: string;
  company: string;
  location?: string;
  description?: string;
  url?: string;
}): Promise<JobInfo> {
  const { data } = await api.post('/jobs/import-url/confirm', job);
  return data;
}

export interface JobSearchResponse {
  results: JobPreview[];
  total: number;
  apis_used: string[];
}

export async function searchJobs(query: string, location?: string): Promise<JobSearchResponse> {
  const { data } = await api.post('/jobs/search', { query, location: location || '' });
  return data;
}

export async function saveSearchResult(job: {
  title: string;
  company: string;
  location?: string;
  description?: string;
  url?: string;
}): Promise<JobInfo> {
  const { data } = await api.post('/jobs/search/save', job);
  return data;
}

export async function listJobs(): Promise<JobInfo[]> {
  const { data } = await api.get('/jobs');
  return data;
}

export async function getJob(id: string): Promise<JobInfo> {
  const { data } = await api.get(`/jobs/${id}`);
  return data;
}

export async function deleteJob(id: string): Promise<void> {
  await api.delete(`/jobs/${id}`);
}

export async function matchJob(jobId: string): Promise<MatchResult> {
  const { data } = await api.post(`/matching/jobs/${jobId}/match`);
  return data;
}

export async function rematchAllJobs(): Promise<void> {
  await api.post('/matching/jobs/rematch-all');
}
