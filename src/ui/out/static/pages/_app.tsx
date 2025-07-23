// static/pages/_app.tsx

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { AppProps } from 'next/app';
import { AppStateProvider, useAppState } from '../context/AppStateContext';
import { AuthProvider, useAuth } from '../context/AuthContext';
import '../styles/globals.css';

// Import using relative URL instead of direct import
const logoPath = '/assets/grace_logo_gold.png';

const preventUnintendedRefresh = (e: BeforeUnloadEvent) => {
  e.preventDefault();
  e.returnValue = '';
};

const LogoutButton = () => (
  <button 
    className="transition-all hover:text-red-400 pb-1"
    onClick={() => {
      if (confirm('Are you sure you want to logout?')) {
        window.location.href = '/login';
      }
    }}
  >
    Logout
  </button>
);

function Layout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = router.pathname;
  const { user } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Use the AppState context
  const { dispatch, hydrateFromStorage } = useAppState();
  
  // Capture page state on path change
  useEffect(() => {
    if (user) {
      dispatch({
        type: 'SET_PAGE_STATE',
        payload: { lastVisitedPath: pathname }
      });
    }
  }, [pathname, user, dispatch]);

  // Prevent unintended refresh for unsaved changes
  useEffect(() => {
    window.addEventListener('beforeunload', preventUnintendedRefresh);
    return () => {
      window.removeEventListener('beforeunload', preventUnintendedRefresh);
    };
  }, []);

  // Hydrate state on initial load
  useEffect(() => {
    if (user) {
      hydrateFromStorage(router.push);
    }
  }, [user, router.push, hydrateFromStorage]);

  const navLinks = [
    { name: 'Chat', path: '/chat' },
    { name: 'Wallet', path: '/wallet' },
    { name: 'Trading', path: '/trading' },
    { name: 'Social', path: '/social' },
    { name: 'Settings', path: '/settings' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#140000] to-black text-white flex flex-col items-center">
      <header className="w-full max-w-screen-md text-center border-b border-red-700 pb-1 mb-2">
        <img src={logoPath} alt="Grace Logo" className="w-48 md:w-56 mx-auto mt-2 mb-1" />
        
        {/* Mobile hamburger button */}
        <button 
          className="md:hidden absolute right-4 top-6 text-white p-2" 
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={mobileMenuOpen ? "M6 18L18 6M6 6l12 12" : "M4 6h16M4 12h16M4 18h16"} />
          </svg>
        </button>
        
        {/* Desktop nav bar */}
        <nav className={`
          ${mobileMenuOpen ? 'flex' : 'hidden'} 
          md:flex 
          flex-col md:flex-row 
          justify-center 
          md:space-x-6 md:space-y-0 
          space-y-4 
          text-red-300 text-lg md:text-xl font-mono
          w-full 
          pb-1
        `}>
          {navLinks.map((link) => (
            <Link
              key={link.path}
              href={link.path}
              className={`transition-all hover:text-red-400 pb-1 ${pathname === link.path ? 'text-red-300 border-b border-red-500' : 'text-white'}`}
              onClick={() => setMobileMenuOpen(false)}
            >
              {link.name}
            </Link>
          ))}
          <LogoutButton />
        </nav>
      </header>
      <main className="w-full max-w-screen-md px-4 py-3 flex-grow">
        {children}
      </main>
    </div>
  );
}

export default function App({ Component, pageProps }: AppProps) {
  return (
    <AuthProvider>
      <AppStateProvider>
        <Layout>
          <Component {...pageProps} />
        </Layout>
      </AppStateProvider>
    </AuthProvider>
  );
}
