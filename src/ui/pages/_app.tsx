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

// FIXED: Simplified and stabilized AuthGuard component
function AuthGuard({ children, router }: { children: React.ReactNode, router: any }) {
  const { user, loading, isAuthenticated } = useAuth();
  const isPublicPage = publicPages.includes(router.pathname);
  const [isNavigating, setIsNavigating] = useState(false);
  const lastRedirectAtRef = useRef<number>(0);
  const initialLoadComplete = useRef(false);
  const unauthGraceUntilRef = useRef<number>(0);
  
  // FIXED: Extended grace window and better token handling
  useEffect(() => {
    if (!loading) {
      initialLoadComplete.current = true;
      // If a token exists, provide a longer grace window to avoid bouncing to login
      const tokenExists = !!getAuthToken();
      if (tokenExists) {
        unauthGraceUntilRef.current = Date.now() + 5000; // FIXED: Extended to 5s grace
        console.log('AuthGuard: Token exists, setting 5s grace window');
      } else {
        unauthGraceUntilRef.current = 0;
      }
    }
  }, [loading]);
  
  // FIXED: Simplified redirect logic with better grace handling
  useEffect(() => {
    if (!initialLoadComplete.current || loading || isNavigating) {
      return;
    }
    
    // If not authenticated and not on a public page, redirect to login
    if (!isAuthenticated && !user && !isPublicPage) {
      const now = Date.now();
      const withinGrace = now < unauthGraceUntilRef.current;
      const tokenExists = !!getAuthToken();
      
      // FIXED: Never redirect away from chat if a token exists during grace period
      if (router.pathname === '/chat' && (tokenExists || withinGrace)) {
        console.log('AuthGuard: On /chat with token/grace present; suppressing unauth redirect');
        return;
      }
      
      if (withinGrace) {
        console.log('AuthGuard: Skipping unauth redirect (within grace period)');
        return;
      }
      
      // Throttle repeated redirects
      const now2 = Date.now();
      const recentlyRedirected = now2 - lastRedirectAtRef.current < 2000;
      if (recentlyRedirected) {
        console.log('AuthGuard: Skipping redirect (recently redirected)');
        return;
      }
      
      console.log('AuthGuard: Redirecting unauthenticated user to login');
      lastRedirectAtRef.current = now2;
      setIsNavigating(true);
      router.replace('/login')
        .then(() => setIsNavigating(false))
        .catch((error) => {
          console.error('Navigation error:', error);
          setIsNavigating(false);
        });
    }
    
    // FIXED: Simplified authenticated user redirect logic
    if (isAuthenticated && user && isPublicPage) {
      // Check for coordination flags to avoid double redirects
      let skipPublicRedirect = false;
      try {
        skipPublicRedirect = sessionStorage.getItem('GRACE_POST_LOGIN_REDIRECT') === '1';
      } catch {}

      // Throttle repeated redirects within a short window
      const now = Date.now();
      const recentlyRedirected = now - lastRedirectAtRef.current < 2000;

      if (!skipPublicRedirect && !recentlyRedirected) {
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
  }, [isAuthenticated, user, isPublicPage, loading, router, isNavigating]);

  // FIXED: Clear redirect guard when on /chat
  useEffect(() => {
    if (router.pathname === '/chat') {
      try { sessionStorage.removeItem('GRACE_ALREADY_REDIRECTED'); } catch {}
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