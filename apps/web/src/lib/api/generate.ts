import api from './client';

export interface ResumeSuggestions {
  emphasize: string[];
  new_bullets: string[];
  professional_summary: string;
}

export interface CoverLetterResponse {
  content: string;
  job_id: string;
}

export interface EmailResponse {
  content: string;
  job_id: string;
}

export interface RoadmapItem {
  skill: string;
  importance: string;
  resources: string[];
  project_idea: string;
  estimated_time: string;
}

export interface PrepQuestion {
  category: string;
  question: string;
  suggested_answer: string | null;
  difficulty: string | null;
}

export interface PrepResponse {
  job_id: string;
  technical: PrepQuestion[];
  behavioral: PrepQuestion[];
  system_design: PrepQuestion[];
}

export async function getResumeSuggestions(jobId: string): Promise<ResumeSuggestions> {
  const { data } = await api.post(`/generate/resume-suggestions/${jobId}`);
  return data;
}

export async function getCoverLetter(jobId: string): Promise<CoverLetterResponse> {
  const { data } = await api.post(`/generate/cover-letter/${jobId}`);
  return data;
}

export async function getRecruiterEmail(jobId: string): Promise<EmailResponse> {
  const { data } = await api.post(`/generate/recruiter-email/${jobId}`);
  return data;
}

export async function getRoadmap(jobId: string): Promise<{ items: RoadmapItem[]; job_id: string }> {
  const { data } = await api.post(`/generate/roadmap/${jobId}`);
  return data;
}

export async function getPrepQuestions(jobId: string): Promise<PrepResponse> {
  const { data } = await api.post(`/prep/questions/${jobId}`);
  return data;
}
