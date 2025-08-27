import React, { useEffect, useState, useRef } from 'react';
import { AppProps } from 'next/app';
import { useRouter } from 'next/router';
import { AuthProvider, useAuth } from '../components/AuthContext';
import { AppStateProvider } from '../context/AppStateContext';
import ErrorBoundary from '../components/ErrorBoundary';
import StateLoader from '../components/StateLoader';
import LoadingPage from '../components/LoadingPage';
import { ToastContainer } from 'react-toastify';
import Layout from './Layout';
import '../index.css';
import 'react-toastify/dist/ReactToastify.css';
import '../styles/animations.css';
import { getAuthToken } from '../api/apiClient';

// Pages that should have the layout (header/navigation)
const pagesWithLayout = ['/chat', '/wallet', '/trading', '/social', '/settings'];

// Pages that don't require authentication
const publicPages = ['/login', '/register', '/forgot', '/reset'];

// Auth guard component to protect routes
function AuthGuard({ children, router }: { children: React.ReactNode, router: any }) {
  const { user, loading, isAuthenticated } = useAuth();
  const isPublicPage = publicPages.includes(router.pathname);
  const [isNavigating, setIsNavigating] = useState(false);
  const lastRedirectAtRef = useRef<number>(0);
  const initialLoadComplete = useRef(false);
  const unauthGraceUntilRef = useRef<number>(0);
  
  // Once the initial load is complete, we'll handle redirects
  useEffect(() => {
    if (!loading) {
      initialLoadComplete.current = true;
      // If a token exists, provide a short grace window to avoid bouncing to login
      const tokenExists = !!getAuthToken();
      if (tokenExists) {
        unauthGraceUntilRef.current = Date.now() + 2000; // 2s grace to accommodate remounts
      } else {
        unauthGraceUntilRef.current = 0;
      }
    }
  }, [loading]);
  
  // Handle redirects separately, but only after initial auth check
  useEffect(() => {
    if (!initialLoadComplete.current) return;

    // If still loading auth, don't redirect yet
    if (loading) return;

    // Skip navigation if:
    // 1. Still loading authentication state
    // 2. Already navigating
    // 3. Initial load hasn't completed
    if (loading || isNavigating || !initialLoadComplete.current) {
      return;
    }
    
    // If not authenticated and not on a public page, redirect to login
    if (!isAuthenticated && !user && !isPublicPage) {
      const now = Date.now();
      const withinGrace = now < unauthGraceUntilRef.current;
      const tokenExists = !!getAuthToken();
      // Never redirect away from chat if a token exists; allow auth to settle
      if (router.pathname === '/chat' && tokenExists) {
        console.log('AuthGuard: On /chat with token present; suppressing unauth redirect');
        return;
      }
      if (withinGrace || tokenExists) {
        // Skip redirect during grace or if a token exists; let AuthContext settle
        console.log('AuthGuard: Skipping unauth redirect (grace/token present)', {
          withinGrace,
          tokenExists,
        });
      } else {
        console.log('AuthGuard: Redirecting unauthenticated user to login');
        setIsNavigating(true);
        router.replace('/login')
          .then(() => setIsNavigating(false))
          .catch((error) => {
            console.error('Navigation error:', error);
            setIsNavigating(false);
          });
      }
    }
    
    // If authenticated and on a public page, redirect to chat
    // But only if there isn't an explicit navigation happening from login/register
    // (which is handled by the useEffect in those components)
    if (isAuthenticated && user && isPublicPage) {
      // Coordination flag set by login/register to avoid double redirects
      let skipPublicRedirect = false;
      try {
        skipPublicRedirect = sessionStorage.getItem('GRACE_POST_LOGIN_REDIRECT') === '1';
      } catch {}

      // Throttle repeated redirects within a short window
      const now = Date.now();
      const recentlyRedirected = now - lastRedirectAtRef.current < 1000;

      // Persist a one-time guard to avoid repeated redirects across remounts
      let alreadyRedirected = false;
      try {
        alreadyRedirected = sessionStorage.getItem('GRACE_ALREADY_REDIRECTED') === '1';
      } catch {}

      if (!skipPublicRedirect && !recentlyRedirected && !alreadyRedirected) {
        console.log('AuthGuard: Redirecting authenticated user to chat');
        lastRedirectAtRef.current = now;
        setIsNavigating(true);
        try { sessionStorage.setItem('GRACE_ALREADY_REDIRECTED', '1'); } catch {}
        router.replace('/chat')
          .then(() => setIsNavigating(false))
          .catch((error) => {
            console.error('Navigation error:', error);
            setIsNavigating(false);
          });
      } else {
        // Clear the flag after the first pass to re-enable normal behavior
        try { sessionStorage.removeItem('GRACE_POST_LOGIN_REDIRECT'); } catch {}
      }
    }
  }, [isAuthenticated, user, isPublicPage, loading, router]);

  // Clear the one-time redirect guard when we are on /chat
  useEffect(() => {
    if (router.pathname === '/chat') {
      try { sessionStorage.removeItem('GRACE_ALREADY_REDIRECTED'); } catch {}
    }
  }, [router.pathname]);

  // Show enhanced loading states
  if (loading) {
    return <LoadingPage message="Loading authentication..." />;
  }
  
  // Show navigation state
  if (isNavigating) {
    return <LoadingPage message="Navigating..." />;
  }
  
  // Don't render children until auth check is complete
  if (!loading && !user && !isPublicPage) {
    return <LoadingPage message="Redirecting to login..." />;
  }
  
  // Render children with proper layout
  return <>{children}</>;
}

export default function App({ Component, pageProps, router }: AppProps) {
  const shouldHaveLayout = pagesWithLayout.includes(router.pathname);

  return (
    <ErrorBoundary componentName="Main App">
      <AuthProvider>
        <AppStateProvider>
          <StateLoader>
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
          </StateLoader>
        </AppStateProvider>
      </AuthProvider>
    </ErrorBoundary>
  );
}