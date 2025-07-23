import React from 'react';
import Head from 'next/head';
import { useAppState } from '../context/AppStateContext';
import { useAuth } from '../context/AuthContext';
import { useRouter } from 'next/router';

export default function Home() {
  const { state } = useAppState();
  const { user, isAuthenticated, loading } = useAuth();
  const router = useRouter();

  // Redirect to appropriate page based on authentication status
  React.useEffect(() => {
    if (!loading) {
      if (isAuthenticated && user) {
        router.push('/trading'); // Redirect to trading page if logged in
      }
    }
  }, [loading, isAuthenticated, user, router]);

  return (
    <div className="container mx-auto px-4 py-16">
      <Head>
        <title>Grace Project | Welcome</title>
        <meta name="description" content="Grace Project Trading Platform" />
      </Head>

      <div className="text-center">
        <h1 className="text-4xl font-bold text-red-500 mb-8">Grace Project</h1>
        <p className="text-xl mb-8">Advanced Trading Platform</p>
        
        {loading ? (
          <div className="flex justify-center">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-red-500"></div>
          </div>
        ) : isAuthenticated ? (
          <div className="space-y-4">
            <p className="text-lg">Welcome back, {user?.username || 'Trader'}!</p>
            <div className="flex justify-center space-x-4">
              <button 
                onClick={() => router.push('/trading')}
                className="bg-red-600 hover:bg-red-700 text-white px-6 py-2 rounded"
              >
                Go to Trading
              </button>
              <button 
                onClick={() => router.push('/wallet')}
                className="bg-gray-700 hover:bg-gray-800 text-white px-6 py-2 rounded"
              >
                View Wallet
              </button>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <p>Please log in to access the platform</p>
            <div className="flex justify-center space-x-4">
              <button 
                onClick={() => router.push('/login')}
                className="bg-red-600 hover:bg-red-700 text-white px-6 py-2 rounded"
              >
                Login
              </button>
              <button 
                onClick={() => router.push('/register')}
                className="bg-gray-700 hover:bg-gray-800 text-white px-6 py-2 rounded"
              >
                Register
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
