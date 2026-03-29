import { createContext, useContext, useEffect, useState, type ReactNode } from 'react';
import api, { setAccessToken, getAccessToken } from '@/lib/api/client';

interface User {
  id: string;
  email: string;
  name: string;
  avatar_url: string | null;
  created_at: string;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name: string) => Promise<void>;
  logout: () => Promise<void>;
  googleLogin: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check for OAuth callback token in URL fragment
    const hash = window.location.hash;
    if (hash.includes('token=')) {
      const token = hash.split('token=')[1];
      setAccessToken(token);
      window.history.replaceState(null, '', window.location.pathname);
    }

    // Try to restore session
    const initAuth = async () => {
      try {
        // Try to get existing token or refresh if we have a refresh token cookie
        if (!getAccessToken()) {
          try {
            const { data } = await api.post('/auth/refresh');
            setAccessToken(data.access_token);
          } catch {
            // No valid refresh token, user needs to login
            setIsLoading(false);
            return;
          }
        }
        const { data: userData } = await api.get('/auth/me');
        setUser(userData);
      } catch {
        setAccessToken(null);
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    };
    initAuth();
  }, []);

  const login = async (email: string, password: string) => {
    const { data } = await api.post('/auth/login', { email, password });
    setAccessToken(data.access_token);
    setUser(data.user);
  };

  const register = async (email: string, password: string, name: string) => {
    const { data } = await api.post('/auth/register', { email, password, name });
    setAccessToken(data.access_token);
    setUser(data.user);
  };

  const logout = async () => {
    try {
      await api.post('/auth/logout');
    } finally {
      setAccessToken(null);
      setUser(null);
    }
  };

  const googleLogin = () => {
    window.location.href = '/api/v1/auth/google';
  };

  return (
    <AuthContext.Provider value={{ user, isLoading, login, register, logout, googleLogin }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
}
