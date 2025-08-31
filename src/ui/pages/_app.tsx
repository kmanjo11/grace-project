import React, { useEffect, useState, useRef, useMemo } from 'react';
import { AppProps } from 'next/app';
import { useRouter } from 'next/router';
import { AuthProvider, useAuth } from '../components/AuthContext';
import { AppStateProvider } from '../context/AppStateContext';
import ErrorBoundary from '../components/ErrorBoundary';
import LoadingPage from '../components/LoadingPage';
import { ToastContainer } from 'react-toastify';
import Layout from './Layout';
import '../index.css';
import 'react-toastify/dist/ReactToastify.css';
import '../styles/animations.css';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { initClientLogger } from '../utils/clientLogger';
// Auth token is managed inside AuthContext; AuthGuard should rely on verified state only

// Pages that should have the layout (header/navigation)
const pagesWithLayout = ['/chat', '/wallet', '/trading', '/social', '/settings'];

// Pages that don't require authentication
const publicPages = ['/','/login', '/register', '/forgot', '/reset'];

// FIXED: Simplified and stabilized AuthGuard component
function AuthGuard({ children, router }: { children: React.ReactNode, router: any }) {
  const { user, loading, isAuthenticated } = useAuth();
  const isPublicPage = publicPages.includes(router.pathname);
  const [isNavigating, setIsNavigating] = useState(false);
  const lastRedirectAtRef = useRef<number>(0);
  const initialLoadComplete = useRef(false);
  
  // Mark when initial auth load completes; do not implement token-based grace here
  useEffect(() => {
    if (!loading) {
      initialLoadComplete.current = true;
    }
  }, [loading]);
  
  // Simplified redirect logic relying solely on verified auth state
  useEffect(() => {
    if (!initialLoadComplete.current || loading || isNavigating) {
      return;
    }
    
    // If not authenticated and on a protected page, redirect to login
    if (!isAuthenticated && !user && !isPublicPage) {
      const now = Date.now();
      const recentlyRedirected = now - lastRedirectAtRef.current < 2000;
      if (recentlyRedirected) {
        return;
      }
      lastRedirectAtRef.current = now;
      setIsNavigating(true);
      router.replace('/login')
        .then(() => setIsNavigating(false))
        .catch((error) => {
          console.error('Navigation error:', error);
          setIsNavigating(false);
        });
    }
    
    // If authenticated and on a public page, redirect to chat (but not if already on /chat)
    if (isAuthenticated && user && isPublicPage) {
      // Treat GRACE_POST_LOGIN_REDIRECT as a directive to redirect immediately (once)
      let postLoginRedirect = false;
      try {
        postLoginRedirect = sessionStorage.getItem('GRACE_POST_LOGIN_REDIRECT') === '1';
      } catch {}

      // Throttle repeated redirects within a short window
      const now = Date.now();
      const recentlyRedirected = now - lastRedirectAtRef.current < 2000;

      const alreadyOnChat = router.pathname === '/chat';
      if (!alreadyOnChat && (postLoginRedirect || !recentlyRedirected)) {
        lastRedirectAtRef.current = now;
        setIsNavigating(true);
        try { sessionStorage.removeItem('GRACE_POST_LOGIN_REDIRECT'); } catch {}
        router.replace('/chat')
          .then(() => setIsNavigating(false))
          .catch((error) => {
            console.error('Navigation error:', error);
            setIsNavigating(false);
          });
      }
    }
  }, [isAuthenticated, user, isPublicPage, loading, router, isNavigating]);

  // FIXED: Clear any one-time flags when on /chat
  useEffect(() => {
    if (router.pathname === '/chat') {
      // Currently only GRACE_POST_LOGIN_REDIRECT is used as a one-time flag
      try { sessionStorage.removeItem('GRACE_POST_LOGIN_REDIRECT'); } catch {}
    }
  }, [router.pathname]);

  // FIXED: Simplified loading states
  if (loading) {
    return <LoadingPage message="Loading authentication..." />;
  }
  
  // Show navigation state
  if (isNavigating) {
    return <LoadingPage message="Navigating..." />;
  }
  
  // Don't render children until auth check is complete for protected pages
  if (!loading && !user && !isPublicPage) {
    return <LoadingPage message="Redirecting to login..." />;
  }
  
  // Render children with proper layout
  return <>{children}</>;
}

export default function App({ Component, pageProps, router }: AppProps) {
  const shouldHaveLayout = pagesWithLayout.includes(router.pathname);
  const queryClient = useMemo(() => new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 30_000,
        gcTime: 5 * 60_000,
        refetchOnWindowFocus: false,
      },
    },
  }), []);

  // Initialize client logger once if enabled via env
  useEffect(() => {
    try {
      const enabled = process.env.NEXT_PUBLIC_ENABLE_CLIENT_LOGS;
      if (enabled && enabled !== 'false' && enabled !== '0') {
        initClientLogger(router);
      }
    } catch {}
  }, []);

  return (
    <ErrorBoundary componentName="Main App">
      <AuthProvider>
        <AppStateProvider>
          <QueryClientProvider client={queryClient}>
            <AuthGuard router={router}>
              {shouldHaveLayout ? (
                <Layout>
                  <Component {...pageProps} />
                </Layout>
              ) : (
                <Component {...pageProps} />
              )}
              <ToastContainer position="bottom-right" theme="dark" />
            </AuthGuard>
            <ReactQueryDevtools initialIsOpen={false} />
          </QueryClientProvider>
        </AppStateProvider>
      </AuthProvider>
    </ErrorBoundary>
  );
}