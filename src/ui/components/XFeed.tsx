import React, { useState, useEffect, Fragment } from 'react';
import { PlusIcon, TrashIcon, ArrowPathIcon, Cog6ToothIcon, HeartIcon, ArrowPathRoundedSquareIcon } from '@heroicons/react/24/outline';
import { Dialog, Transition } from '@headlessui/react';
import { useAppState } from '../context/AppStateContext';
import axios from 'axios';

interface Tweet {
  id: string;
  text: string;
  created_at: string;
  username: string;
  name: string;
  profile_image_url?: string;
  media?: {
    type: string;
    url: string;
  }[];
  heat_score?: number;
  likes_count: number;
  retweets_count: number;
}

interface XFeedProps {
  maxItems?: number;
}

const XFeed: React.FC<XFeedProps> = ({ maxItems = 5 }) => {
  const { state, dispatch } = useAppState();
  const [tweets, setTweets] = useState<Tweet[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [openSettings, setOpenSettings] = useState(false);
  const [newHandle, setNewHandle] = useState('');
  
  // Get followed accounts from app state or initialize empty array
  const followedAccounts = state.xfeed?.followedAccounts || [];

  // Load tweets on component mount and when followed accounts change
  useEffect(() => {
    if (followedAccounts.length > 0) {
      fetchTweets();
    }
  }, [followedAccounts]);

  // API response type
  interface ApiResponse {
    success: boolean;
    data: {
      results?: any[];
      query?: string;
      search_type?: string;
      count?: number;
    };
  }

  // Fetch tweets from followed accounts
  const fetchTweets = async () => {
    if (followedAccounts.length === 0) return;
    
    setLoading(true);
    setError(null);
    
    try {
      // Create promises for each account
      const promises = followedAccounts.map(handle => {
        // Format handle for Twitter search according to social_media_service.py
        // For user tweets, we should use 'from:username' format
        const formattedQuery = `from:${handle.replace('@', '')}`;
        
        console.log(`Fetching tweets for ${handle} with query: ${formattedQuery}`);
        
        // Update to match the correct endpoint in social_media_service.py
        return axios.get<ApiResponse>(`/api/social/tweets`, {
          params: {
            query: formattedQuery,
            search_type: 'tweets',
            count: Math.ceil(maxItems / followedAccounts.length),
            include_media: true
          }
        });
      });
      
      // Execute all requests in parallel
      const results = await Promise.all(promises);
      
      // Combine and sort tweets
      let allTweets: Tweet[] = [];
      
      results.forEach((response, index) => {
        const data = response.data.data || {};
        if (data.results && Array.isArray(data.results)) {
          const accountTweets = data.results.map((tweet: any) => ({
            id: tweet.id,
            text: tweet.text,
            created_at: tweet.created_at,
            username: tweet.user?.username || followedAccounts[index],
            name: tweet.user?.name || followedAccounts[index],
            profile_image_url: tweet.user?.profile_image_url,
            media: tweet.media,
            heat_score: calculateHeatScore(tweet),
            likes_count: tweet.likes_count || 0,
            retweets_count: tweet.retweets_count || 0
          }));
          
          allTweets = [...allTweets, ...accountTweets];
        }
      });
      
      // Sort by date (newest first)
      allTweets.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
      
      // Limit to max items
      setTweets(allTweets.slice(0, maxItems));
    } catch (err) {
      console.error('Error fetching tweets:', err);
      setError('Failed to load tweets. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  // Calculate heat score based on likes, retweets, etc.
  const calculateHeatScore = (tweet: any): number => {
    const likesWeight = 1;
    const retweetsWeight = 2;
    const recencyWeight = 3;
    
    const likes = tweet.likes_count || 0;
    const retweets = tweet.retweets_count || 0;
    
    // Calculate recency score (higher for newer tweets)
    const tweetDate = new Date(tweet.created_at);
    const now = new Date();
    const ageInHours = (now.getTime() - tweetDate.getTime()) / (1000 * 60 * 60);
    const recencyScore = ageInHours < 24 ? (24 - ageInHours) / 24 : 0;
    
    // Calculate raw score
    const rawScore = (likes * likesWeight) + (retweets * retweetsWeight) + (recencyScore * 100 * recencyWeight);
    
    // Normalize to 0-100 scale (arbitrary scaling factor of 1000)
    return Math.min(100, Math.round(rawScore / 10));
  };

  // Add a new Twitter handle to follow
  const addHandle = () => {
    if (!newHandle.trim()) return;
    
    // Remove @ if present and clean the handle
    let handle = newHandle.trim();
    if (handle.startsWith('@')) {
      handle = handle.substring(1);
    }
    
    // Further clean the handle - remove any spaces or special characters
    handle = handle.replace(/[^a-zA-Z0-9_]/g, '');
    
    if (!handle) return; // Don't add empty handles
    
    // Check if already in list
    if (followedAccounts.includes(handle)) {
      setNewHandle('');
      return;
    }
    
    // Update state
    const updatedAccounts = [...followedAccounts, handle];
    dispatch({ type: 'UPDATE_XFEED', payload: { followedAccounts: updatedAccounts } });
    setNewHandle('');
    
    // Fetch tweets immediately if this is the first account added
    if (followedAccounts.length === 0) {
      fetchTweets();
    }
  };

  // Remove an account from followed list
  const handleRemoveAccount = (handle: string) => {
    const updatedAccounts = followedAccounts.filter(h => h !== handle);
    
    // Update app state
    dispatch({
      type: 'UPDATE_XFEED',
      payload: {
        followedAccounts: updatedAccounts
      }
    });
  };

  // Format tweet date
  const formatDate = (dateString: string): string => {
    try {
      const date = new Date(dateString);
      const now = new Date();
      const diffMs = now.getTime() - date.getTime();
      const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
      
      if (diffDays === 0) {
        // Today - show hours/minutes ago
        const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
        if (diffHours === 0) {
          const diffMinutes = Math.floor(diffMs / (1000 * 60));
          return `${diffMinutes} min${diffMinutes !== 1 ? 's' : ''} ago`;
        }
        return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
      } else if (diffDays === 1) {
        return 'Yesterday';
      } else if (diffDays < 7) {
        return `${diffDays} days ago`;
      } else {
        return date.toLocaleDateString();
      }
    } catch (e) {
      return dateString;
    }
  };

  return (
    <div className="p-4 h-full flex flex-col overflow-hidden bg-white rounded-md shadow">
      <div className="flex items-center mb-4">
        <h2 className="text-lg font-semibold flex-grow">X Feed</h2>
        <div className="flex space-x-2">
          <button 
            className={`p-1 rounded-full hover:bg-gray-100 transition-colors ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
            onClick={fetchTweets} 
            disabled={loading}
            aria-label="Refresh feed"
          >
            <ArrowPathIcon className="h-5 w-5" />
          </button>
          <button 
            className="p-1 rounded-full hover:bg-gray-100 transition-colors"
            onClick={() => setOpenSettings(true)}
            aria-label="Feed settings"
          >
            <Cog6ToothIcon className="h-5 w-5" />
          </button>
        </div>
      </div>
      
      <div className="overflow-auto flex-1">
        {followedAccounts.length === 0 ? (
          <div className="p-4 text-center">
            <p className="text-base text-gray-600">No accounts followed</p>
            <button 
              className="mt-2 bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded-md text-sm flex items-center mx-auto"
              onClick={() => setOpenSettings(true)}
            >
              <PlusIcon className="h-4 w-4 mr-1" />
              Add Accounts
            </button>
          </div>
        ) : loading ? (
          <div className="flex justify-center p-6">
            <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
          </div>
        ) : error ? (
          <div className="p-4 text-center">
            <p className="text-base text-red-600">{error}</p>
          </div>
        ) : tweets.length === 0 ? (
          <div className="p-4 text-center">
            <p className="text-base text-gray-600">No tweets found</p>
          </div>
        ) : (
          tweets.map(tweet => (
            <div key={tweet.id} className="mb-4 p-3 bg-white rounded-lg border border-gray-200 hover:shadow-md transition-shadow">
              <div className="flex">
                <div className="mr-3">
                  {tweet.profile_image_url ? (
                    <img 
                      src={tweet.profile_image_url} 
                      alt={tweet.name}
                      className="w-10 h-10 rounded-full"
                    />
                  ) : (
                    <div className="w-10 h-10 rounded-full bg-blue-600 text-white flex items-center justify-center font-semibold">
                      {tweet.username.charAt(0).toUpperCase()}
                    </div>
                  )}
                </div>
                <div className="flex-1">
                  <div className="flex items-center">
                    <span className="font-semibold text-sm">
                      {tweet.name}
                    </span>
                    <span className="ml-1 text-xs text-gray-500">
                      @{tweet.username}
                    </span>
                    <span className="ml-auto text-xs text-gray-500">
                      {formatDate(tweet.created_at)}
                    </span>
                  </div>
                  
                  <div className="mt-1 text-sm">
                    {tweet.text}
                  </div>
                  
                  {tweet.media && tweet.media.length > 0 && tweet.media[0].type === 'photo' && (
                    <div className="mt-2">
                      <img
                        src={tweet.media[0].url}
                        alt="Tweet media"
                        className="max-h-[150px] object-contain rounded"
                      />
                    </div>
                  )}
                  
                  <div className="flex mt-2 text-xs text-gray-500 space-x-4">
                    <div className="flex items-center">
                      <HeartIcon className="h-3 w-3 mr-1" />
                      {tweet.likes_count}
                    </div>
                    <div className="flex items-center">
                      <ArrowPathRoundedSquareIcon className="h-3 w-3 mr-1" />
                      {tweet.retweets_count}
                    </div>
                    {tweet.heat_score !== undefined && (
                      <div className={`ml-auto px-1.5 py-0.5 rounded text-white text-xs ${
                        tweet.heat_score > 80 ? 'bg-red-500' : 
                        tweet.heat_score > 50 ? 'bg-yellow-500' : 
                        'bg-blue-500'
                      }`}>
                        {tweet.heat_score}°
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
        
      {/* Settings Dialog */}
      <Transition appear show={openSettings} as={Fragment}>
        <Dialog as="div" className="relative z-10" onClose={() => setOpenSettings(false)}>
          <Transition.Child
            as={Fragment}
            enter="ease-out duration-300"
            enterFrom="opacity-0"
            enterTo="opacity-100"
            leave="ease-in duration-200"
            leaveFrom="opacity-100"
            leaveTo="opacity-0"
          >
            <div className="fixed inset-0 bg-black bg-opacity-25" />
          </Transition.Child>

          <div className="fixed inset-0 overflow-y-auto">
            <div className="flex min-h-full items-center justify-center p-4 text-center">
              <Transition.Child
                as={Fragment}
                enter="ease-out duration-300"
                enterFrom="opacity-0 scale-95"
                enterTo="opacity-100 scale-100"
                leave="ease-in duration-200"
                leaveFrom="opacity-100 scale-100"
                leaveTo="opacity-0 scale-95"
              >
                <Dialog.Panel className="w-full max-w-md transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all">
                  <Dialog.Title
                    as="h3"
                    className="text-lg font-medium leading-6 text-gray-900"
                  >
                    X Feed Settings
                  </Dialog.Title>
                  
                  <div className="mt-4">
                    <h4 className="text-sm font-medium text-gray-700">Add X accounts to follow</h4>
                    
                    <div className="mt-2 flex">
                      <input
                        type="text"
                        className="flex-grow rounded-md border border-gray-300 px-3 py-1.5 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                        placeholder="@username"
                        value={newHandle}
                        onChange={(e) => setNewHandle(e.target.value)}
                      />
                      <button
                        type="button"
                        className={`ml-2 rounded-md bg-blue-600 px-3.5 py-1.5 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600 ${!newHandle.trim() ? 'opacity-50 cursor-not-allowed' : ''}`}
                        onClick={addHandle}
                        disabled={!newHandle.trim()}
                      >
                        Add
                      </button>
                    </div>
                  </div>

                  <div className="mt-4">
                    <div className="border-t border-gray-200 pt-4">
                      <h4 className="text-sm font-medium text-gray-700">Followed Accounts</h4>
                      
                      {followedAccounts.length === 0 ? (
                        <p className="mt-1 text-sm text-gray-500">
                          No accounts added yet
                        </p>
                      ) : (
                        <ul className="mt-2 space-y-2">
                          {followedAccounts.map(handle => (
                            <li key={handle} className="flex items-center justify-between">
                              <span className="text-sm">@{handle}</span>
                              <button
                                type="button"
                                onClick={() => handleRemoveAccount(handle)}
                                className="rounded-full p-1 text-gray-400 hover:text-red-600 hover:bg-red-50"
                              >
                                <TrashIcon className="h-4 w-4" />
                              </button>
                            </li>
                          ))}
                        </ul>
                      )}
                    </div>
                  </div>

                  <div className="mt-6 flex justify-end">
                    <button
                      type="button"
                      className="rounded-md bg-gray-100 px-3.5 py-1.5 text-sm font-semibold text-gray-900 shadow-sm hover:bg-gray-200 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-gray-600"
                      onClick={() => setOpenSettings(false)}
                    >
                      Close
                    </button>
                  </div>
                </Dialog.Panel>
              </Transition.Child>
            </div>
          </div>
        </Dialog>
      </Transition>
    </div>
  );
};

export default XFeed;