// src/pages/Social.tsx

import React, { useEffect, useState } from 'react';
import { useAuth } from '../components/AuthContext';
import { api, API_ENDPOINTS } from '../api/apiClient';

interface SentimentData {
  positive: number;
  negative: number;
  neutral: number;
  overall: string;
  [key: string]: any;
}

interface Topic {
  name: string;
  count: number;
  sentiment: string;
  [key: string]: any;
}

interface InfluentialAccount {
  username: string;
  displayName?: string;
  followers: number;
  influence: number;
  [key: string]: any;
}

interface Tweet {
  id: string;
  text: string;
  username: string;
  timestamp: string;
  likes: number;
  [key: string]: any;
}

export default function Social() {
  const { user } = useAuth();
  const [sentiment, setSentiment] = useState<SentimentData | null>(null);
  const [topics, setTopics] = useState<Topic[]>([]);
  const [accounts, setAccounts] = useState<InfluentialAccount[]>([]);
  const [tweets, setTweets] = useState<Tweet[]>([]);
  const [selectedTopic, setSelectedTopic] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const fetchSocialData = async () => {
      try {
        setIsLoading(true);
        setError('');
        
        // Fetch sentiment data
        const sentimentResponse = await api.get(API_ENDPOINTS.SOCIAL.SENTIMENT);
        if (sentimentResponse.success && sentimentResponse.data) {
          setSentiment(sentimentResponse.data);
        }
        
        // Fetch trending topics
        const topicsResponse = await api.get(API_ENDPOINTS.SOCIAL.TRENDING);
        if (topicsResponse.success && topicsResponse.data) {
          setTopics(topicsResponse.data);
        }
        
        // Fetch influential accounts
        const accountsResponse = await api.get(API_ENDPOINTS.SOCIAL.INFLUENTIAL);
        if (accountsResponse.success && accountsResponse.data) {
          setAccounts(accountsResponse.data);
        }
      } catch (err: any) {
        console.error('Error loading social data:', err);
        setError(err?.message || 'Failed to load social data');
      } finally {
        setIsLoading(false);
      }
    };
    
    if (user) {
      fetchSocialData();
    }
  }, [user]);

  useEffect(() => {
    if (!selectedTopic) return;
    
    const fetchTweets = async () => {
      try {
        setIsLoading(true);
        setError('');
        
        const { data, success } = await api.get(
          `${API_ENDPOINTS.SOCIAL.TWEETS}?topic=${encodeURIComponent(selectedTopic)}`
        );
        
        if (success && data) {
          setTweets(data);
        } else {
          throw new Error(data?.error || 'Failed to load tweets');
        }
      } catch (err: any) {
        console.error('Error loading tweets:', err);
        setError(err?.message || 'Failed to load tweets');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchTweets();
  }, [selectedTopic]);

  return (
    <div className="max-w-3xl mx-auto">
      {isLoading && <p className="text-blue-300 text-sm">Loading...</p>}
      {error && <p className="text-red-500 text-sm">{error}</p>}
      <h1 className="text-2xl font-mono text-red-300">Crypto Social Trends</h1>

        <div className="grid grid-cols-3 gap-4">
          <div className="col-span-1 space-y-4">
            <div className="border border-red-800 rounded p-3">
              <h2 className="text-red-400 text-sm mb-2">Trending Topics</h2>
              {topics.map((t, i) => (
                <button
                  key={i}
                  onClick={() => setSelectedTopic(t.topic)}
                  className="block w-full text-left text-sm hover:text-red-300"
                >
                  #{t.topic} ({t.count})
                </button>
              ))}
            </div>

            <div className="border border-red-800 rounded p-3">
              <h2 className="text-red-400 text-sm mb-2">Influential Accounts</h2>
              {accounts.map((acc, i) => (
                <div key={i} className="text-sm">
                  <p className="text-white font-semibold">{acc.handle}</p>
                  <p className="text-gray-400 text-xs">{acc.followers} followers — topics: {acc.topics?.join(', ')}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="col-span-2 space-y-4">
            <div className="border border-red-800 rounded p-3">
              <h2 className="text-red-400 text-sm mb-2">Market Sentiment</h2>
              {sentiment ? (
                <ul className="text-sm space-y-1">
                  <li>Positive: <span className="text-green-400">{sentiment.positive}%</span></li>
                  <li>Neutral: <span className="text-yellow-300">{sentiment.neutral}%</span></li>
                  <li>Negative: <span className="text-red-400">{sentiment.negative}%</span></li>
                </ul>
              ) : (
                <p className="text-gray-400 text-sm">Loading sentiment...</p>
              )}
            </div>

            <div className="border border-red-800 rounded p-3">
              <h2 className="text-red-400 text-sm mb-2">Tweets about {selectedTopic || '...'}</h2>
              {tweets.map((tw, i) => (
                <div key={i} className="border-b border-red-900 pb-2 mb-2">
                  <p className="text-sm text-white">{tw.text}</p>
                  <p className="text-xs text-gray-400">❤️ {tw.likes} · 🔁 {tw.retweets}</p>
                </div>
              ))}
              {selectedTopic && tweets.length === 0 && (
                <p className="text-sm text-gray-400">No tweets found.</p>
              )}
            </div>
          </div>
        </div>
      </div>
  );
}
