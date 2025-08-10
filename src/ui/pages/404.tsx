import React, { useEffect } from 'react';
import { useRouter } from 'next/router';

// This is a custom 404 page that also helps with client-side routing
// in static export mode by redirecting to the correct page
export default function Custom404() {
  const router = useRouter();

  useEffect(() => {
    // Get the current path excluding the domain
    const path = window.location.pathname;
    
    // List of known routes in our app
    const knownRoutes = ['/chat', '/login', '/register', '/forgot', '/reset', '/wallet'];
    
    // Clean up the path (remove any trailing slash)
    const cleanPath = path.endsWith('/') ? path.slice(0, -1) : path;
    
    // Check if this is a known route that should be client-side rendered
    const matchedRoute = knownRoutes.find(route => 
      cleanPath === route || cleanPath.startsWith(`${route}/`)
    );
    
    if (matchedRoute) {
      console.log(`404 handler: Redirecting from ${path} to ${matchedRoute}`);
      router.replace(matchedRoute);
    }
  }, [router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-[#140000] to-black text-white">
      <div className="text-center p-8">
        <h1 className="text-4xl font-bold text-red-500 mb-4">Page Not Found</h1>
        <p className="mb-6">The page you're looking for doesn't exist or has been moved.</p>
        <button 
          onClick={() => router.push('/login')}
          className="px-6 py-2 bg-red-700 hover:bg-red-800 rounded-md"
        >
          Return to Login
        </button>
      </div>
    </div>
  );
}
