// src/ui/components/WalletDebugger.tsx
import React, { useState, useEffect } from 'react';
import { useAuth } from './AuthContext';
import { api, API_ENDPOINTS } from '../api/apiClient';

/**
 * Wallet Debugger Component
 * 
 * This component helps debug wallet display issues by directly fetching
 * and displaying wallet data with visibility into each step of the process.
 */
const WalletDebugger: React.FC = () => {
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [walletData, setWalletData] = useState<any>(null);
  const [debugInfo, setDebugInfo] = useState<any>({
    walletApiCalled: false,
    walletApiResponse: null,
    walletApiError: null,
    hasWalletAddress: false,
    walletAddress: null,
    walletDataRaw: null
  });
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Fetch wallet information
  const fetchWalletData = async () => {
    setIsLoading(true);
    try {
      setDebugInfo(prev => ({ ...prev, walletApiCalled: true }));
      
      // Make API call to get wallet info
      const response = await api.get(API_ENDPOINTS.WALLET.INFO, {});
      
      // Log the full response for debugging
      console.log('Wallet API Response:', response);
      
      setDebugInfo(prev => ({ 
        ...prev, 
        walletApiResponse: response,
        walletDataRaw: response.data 
      }));
      
      if (response.success && response.data?.wallet) {
        setWalletData(response.data.wallet);
        
        // Check for wallet address
        const walletAddress = response.data.wallet.address;
        setDebugInfo(prev => ({ 
          ...prev, 
          hasWalletAddress: !!walletAddress,
          walletAddress: walletAddress || 'No address found' 
        }));
      } else {
        setErrorMessage('Wallet data not available or empty response');
        setDebugInfo(prev => ({ 
          ...prev, 
          hasWalletAddress: false,
          walletAddress: 'No address found' 
        }));
      }
    } catch (error) {
      console.error('Error fetching wallet data:', error);
      setErrorMessage(`Failed to fetch wallet data: ${error instanceof Error ? error.message : 'Unknown error'}`);
      setDebugInfo(prev => ({ 
        ...prev, 
        walletApiError: error instanceof Error ? error.message : 'Unknown error'
      }));
    } finally {
      setIsLoading(false);
    }
  };

  // Manual wallet generation
  const generateWallet = async () => {
    setIsLoading(true);
    try {
      const response = await api.post(API_ENDPOINTS.WALLET.GENERATE, {});
      console.log('Wallet Generation Response:', response);
      
      if (response.success) {
        setDebugInfo(prev => ({ 
          ...prev, 
          walletGenerationResponse: response,
          walletGenerationSuccess: true
        }));
        
        // Refresh wallet data after generation
        await fetchWalletData();
      } else {
        setErrorMessage('Failed to generate wallet');
        setDebugInfo(prev => ({ 
          ...prev, 
          walletGenerationResponse: response,
          walletGenerationSuccess: false 
        }));
      }
    } catch (error) {
      console.error('Error generating wallet:', error);
      setErrorMessage(`Failed to generate wallet: ${error instanceof Error ? error.message : 'Unknown error'}`);
      setDebugInfo(prev => ({ 
        ...prev, 
        walletGenerationError: error instanceof Error ? error.message : 'Unknown error'
      }));
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch wallet data on component mount
  useEffect(() => {
    if (user?.id) {
      fetchWalletData();
    }
  }, [user?.id]);

  return (
    <div className="p-4 bg-gray-800 rounded-lg shadow-lg">
      <h2 className="text-xl font-bold text-white mb-4">Wallet Debugger</h2>
      
      {isLoading ? (
        <div className="flex items-center justify-center h-40">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        </div>
      ) : (
        <div>
          {/* Debug Status Section */}
          <div className="mb-4 p-3 bg-gray-900 rounded">
            <h3 className="text-md text-blue-400 font-bold mb-2">Debug Status</h3>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div className="text-gray-400">API Call Made:</div>
              <div className={debugInfo.walletApiCalled ? 'text-green-400' : 'text-red-400'}>
                {debugInfo.walletApiCalled ? 'Yes' : 'No'}
              </div>
              
              <div className="text-gray-400">API Call Success:</div>
              <div className={debugInfo.walletApiResponse?.success ? 'text-green-400' : 'text-red-400'}>
                {debugInfo.walletApiResponse?.success ? 'Yes' : 'No'}
              </div>
              
              <div className="text-gray-400">Has Wallet Address:</div>
              <div className={debugInfo.hasWalletAddress ? 'text-green-400' : 'text-red-400'}>
                {debugInfo.hasWalletAddress ? 'Yes' : 'No'}
              </div>
            </div>
          </div>
          
          {/* Wallet Address Section */}
          <div className="mb-4 p-3 bg-gray-900 rounded">
            <h3 className="text-md text-blue-400 font-bold mb-2">Wallet Address</h3>
            {debugInfo.hasWalletAddress ? (
              <div className="bg-gray-800 p-2 rounded text-green-300 font-mono text-sm break-all">
                {debugInfo.walletAddress}
              </div>
            ) : (
              <div className="bg-red-900/30 p-2 rounded text-red-300 text-sm">
                No wallet address found
                <button
                  onClick={generateWallet}
                  className="mt-2 w-full bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded text-sm"
                  disabled={isLoading}
                >
                  {isLoading ? 'Generating...' : 'Generate Wallet Now'}
                </button>
              </div>
            )}
          </div>
          
          {/* Error Messages */}
          {errorMessage && (
            <div className="mb-4 p-3 bg-red-900/30 rounded">
              <h3 className="text-md text-red-400 font-bold mb-2">Error</h3>
              <div className="text-red-300 text-sm">{errorMessage}</div>
            </div>
          )}
          
          {/* Raw Wallet Data */}
          <div className="mb-4 p-3 bg-gray-900 rounded">
            <h3 className="text-md text-blue-400 font-bold mb-2">Raw Wallet Data</h3>
            <pre className="bg-gray-800 p-2 rounded text-gray-300 text-xs overflow-auto max-h-60">
              {JSON.stringify(walletData, null, 2) || "No data available"}
            </pre>
          </div>
          
          {/* API Response Details */}
          <div className="p-3 bg-gray-900 rounded">
            <h3 className="text-md text-blue-400 font-bold mb-2">API Response</h3>
            <pre className="bg-gray-800 p-2 rounded text-gray-300 text-xs overflow-auto max-h-60">
              {JSON.stringify(debugInfo.walletApiResponse, null, 2) || "No response data"}
            </pre>
          </div>
          
          {/* Refresh Button */}
          <button
            onClick={fetchWalletData}
            className="mt-4 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded text-sm"
            disabled={isLoading}
          >
            {isLoading ? 'Refreshing...' : 'Refresh Wallet Data'}
          </button>
        </div>
      )}
    </div>
  );
};

export default WalletDebugger;
