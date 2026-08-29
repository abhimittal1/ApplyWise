import { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from '@/lib/auth/AuthContext';
import { ThemeProvider } from '@/lib/theme';
import { ProtectedRoute } from '@/lib/auth/ProtectedRoute';
import AppLayout from '@/components/shared/AppLayout';

// Public pages loaded directly for instant initial paint
import LandingPage from '@/pages/landing/LandingPage';
import LoginPage from '@/pages/auth/LoginPage';
import RegisterPage from '@/pages/auth/RegisterPage';
import AuthCallbackPage from '@/pages/auth/AuthCallbackPage';

// Lazy-load protected dashboard pages to keep public landing bundle lightweight
const DashboardPage = lazy(() => import('@/pages/DashboardPage'));
const KnowledgePage = lazy(() => import('@/pages/knowledge/KnowledgePage'));
const JobsPage = lazy(() => import('@/pages/jobs/JobsPage'));
const TrackerPage = lazy(() => import('@/pages/tracker/TrackerPage'));
const PrepPage = lazy(() => import('@/pages/prep/PrepPage'));
const SettingsPage = lazy(() => import('@/pages/settings/SettingsPage'));

function PageLoader() {
  return (
    <div className="flex h-64 w-full items-center justify-center">
      <div className="h-7 w-7 animate-spin rounded-full border-3 border-primary border-t-transparent" />
    </div>
  );
}

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,
      retry: 1,
    },
  },
});

export default function Router() {
  return (
    <ThemeProvider>
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <BrowserRouter>
            <Routes>
              {/* Public routes */}
              <Route path="/" element={<LandingPage />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              <Route path="/auth/callback" element={<AuthCallbackPage />} />

              {/* Protected App routes */}
              <Route
                path="/app"
                element={
                  <ProtectedRoute>
                    <AppLayout />
                  </ProtectedRoute>
                }
              >
                <Route
                  index
                  element={
                    <Suspense fallback={<PageLoader />}>
                      <DashboardPage />
                    </Suspense>
                  }
                />
                <Route
                  path="dashboard"
                  element={
                    <Suspense fallback={<PageLoader />}>
                      <DashboardPage />
                    </Suspense>
                  }
                />
                <Route
                  path="knowledge"
                  element={
                    <Suspense fallback={<PageLoader />}>
                      <KnowledgePage />
                    </Suspense>
                  }
                />
                <Route
                  path="jobs"
                  element={
                    <Suspense fallback={<PageLoader />}>
                      <JobsPage />
                    </Suspense>
                  }
                />
                <Route
                  path="tracker"
                  element={
                    <Suspense fallback={<PageLoader />}>
                      <TrackerPage />
                    </Suspense>
                  }
                />
                <Route
                  path="prep"
                  element={
                    <Suspense fallback={<PageLoader />}>
                      <PrepPage />
                    </Suspense>
                  }
                />
                <Route
                  path="settings"
                  element={
                    <Suspense fallback={<PageLoader />}>
                      <SettingsPage />
                    </Suspense>
                  }
                />
              </Route>

              {/* Backward compatibility redirects */}
              <Route path="/dashboard" element={<Navigate to="/app" replace />} />
              <Route path="/knowledge" element={<Navigate to="/app/knowledge" replace />} />
              <Route path="/jobs" element={<Navigate to="/app/jobs" replace />} />
              <Route path="/tracker" element={<Navigate to="/app/tracker" replace />} />
              <Route path="/prep" element={<Navigate to="/app/prep" replace />} />
              <Route path="/settings" element={<Navigate to="/app/settings" replace />} />

              {/* Fallback */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </BrowserRouter>
        </AuthProvider>
      </QueryClientProvider>
    </ThemeProvider>
  );
}
