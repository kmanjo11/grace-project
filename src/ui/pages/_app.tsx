import React, { useEffect, useState, useRef } from 'react';
import { AppProps } from 'next/app';
import { useRouter } from 'next/router';
import { AuthProvider, useAuth } from '../components/AuthContext';
import { AppStateProvider } from '../context/AppStateContext';
import ErrorBoundary from '../components/ErrorBoundary';
import StateLoader from '../components/StateLoader';
import LoadingPage from '../components/LoadingPage';
import { ToastContainer } from 'react-toastify';
import Layout from './layout';
import '../index.css';
import 'react-toastify/dist/ReactToastify.css';
import '../styles/animations.css';

// Pages that should have the layout (header/navigation)
const pagesWithLayout = ['/chat', '/wallet', '/trading', '/social', '/settings'];

// Pages that don't require authentication
const publicPages = ['/login', '/register', '/forgot', '/reset'];

// Auth guard component to protect routes
function AuthGuard({ children, router }: { children: React.ReactNode, router: any }) {
  const { user, loading, isAuthenticated } = useAuth();
  const isPublicPage = publicPages.includes(router.pathname);
  const [isNavigating, setIsNavigating] = useState(false);
  const initialLoadComplete = useRef(false);
  
  // Once the initial load is complete, we'll handle redirects
  useEffect(() => {
    if (!loading) {
      initialLoadComplete.current = true;
    }
  }, [loading]);
  
  // Handle redirects separately, but only after initial auth check
  useEffect(() => {
    // Skip navigation if:
    // 1. Still loading authentication state
    // 2. Already navigating
    // 3. Initial load hasn't completed
    if (loading || isNavigating || !initialLoadComplete.current) {
      return;
    }
    
    // If not authenticated and not on a public page, redirect to login
    if (!isAuthenticated && !user && !isPublicPage) {
      console.log('AuthGuard: Redirecting unauthenticated user to login');
      setIsNavigating(true);
      router.push('/login')
        .then(() => setIsNavigating(false))
        .catch((error) => {
          console.error('Navigation error:', error);
          setIsNavigating(false);
        });
    }
    
    // If authenticated and on a public page, redirect to chat
    // But only if there isn't an explicit navigation happening from login/register
    // (which is handled by the useEffect in those components)
    if (isAuthenticated && user && isPublicPage) {
      console.log('AuthGuard: Redirecting authenticated user to chat');
      setIsNavigating(true);
      router.push('/chat')
        .then(() => setIsNavigating(false))
        .catch((error) => {
          console.error('Navigation error:', error);
          setIsNavigating(false);
        });
    }
  }, [isAuthenticated, user, loading, isPublicPage, router, isNavigating]);
  
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