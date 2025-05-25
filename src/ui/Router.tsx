// src/ui/Router.tsx

import React from 'react';
import { PageTransition } from './components/PageTransition';
import '../ui/styles/transitions.css';

import { BrowserRouter as Router, Route, Routes, Navigate, useLocation } from 'react-router-dom';
import { useAuth } from './components/AuthContext';
import ErrorBoundary from './components/ErrorBoundary';
import Layout from './pages/Layout';

// Add component error boundary wrapper
const withErrorBoundary = (Component: React.ComponentType<any>, name: string) => {
  return (props: any) => (
    <ErrorBoundary componentName={name}>
      <Component {...props} />
    </ErrorBoundary>
  );
};

import Login from './pages/Login';
import Register from './pages/Register';
import Forgot from './pages/Forgot';
import Reset from './pages/Reset';
import Chat from './pages/Chat';
import Wallet from './pages/Wallet';
import Trading from './pages/Trading';
import Social from './pages/Social';
import Settings from './pages/Settings';
import WidgetTest from './pages/WidgetTest';

function PrivateRoute({ children }: { children: JSX.Element }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="min-h-screen bg-black text-white p-4">Loading...</div>;
  return user ? (
    <Layout>
      <ErrorBoundary componentName="LayoutContent">
        {children}
      </ErrorBoundary>
    </Layout>
  ) : <Navigate to="/login" replace />;
}

// Inner router component that uses location
function AppRoutes() {
  const location = useLocation();
  
  return (
    <PageTransition key={location.pathname}>
      <Routes location={location}>
        {/* Public routes - no Layout needed */}
        <Route path="/login" element={<ErrorBoundary componentName="Login"><Login /></ErrorBoundary>} />
        <Route path="/register" element={<ErrorBoundary componentName="Register"><Register /></ErrorBoundary>} />
        <Route path="/forgot" element={<ErrorBoundary componentName="Forgot"><Forgot /></ErrorBoundary>} />
        <Route path="/reset" element={<ErrorBoundary componentName="Reset"><Reset /></ErrorBoundary>} />

        {/* Protected routes - wrapped with Layout via PrivateRoute */}
        <Route path="/chat" element={<PrivateRoute><ErrorBoundary componentName="Chat"><Chat /></ErrorBoundary></PrivateRoute>} />
        <Route path="/wallet" element={<PrivateRoute><ErrorBoundary componentName="Wallet"><Wallet /></ErrorBoundary></PrivateRoute>} />
        <Route path="/trading" element={<PrivateRoute><ErrorBoundary componentName="Trading"><Trading /></ErrorBoundary></PrivateRoute>} />
        <Route path="/social" element={<PrivateRoute><ErrorBoundary componentName="Social"><Social /></ErrorBoundary></PrivateRoute>} />
        <Route path="/settings" element={<PrivateRoute><ErrorBoundary componentName="Settings"><Settings /></ErrorBoundary></PrivateRoute>} />
        <Route path="/widget-test" element={<PrivateRoute><ErrorBoundary componentName="WidgetTest"><WidgetTest /></ErrorBoundary></PrivateRoute>} />

        <Route path="*" element={<Navigate to="/chat" replace />} />
      </Routes>
    </PageTransition>
  );
}

// Main router component that provides the Router context
export default function AppRouter() {
  return (
    <Router>
      <AppRoutes />
    </Router>
  );
}