import React from 'react';

interface LoadingPageProps {
  message?: string;
  showLogo?: boolean;
}

/**
 * LoadingPage component
 * 
 * Displays a consistent loading animation for transitions between pages
 * or during authentication processes.
 */
export default function LoadingPage({ 
  message = 'Loading...', 
  showLogo = true 
}: LoadingPageProps) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-black text-white p-4">
      <div className="text-center">
        {showLogo && (
          <div className="mb-4 text-red-500 text-xl font-bold">Grace</div>
        )}
        <div className="flex items-center justify-center">
          <span className="mr-2">{message}</span>
          <div className="animate-pulse">...</div>
        </div>
      </div>
    </div>
  );
}
