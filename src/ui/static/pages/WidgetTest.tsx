import React, { useState, useEffect } from 'react';
import { useAuth } from '../components/AuthContext';
import LightweightPositionsWidget from '../components/LightweightPositionsWidget';

/**
 * Test page for isolating and debugging the LightweightPositionsWidget
 */
const WidgetTest: React.FC = () => {
  const { user } = useAuth();
  const [isDebugVisible, setIsDebugVisible] = useState(false);

  return (
    <div className="container mx-auto p-6 max-w-5xl">
      <div className="bg-gray-900 p-6 rounded-lg shadow-lg">
        <h1 className="text-2xl font-bold text-white mb-6">Widget Test Page</h1>
        
        {/* Debug status display */}
        <div className="mb-6 p-4 bg-gray-800 rounded-lg">
          <h2 className="text-xl text-white mb-2">Debug Information</h2>
          <p className="text-green-400">User authenticated: {user ? "Yes" : "No"}</p>
          {user && (
            <div className="mt-2">
              <p className="text-gray-300">User ID: {user.id}</p>
              <p className="text-gray-300">Token present: {user.token ? "Yes" : "No"}</p>
            </div>
          )}
          <button 
            className="mt-3 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded"
            onClick={() => setIsDebugVisible(!isDebugVisible)}
          >
            {isDebugVisible ? "Hide Debug Data" : "Show Debug Data"}
          </button>
          
          {isDebugVisible && (
            <div className="mt-3 p-3 bg-gray-700 rounded overflow-auto max-h-48">
              <pre className="text-xs text-green-300 whitespace-pre-wrap">
                {JSON.stringify(user, null, 2)}
              </pre>
            </div>
          )}
        </div>
        
        {/* Widget container with visible border */}
        <div className="border-2 border-red-500 p-4 rounded-lg relative">
          <div className="absolute -top-3 left-3 bg-gray-900 px-2 text-red-500 font-bold">
            LightweightPositionsWidget
          </div>
          
          {/* The actual widget */}
          <div className="mt-2">
            <LightweightPositionsWidget
              initialExpanded={true}
              refreshInterval={10000}
            />
          </div>
        </div>
        
        {/* Console output display */}
        <div className="mt-6 p-4 bg-black rounded-lg">
          <h2 className="text-xl text-white mb-2">Console Output</h2>
          <p className="text-yellow-400 text-sm">Open browser dev tools (F12) to see actual console messages</p>
        </div>
      </div>
    </div>
  );
};

export default WidgetTest;
