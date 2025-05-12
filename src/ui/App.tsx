
import React from 'react';
import { AuthProvider } from './components/AuthContext';
import AppRouter from './Router';
import ErrorBoundary from './components/ErrorBoundary';

export default function App() {
  return (
    <ErrorBoundary componentName="Main App">
      <AuthProvider>
        <AppRouter />
      </AuthProvider>
    </ErrorBoundary>
  );
}