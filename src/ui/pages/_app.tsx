
import React from 'react';
import { AppProps } from 'next/app'; 
import { AuthProvider } from '../components/AuthContext';
import { AppStateProvider } from '../context/AppStateContext';
import AppRouter from '../Router';
import ErrorBoundary from '../components/ErrorBoundary';
import StateLoader from '../components/StateLoader';
import { ToastContainer } from 'react-toastify';
import Layout from './Layout';
import '../index.css';
import 'react-toastify/dist/ReactToastify.css';
import '../styles/animations.css';


// Pages that should have the layout (header/navigation)
const pagesWithLayout = ['/chat', '/wallet', '/trading', '/social', '/settings'];

export default function App({ Component, pageProps, router }: AppProps) {
  const shouldHaveLayout = pagesWithLayout.includes(router.pathname);

  return (
    <ErrorBoundary componentName="Main App">
      <AuthProvider>
        <AppStateProvider>
          <StateLoader>
            <Component {...pageProps} />
            <ToastContainer position="bottom-right" theme="dark" />
          </StateLoader>
        </AppStateProvider>
      </AuthProvider>
    </ErrorBoundary>
  );
}