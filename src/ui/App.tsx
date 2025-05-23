
import React from 'react';
import { AuthProvider } from './components/AuthContext';
import { AppStateProvider } from './context/AppStateContext';
import AppRouter from './Router';
import ErrorBoundary from './components/ErrorBoundary';
import StateLoader from './components/StateLoader';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import './styles/animations.css';

export default function App() {
  return (
    <ErrorBoundary componentName="Main App">
      <AuthProvider>
        <AppStateProvider>
          <StateLoader>
            <AppRouter />
            <ToastContainer position="bottom-right" theme="dark" />
          </StateLoader>
        </AppStateProvider>
      </AuthProvider>
    </ErrorBoundary>
  );
}