import api from './client';

export type AppStatus = 'SAVED' | 'APPLIED' | 'OA' | 'INTERVIEW' | 'OFFER' | 'REJECTED';

export interface ApplicationInfo {
  id: string;
  job_id: string;
  status: AppStatus;
  applied_at: string | null;
  oa_date: string | null;
  interview_date: string | null;
  offer_date: string | null;
  recruiter_name: string | null;
  recruiter_email: string | null;
  notes: Record<string, { content: string; created_at: string }[]> | null;
  created_at: string;
  job_title: string | null;
  job_company: string | null;
}

export async function listApplications(): Promise<ApplicationInfo[]> {
  const { data } = await api.get('/tracker');
  return data;
}

export async function createApplication(jobId: string, status: AppStatus = 'SAVED'): Promise<ApplicationInfo> {
  const { data } = await api.post('/tracker', { job_id: jobId, status });
  return data;
}

export async function updateApplicationStatus(id: string, status: AppStatus): Promise<ApplicationInfo> {
  const { data } = await api.patch(`/tracker/${id}/status`, { status });
  return data;
}

export async function addNote(id: string, stage: string, content: string): Promise<ApplicationInfo> {
  const { data } = await api.post(`/tracker/${id}/notes`, { stage, content });
  return data;
}

export async function deleteApplication(id: string): Promise<void> {
  await api.delete(`/tracker/${id}`);
}
