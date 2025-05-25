// src/ui/components/PositionsWidgetDebugger.tsx
import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from './AuthContext';
import { api, API_ENDPOINTS } from '../api/apiClient';
import LightweightPositionsWidget from './LightweightPositionsWidget';

/**
 * Positions Widget Debugger
 * 
 * This component wraps the LightweightPositionsWidget with debugging capabilities
 * to help diagnose rendering issues specifically with the positions widget.
 */
const PositionsWidgetDebugger: React.FC = () => {
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [apiStatus, setApiStatus] = useState<{
    positionsApiCalled: boolean;
    positionsApiSuccess: boolean;
    positionsData: any;
    errorMessage: string | null;
  }>({
    positionsApiCalled: false,
    positionsApiSuccess: false,
    positionsData: null,
    errorMessage: null
  });

  // Directly fetch positions data to verify API is working
  const fetchPositionsData = useCallback(async () => {
    if (!user?.id) return;
    
    setIsLoading(true);
    try {
      setApiStatus(prev => ({ ...prev, positionsApiCalled: true }));
      
      // Try first with leverage positions endpoint
      const leverageResponse = await api.get(API_ENDPOINTS.USER.LEVERAGE_POSITIONS, {});
      console.log('Leverage positions API response:', leverageResponse);
      
      // Then try spot positions
      const spotResponse = await api.get(API_ENDPOINTS.USER.SPOT_POSITIONS, {});
      console.log('Spot positions API response:', spotResponse);
      
      // Combine the responses
      const combined = {
        leverage: leverageResponse?.data?.positions || [],
        spot: spotResponse?.data?.positions || [],
        success: leverageResponse.success || spotResponse.success
      };
      
      setApiStatus({
        positionsApiCalled: true,
        positionsApiSuccess: combined.success,
        positionsData: combined,
        errorMessage: (!combined.success) 
          ? 'Failed to fetch positions data' 
          : null
      });
      
    } catch (error) {
      console.error('Error fetching positions data:', error);
      setApiStatus({
        positionsApiCalled: true,
        positionsApiSuccess: false,
        positionsData: null,
        errorMessage: error instanceof Error ? error.message : 'Unknown error'
      });
    } finally {
      setIsLoading(false);
    }
  }, [user?.id]);

  // Fetch data on component mount
  useEffect(() => {
    fetchPositionsData();
  }, [fetchPositionsData]);

  return (
    <div className="positions-debugger">
      {/* Debug Status Panel */}
      <div className="mb-4 p-4 bg-gray-900 border border-gray-700 rounded-md">
        <h3 className="text-md text-purple-400 font-bold mb-2">Positions Widget Debug Status</h3>
        
        <div className="grid grid-cols-2 gap-2 text-sm mb-4">
          <div className="text-gray-400">User Authenticated:</div>
          <div className={user?.id ? 'text-green-400' : 'text-red-400'}>
            {user?.id ? 'Yes' : 'No'}
          </div>
          
          <div className="text-gray-400">Positions API Called:</div>
          <div className={apiStatus.positionsApiCalled ? 'text-green-400' : 'text-red-400'}>
            {apiStatus.positionsApiCalled ? 'Yes' : 'No'}
          </div>
          
          <div className="text-gray-400">Positions API Success:</div>
          <div className={apiStatus.positionsApiSuccess ? 'text-green-400' : 'text-red-400'}>
            {apiStatus.positionsApiSuccess ? 'Yes' : 'No'}
          </div>
          
          <div className="text-gray-400">Leverage Positions Count:</div>
          <div className="text-blue-400">
            {apiStatus.positionsData?.leverage?.length || 0}
          </div>
          
          <div className="text-gray-400">Spot Positions Count:</div>
          <div className="text-blue-400">
            {apiStatus.positionsData?.spot?.length || 0}
          </div>
        </div>
        
        {apiStatus.errorMessage && (
          <div className="mb-4 p-3 bg-red-900/30 rounded">
            <h3 className="text-sm text-red-400 font-bold mb-1">Error Message:</h3>
            <div className="text-red-300 text-sm">{apiStatus.errorMessage}</div>
          </div>
        )}
        
        <div className="flex space-x-2">
          <button
            onClick={fetchPositionsData}
            className="bg-purple-600 hover:bg-purple-700 text-white px-3 py-1 rounded text-sm"
            disabled={isLoading}
          >
            {isLoading ? 'Loading...' : 'Refresh Positions Data'}
          </button>
        </div>
      </div>
      
      {/* The Actual LightweightPositionsWidget with Custom Styling */}
      <div className="relative border-2 border-dashed border-purple-500 p-4 rounded-md bg-opacity-10 bg-purple-900">
        <div className="absolute -top-3 left-4 bg-gray-900 px-2 text-purple-400 text-xs font-bold">
          LightweightPositionsWidget Component
        </div>
        
        <LightweightPositionsWidget 
          initialExpanded={true}
          refreshInterval={60000} 
        />
        
        {/* Overlay for empty data state */}
        {(apiStatus.positionsApiSuccess && 
          apiStatus.positionsData?.leverage?.length === 0 && 
          apiStatus.positionsData?.spot?.length === 0) && (
          <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-70 rounded-md">
            <div className="text-center p-4">
              <span className="text-yellow-400 text-sm font-bold">No Positions Found</span>
              <p className="text-gray-300 text-xs mt-1">
                The API returned successfully but no positions were found.
                <br />This explains why the widget appears empty.
              </p>
            </div>
          </div>
        )}
      </div>
      
      {/* Raw Data Panel */}
      <div className="mt-4 p-4 bg-gray-900 border border-gray-700 rounded-md">
        <h3 className="text-md text-purple-400 font-bold mb-2">Raw Positions Data</h3>
        <div className="bg-black bg-opacity-50 p-3 rounded-md">
          <pre className="text-xs text-gray-300 overflow-auto max-h-60">
            {JSON.stringify(apiStatus.positionsData, null, 2) || "No data available"}
          </pre>
        </div>
      </div>
    </div>
  );
};

export default PositionsWidgetDebugger;
