// src/pages/Wallet.tsx

import React, { useEffect, useState, FormEvent, useRef } from 'react';
import { useAuth } from '../components/AuthContext';
import { api, API_ENDPOINTS } from '../api/apiClient';
import { useRouter } from 'next/router';
import LightweightPositionsWidget from '../components/LightweightPositionsWidget';
import WalletDebugger from '../components/WalletDebugger';
import PositionsWidgetDebugger from '../components/PositionsWidgetDebugger';

// Crypto wallet address converter - compatible with existing setup
const COOL_PREFIXES = [
  '🚀', '💎', '🌟', '⚡', '🔥', '🤖', 
  'MOON', 'DEGEN', 'CHAD', 'BASED', 'ALPHA'
];

/**
 * Converts any wallet address format to a readable, crypto-friendly format
 * Compatible with binary addresses and escaped hex formats
 */
function convertToReadableAddress(address: string): string {
  if (!address) return 'No Address';
  
  try {
    // Handle null or undefined
    if (address === null || address === undefined) {
      return 'No Address';
    }
    
    // Clean up escaped hex characters if present (\x format)
    let cleanAddress = String(address);
    
    // Check for escaped hex pattern
    if (cleanAddress.includes('\\x')) {
      try {
        // First approach: convert escaped hex to proper characters
        // This handles formats like: E$\x1f\xdc\xcb\xde\xdb\xf9\x1d...
        const hexPattern = /\\x([0-9a-fA-F]{2})/g;
        let match;
        let hexString = '';
        
        // Extract all hex values and convert to a clean hex string
        while ((match = hexPattern.exec(cleanAddress)) !== null) {
          hexString += match[1];
        }
        
        // If we found hex values, use them
        if (hexString.length > 0) {
          cleanAddress = hexString;
        } else {
          // Fallback: just remove the \x parts
          cleanAddress = cleanAddress.replace(/\\x/g, '');
        }
      } catch (err) {
        // Fallback: just remove the \x parts
        cleanAddress = cleanAddress.replace(/\\x/g, '');
      }
    }
    
    // If it contains non-alphanumeric characters, convert to hex
    if (!/^[0-9a-zA-Z]+$/.test(cleanAddress)) {
      try {
        // Convert each character to its hex representation
        const hexAddress = Array.from(cleanAddress)
          .map(c => {
            try {
              return c.charCodeAt(0).toString(16).padStart(2, '0');
            } catch {
              return '00'; // Fallback for any character issues
            }
          })
          .join('');
        cleanAddress = hexAddress;
      } catch (err) {
        // If conversion fails, use a simplified approach
        cleanAddress = cleanAddress.replace(/[^a-zA-Z0-9]/g, '');
      }
    }
    
    // Get a random cool prefix
    const prefixIndex = Math.floor(Math.random() * COOL_PREFIXES.length);
    const prefix = COOL_PREFIXES[prefixIndex] || 'DEGEN'; // Fallback prefix
    
    // Format for crypto wallet compatibility
    // Ensure it's a valid-looking crypto address (hexadecimal format)
    let cryptoAddress = cleanAddress || 'invalid_wallet_address';
    
    // Make sure it's a proper hex string (for crypto wallets)
    if (!/^[0-9a-fA-F]+$/.test(cryptoAddress)) {
      // If not hex, convert to hex
      try {
        cryptoAddress = Array.from(cryptoAddress)
          .map(c => c.charCodeAt(0).toString(16).padStart(2, '0'))
          .join('');
      } catch (err) {
        // If conversion fails, use a fallback
        cryptoAddress = 'deadbeef' + Date.now().toString(16);
      }
    }
    
    // Return the full crypto address with styling
    return `${prefix} ${cryptoAddress} 💰`;
  } catch (e) {
    console.error('Error converting address:', e);
    // Always return something useful even if everything fails
    return 'DEGEN wallet 💰';
  }
}

interface WalletBalance {
  token: string;
  amount: number;
}

interface WalletData {
  address?: string;
  balances?: WalletBalance[];
  [key: string]: any;
}

interface TransactionResult {
  success?: boolean;
  message?: string;
  tx_hash?: string;
  [key: string]: any;
}

export default function Wallet() {
  const { user } = useAuth();
  const [connectionSession, setConnectionSession] = useState<string | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<'idle' | 'connecting' | 'timeout' | 'error'>('idle');
  const [walletData, setWalletData] = useState<WalletData | null>(null);
  const [error, setError] = useState<string>('');
  const [recipient, setRecipient] = useState<string>('');
  const [amount, setAmount] = useState<string>('');
  const [tokenType, setTokenType] = useState<string>('sol');
  const [txResult, setTxResult] = useState<string>('');
  const phantomWindowRef = useRef<Window | null>(null);
  const connectionTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const token = localStorage.getItem('token');
  const router = useRouter();

  // Function to validate a Phantom session with the backend
  const validatePhantomSession = async (sessionId: string): Promise<boolean> => {
    try {
      const { data, success } = await api.post(API_ENDPOINTS.WALLET.COMPLETE_PHANTOM, {
        session_id: sessionId,
        validate_only: true
      });
      
      if (success && data.valid) {
        // Session is valid
        return true;
      } else {
        // Session is invalid, clear it
        setConnectionSession(null);
        localStorage.removeItem('phantom_session');
        return false;
      }
    } catch (err) {
      console.error('Failed to validate Phantom session:', err);
      // On error, assume session is invalid
      setConnectionSession(null);
      localStorage.removeItem('phantom_session');
      return false;
    }
  };

  // Check localStorage for existing session on component mount and validate it
  useEffect(() => {
    const savedSession = localStorage.getItem('phantom_session');
    if (savedSession && user) {
      try {
        const sessionData = JSON.parse(savedSession);
        // Check if session is still valid (not expired)
        const expiryTime = new Date(sessionData.expiresAt).getTime();
        if (expiryTime > Date.now()) {
          // Session still valid, can be reused
          setConnectionSession(sessionData.sessionId);
          
          // Validate the session with the backend
          const validateSession = async () => {
            const isValid = await validatePhantomSession(sessionData.sessionId);
            // If valid, we don't need to do anything else - wallet data will be loaded
            // If invalid, the validatePhantomSession function will clear the session
          };
          
          validateSession();
        } else {
          // Session expired, remove from localStorage
          localStorage.removeItem('phantom_session');
        }
      } catch (e) {
        // Invalid session data, remove it
        localStorage.removeItem('phantom_session');
      }
    }
  }, [user]);

  // Cleanup function to clear any timeouts when component unmounts
  useEffect(() => {
    return () => {
      if (connectionTimeoutRef.current) {
        clearTimeout(connectionTimeoutRef.current);
      }
      
      // Close phantom window if it's still open
      if (phantomWindowRef.current && !phantomWindowRef.current.closed) {
        phantomWindowRef.current.close();
      }
    };
  }, []);

// Update fetchWalletData to also get Mango balance
const fetchWalletData = async () => {
  try {
    setError('');
    // Get wallet data
    const { data, success } = await api.get(API_ENDPOINTS.WALLET.DATA);
    
    if (success && data) {
      // Also get Mango balance
      try {
        const mangoResponse = await api.get(API_ENDPOINTS.WALLET.MANGO_BALANCE);
        if (mangoResponse.success) {
          // Add Mango balance to wallet data
          data.mango_balance = {
            total_value: calculateTotalValue(mangoResponse.data.balances),
            balances: mangoResponse.data.balances
          };
        }
      } catch (mangoErr) {
        console.error('Error fetching Mango balance:', mangoErr);
        data.mango_balance = { total_value: 0, balances: {} };
      }
      
      setWalletData(data);
    } else {
      throw new Error('Failed to load wallet data');
    }
  } catch (err: any) {
    console.error('Wallet data fetch error:', err);
    setError(err?.message || 'Failed to load wallet info');
  }
};

// Helper function to calculate total value from Mango balances
const calculateTotalValue = (balances) => {
  if (!balances) return 0;
  
  let total = 0;
  // Handle different possible structures in the API response
  Object.values(balances).forEach((token: any) => {
    if (typeof token === 'object') {
      // Try different possible property names for the USD value
      const value = token.value_usd || token.notionalValue || token.usd_value || 
                    (token.amount && token.price ? token.amount * token.price : 0);
      total += Number(value) || 0;
    }
  });
  
  return total;
};
  // Load wallet data when user is authenticated
  useEffect(() => {
    if (user) {
      fetchWalletData();
    }
  }, [user]);

  // Get query params from Next.js router
  
  // Check if we're returning from Phantom authorization
  useEffect(() => {
    const { phantom_address: phantomWalletAddress, session_id: sessionId } = router.query;
    
    if (phantomWalletAddress && sessionId && typeof phantomWalletAddress === 'string' && typeof sessionId === 'string') {
      completePhantomConnection(sessionId, phantomWalletAddress);
      // Clean up URL params after processing
      router.replace('/wallet');
    }
  }, [router.query]);

  // Function to initiate Phantom wallet connection
  const connectPhantom = async () => {
    try {
      setError('');
      setConnectionStatus('connecting');
      
      // Check if we have a cached session that's still valid
      const savedSession = localStorage.getItem('phantom_session');
      if (savedSession) {
        try {
          const sessionData = JSON.parse(savedSession);
          // Check if session is still valid (not expired)
          const expiryTime = new Date(sessionData.expiresAt).getTime();
          if (expiryTime > Date.now()) {
            // Reuse the existing session
            setConnectionSession(sessionData.sessionId);
            // Validate the session with the backend
            const isValid = await validatePhantomSession(sessionData.sessionId);
            if (isValid) {
              // Session is valid, fetch wallet data to update UI
              await fetchWalletData();
              setConnectionStatus('idle');
              return;
            }
          }
          // Session expired or invalid, remove it and continue with new session
          localStorage.removeItem('phantom_session');
        } catch (e) {
          // Invalid session data, remove it
          localStorage.removeItem('phantom_session');
        }
      }
      
      // Prepare redirect URL (back to this page)
      const redirectUrl = `${window.location.origin}/wallet`;
      
      const { data, success } = await api.post(API_ENDPOINTS.WALLET.CONNECT_PHANTOM, {
        redirect_url: redirectUrl
      });
      
      if (success && data.connection) {
        // Store session ID for later completion
        const sessionId = data.connection.session_id;
        setConnectionSession(sessionId);
        
        // Save session to localStorage with expiry time (30 minutes from now)
        const expiryTime = new Date(Date.now() + 30 * 60 * 1000);
        localStorage.setItem('phantom_session', JSON.stringify({
          sessionId,
          expiresAt: expiryTime.toISOString()
        }));
        
        // URL to redirect user for Phantom authorization
        const authorizeUrl = data.connection.authorize_url;
        
        // Open Phantom wallet in a popup window
        const width = 450;
        const height = 600;
        const left = window.innerWidth / 2 - width / 2;
        const top = window.innerHeight / 2 - height / 2;
        
        phantomWindowRef.current = window.open(
          authorizeUrl,
          'Connect Phantom Wallet',
          `width=${width},height=${height},left=${left},top=${top}`
        );
        
        // Set up message listener for popup communication
        const messageHandler = (event: MessageEvent) => {
          if (event.data?.type === 'phantom_connection' && event.data?.wallet_address) {
            completePhantomConnection(sessionId, event.data.wallet_address);
            window.removeEventListener('message', messageHandler);
            // Clear timeout if connection succeeds
            if (connectionTimeoutRef.current) {
              clearTimeout(connectionTimeoutRef.current);
              connectionTimeoutRef.current = null;
            }
          }
        };
        
        window.addEventListener('message', messageHandler);
        
        // Set a timeout to handle case where popup is closed or authorization fails
        connectionTimeoutRef.current = setTimeout(() => {
          setConnectionStatus('timeout');
          window.removeEventListener('message', messageHandler);
          
          // Check if the popup was closed
          if (phantomWindowRef.current && phantomWindowRef.current.closed) {
            console.log('Phantom connection window was closed by user');
          }
          
          // Don't clear the session ID here - user might want to retry with same session
        }, 45000); // 45 second timeout
      } else {
        setConnectionStatus('error');
        throw new Error(data?.error || 'Connection failed');
      }
    } catch (err: any) {
      console.error('Phantom connect error:', err);
      setConnectionStatus('error');
      setError(err?.message || 'Connection failed');
    }
  };

  // Function to disconnect Phantom wallet
  const disconnectPhantom = async () => {
    try {
      setError('');
      
      // Call backend to disconnect the wallet
      const { data, success } = await api.post(API_ENDPOINTS.WALLET.DISCONNECT_PHANTOM, {});
      
      if (success) {
        // Clear local session data
        localStorage.removeItem('phantom_session');
        setConnectionSession(null);
        
        // Refresh wallet data to update UI
        await fetchWalletData();
      } else {
        throw new Error(data?.error || 'Failed to disconnect wallet');
      }
    } catch (err: any) {
      console.error('Phantom disconnect error:', err);
      setError(err?.message || 'Failed to disconnect wallet');
    }
  };

  // Function to complete Phantom wallet connection
  const completePhantomConnection = async (sessionId: string, walletAddress: string) => {
    try {
      setError('');
      setConnectionStatus('idle');
      
      // Use the standardized API_ENDPOINTS constant for consistency
      const { data, success } = await api.post(API_ENDPOINTS.WALLET.COMPLETE_PHANTOM, {
        session_id: sessionId,
        wallet_address: walletAddress
      });
      
      if (success) {
        // Close the phantom window if it's still open
        if (phantomWindowRef.current && !phantomWindowRef.current.closed) {
          phantomWindowRef.current.close();
        }
        
        // Refresh wallet data to show new phantom wallet
        await fetchWalletData();
        
        // Keep the session in localStorage for reuse
        // The session is already stored with an expiry time
      } else {
        throw new Error(data?.error || 'Failed to complete Phantom wallet connection');
      }
    } catch (err: any) {
      console.error('Phantom connection completion error:', err);
      setConnectionStatus('error');
      setError(err?.message || 'Failed to complete wallet connection');
    }
  };

  const sendTransaction = async () => {
    if (!recipient || !amount) {
      setError('Recipient and amount are required');
      return;
    }
    
    try {
      setError('');
      setTxResult('');
      
      // Use standardized API client
      const { data, success } = await api.post(API_ENDPOINTS.WALLET.SEND, {
        recipient_address: recipient,
        amount,
        token: tokenType,
        wallet_type: 'internal',
      });
      
      if (success) {
        setTxResult(data?.message || data?.tx_hash || 'Transaction submitted');
        // Refresh wallet data after successful transaction
        const walletResponse = await api.get(API_ENDPOINTS.WALLET.DATA);
        if (walletResponse.success) {
          setWalletData(walletResponse.data);
        }
      } else {
        throw new Error(data?.error || 'Transaction failed');
      }
    } catch (err: any) {
      console.error('Send transaction error:', err);
      setError(err?.message || 'Failed to send transaction');
      setTxResult('Failed to send transaction');
    }
  };

  return (
    <div className="space-y-4">
        <h1 className="text-2xl font-mono text-red-300">Wallet Dashboard</h1>
        {error && <p className="text-red-500">{error}</p>}
        {walletData ? (
          <div className="grid grid-cols-2 gap-4">
            <div className="border border-red-800 rounded p-4">
              <h2 className="text-red-400 mb-2">Internal Wallet</h2>
              <p className="text-sm break-all">Address: <span className="text-white">{walletData.internal_wallet?.address}</span></p>
              <p className="text-sm">
                <span className="text-purple-400">◎ SOL</span>: {walletData.internal_wallet?.balances?.sol || '0.00'}
              </p>
              <p className="text-sm">
                <span className="text-green-400">$ USDC</span>: {walletData.internal_wallet?.balances?.usdc || '0.00'}
              </p>
              <p className="text-sm">
                <span className="text-orange-400">🥭 Mango Balance</span>: ${typeof walletData.mango_balance?.total_value === 'number' ? walletData.mango_balance.total_value.toFixed(2) : '0.00'}
              </p>
              
              {/* Crypto Bro Address Converter for Internal Wallet */}
              <div className="mt-2 p-2 bg-gradient-to-r from-blue-900/30 to-indigo-900/30 rounded-lg border border-blue-700">
                <p className="text-xs text-blue-400 font-mono break-all">
                  {convertToReadableAddress(walletData.internal_wallet?.address)}
                </p>
              </div>
              <p className="text-yellow-400 text-xs mt-2">
                ^^This is your internal wallet address. Verify it with Grace. Copy to use for deposits, trading, or transfers.
              </p>

              <div className="mt-4 space-y-2">
                <h3 className="text-sm text-red-400">Send from Internal Wallet</h3>
                <input
                  className="w-full p-2 bg-white/10 text-white rounded"
                  placeholder="Recipient Address"
                  value={recipient}
                  onChange={(e) => setRecipient(e.target.value)}
                />
                <input
                  className="w-full p-2 bg-white/10 text-white rounded"
                  placeholder="Amount"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                />
                <select
                  className="w-full p-2 bg-white/10 text-white rounded"
                  value={tokenType}
                  onChange={(e) => setTokenType(e.target.value)}
                >
                  <option value="sol">SOL</option>
                  <option value="usdc">USDC</option>
                </select>
                <button
                  onClick={sendTransaction}
                  className="w-full rounded bg-red-700 px-4 py-2 text-sm hover:bg-red-900"
                >
                  Send
                </button>
                {txResult && <p className="text-sm text-green-400">{txResult}</p>}
              </div>
            </div>

            <div className="border border-red-800 rounded p-4">
              <h2 className="text-red-400 mb-2">Phantom Wallet</h2>
              {walletData.phantom_wallet?.address ? (
                <>
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="text-sm break-all">Address: <span className="text-white">{walletData.phantom_wallet?.address}</span></p>
                      <p className="text-sm">
                        <span className="text-purple-400">◎ SOL</span>: {walletData.phantom_wallet?.balances?.sol || '0.00'}
                      </p>
                      <p className="text-sm">
                        <span className="text-green-400">$ USDC</span>: {walletData.phantom_wallet?.balances?.usdc || '0.00'}
                      </p>
                    </div>
                    <button
                      onClick={disconnectPhantom}
                      className="bg-red-900 hover:bg-red-800 text-xs px-2 py-1 rounded"
                    >
                      Disconnect
                    </button>
                  </div>
                  
                  {/* Crypto Bro Address Converter */}
                  <div className="mt-4 p-3 bg-gradient-to-r from-purple-900/30 to-pink-900/30 rounded-lg border border-purple-700">
                    <h3 className="text-pink-400 text-sm font-bold mb-2">🔥 CRYPTO BRO ADDRESS 🔥</h3>
                    <div className="bg-black/50 p-2 rounded">
                      <p className="text-sm font-mono text-green-400 break-all">
                        {convertToReadableAddress(walletData.phantom_wallet?.address)}
                      </p>
                    </div>
                    <p className="text-xs text-gray-400 mt-1 text-center">Full address for crypto operations</p>
                  </div>
                </>
              ) : (
                <div>
                  <button
                    onClick={connectPhantom}
                    className="mt-2 rounded bg-red-700 px-4 py-2 text-sm hover:bg-red-900"
                    disabled={connectionStatus === 'connecting'}
                  >
                    {connectionStatus === 'connecting' ? 'Connecting...' : 'Connect Phantom'}
                  </button>
                  
                  {connectionStatus === 'connecting' && (
                    <p className="text-xs text-yellow-300 mt-1">
                      Waiting for Phantom authorization. Please complete the process in the popup window.
                    </p>
                  )}
                  
                  {connectionStatus === 'timeout' && (
                    <div className="mt-2">
                      <p className="text-xs text-orange-400 mb-1">
                        Connection timed out. Did you close the popup window?
                      </p>
                      <button 
                        onClick={connectPhantom}
                        className="text-xs bg-orange-900 hover:bg-orange-800 px-2 py-1 rounded"
                      >
                        Retry Connection
                      </button>
                    </div>
                  )}
                  
                  {connectionStatus === 'error' && (
                    <div className="mt-2">
                      <p className="text-xs text-red-400 mb-1">
                        Connection failed. Please try again.
                      </p>
                      <button 
                        onClick={connectPhantom}
                        className="text-xs bg-red-900 hover:bg-red-800 px-2 py-1 rounded"
                      >
                        Retry Connection
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        ) : (
          <p className="text-gray-400">Loading wallet info...</p>
        )}
        
        {/* Lightweight Positions Widget */}
        <div className="mt-6 border border-red-800 rounded p-4">
          <h2 className="text-xl font-mono text-red-300 mb-4">Your Trading Positions</h2>
          <LightweightPositionsWidget 
            initialExpanded={true}
            refreshInterval={60000} 
          />
        </div>
        
        {/* Wallet Debugger - For diagnosing wallet display issues */}
        <div className="mt-6 border border-blue-800 rounded p-4">
          <h2 className="text-xl font-mono text-blue-300 mb-4">Wallet Debugger</h2>
          <WalletDebugger />
        </div>
      </div>
  );
}
