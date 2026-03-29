import api from './client';

export interface DocumentInfo {
  id: string;
  filename: string;
  file_type: string;
  status: 'UPLOADING' | 'PROCESSING' | 'READY' | 'FAILED';
  created_at: string;
}

export interface DocumentDetail extends DocumentInfo {
  extracted_text: string | null;
  chunk_count: number;
}

export async function uploadDocument(file: File): Promise<DocumentInfo> {
  const formData = new FormData();
  formData.append('file', file);
  const { data } = await api.post('/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
}

export async function listDocuments(): Promise<DocumentInfo[]> {
  const { data } = await api.get('/documents');
  return data;
}

export async function getDocument(id: string): Promise<DocumentDetail> {
  const { data } = await api.get(`/documents/${id}`);
  return data;
}

export async function getDocumentStatus(id: string): Promise<{ id: string; status: string; filename: string }> {
  const { data } = await api.get(`/documents/${id}/status`);
  return data;
}

export async function deleteDocument(id: string): Promise<void> {
  await api.delete(`/documents/${id}`);
}
