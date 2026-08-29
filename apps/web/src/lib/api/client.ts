import axios from 'axios';

const getApiBaseUrl = () => {
  const envUrl = import.meta.env.VITE_API_URL;
  if (envUrl) {
    return envUrl.endsWith('/api/v1') ? envUrl : `${envUrl.replace(/\/$/, '')}/api/v1`;
  }
  return '/api/v1';
};

export const API_BASE_URL = getApiBaseUrl();

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  withCredentials: true,
});

let accessToken: string | null = null;

export function setAccessToken(token: string | null) {
  accessToken = token;
  if (token) {
    sessionStorage.setItem('access_token', token);
  } else {
    sessionStorage.removeItem('access_token');
  }
}

export function getAccessToken(): string | null {
  if (!accessToken) {
    accessToken = sessionStorage.getItem('access_token');
  }
  return accessToken;
}

// Request interceptor: attach Bearer token
api.interceptors.request.use((config) => {
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
});

// Response interceptor: auto-refresh on 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Don't retry if it's already a retry, or if it's the refresh endpoint itself
    const isRefreshEndpoint = originalRequest.url?.includes('/auth/refresh');

    if (error.response?.status === 401 && !originalRequest._retry && !isRefreshEndpoint) {
      originalRequest._retry = true;
      try {
        const { data } = await axios.post(`${API_BASE_URL}/auth/refresh`, null, {
          withCredentials: true,
        });
        setAccessToken(data.access_token);
        originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
        return api(originalRequest);
      } catch {
        setAccessToken(null);
        // Don't hard redirect here - let React Router handle it
        return Promise.reject(error);
      }
    }
    return Promise.reject(error);
  }
);

export default api;
