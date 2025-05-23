import React, { useState, useEffect } from 'react';
import { Box, Typography, Avatar, Card, CardContent, CardMedia, CardHeader, IconButton, CircularProgress, Divider, Chip, TextField, Button, Dialog, DialogTitle, DialogContent, DialogActions, List, ListItem, Paper } from '@mui/material';
import { Add as AddIcon, Delete as DeleteIcon, Refresh as RefreshIcon, Settings as SettingsIcon } from '@mui/icons-material';
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
      const promises = followedAccounts.map(handle => 
        axios.get<ApiResponse>(`/api/social-media/tweets`, {
          params: {
            query: handle,
            search_type: 'tweets',
            count: Math.ceil(maxItems / followedAccounts.length)
          }
        })
      );
      
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

  // Add a new account to follow
  const handleAddAccount = () => {
    if (!newHandle) return;
    
    // Clean handle (remove @ if present)
    const cleanHandle = newHandle.trim().replace(/^@/, '');
    
    if (cleanHandle && !followedAccounts.includes(cleanHandle)) {
      const updatedAccounts = [...followedAccounts, cleanHandle];
      
      // Update app state
      dispatch({
        type: 'UPDATE_XFEED',
        payload: {
          followedAccounts: updatedAccounts
        }
      });
      
      setNewHandle('');
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
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  return (
    <Paper elevation={1} sx={{ width: '100%', p: 1, borderRadius: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
        <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>X Feed</Typography>
        <Box>
          <IconButton onClick={fetchTweets} disabled={loading} size="small">
            <RefreshIcon fontSize="small" />
          </IconButton>
          <IconButton onClick={() => setOpenSettings(true)} size="small">
            <SettingsIcon fontSize="small" />
          </IconButton>
        </Box>
      </Box>
      
      {followedAccounts.length === 0 ? (
        <Box sx={{ mb: 1, p: 2, textAlign: 'center', bgcolor: 'background.paper', borderRadius: 1 }}>
          <Typography variant="body2" sx={{ mb: 1 }}>No accounts added</Typography>
          <Button 
            variant="outlined" 
            size="small"
            startIcon={<AddIcon />}
            onClick={() => setOpenSettings(true)}
          >
            Add Accounts
          </Button>
        </Box>
      ) : loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 2 }}>
          <CircularProgress size={24} />
        </Box>
      ) : error ? (
        <Box sx={{ mb: 1, p: 1, bgcolor: 'error.main', color: 'white', borderRadius: 1 }}>
          <Typography variant="caption">{error}</Typography>
        </Box>
      ) : tweets.length === 0 ? (
        <Box sx={{ mb: 1, p: 1, textAlign: 'center', borderRadius: 1 }}>
          <Typography variant="caption">No tweets found</Typography>
        </Box>
      ) : (
        tweets.map(tweet => (
          <Card key={tweet.id} sx={{ mb: 1, boxShadow: 'none', border: '1px solid', borderColor: 'divider' }}>
            <CardHeader
              sx={{ p: 1 }}
              avatar={
                <Avatar 
                  src={tweet.profile_image_url} 
                  alt={tweet.name}
                  sx={{ width: 24, height: 24 }}
                >
                  {tweet.name.charAt(0)}
                </Avatar>
              }
              title={
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Typography variant="caption" sx={{ fontWeight: 'bold', mr: 0.5 }}>
                    {tweet.name}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    @{tweet.username}
                  </Typography>
                  {tweet.heat_score !== undefined && (
                    <Box 
                      component="span"
                      sx={{ 
                        ml: 'auto', 
                        fontSize: '0.6rem',
                        px: 0.5,
                        py: 0.1,
                        borderRadius: 1,
                        bgcolor: 
                          tweet.heat_score > 80 ? 'error.main' : 
                          tweet.heat_score > 50 ? 'warning.main' : 
                          'info.main',
                        color: 'white'
                      }}
                    >
                      {tweet.heat_score}°
                    </Box>
                  )}
                </Box>
              }
              subheader={
                <Typography variant="caption" color="text.secondary">
                  {formatDate(tweet.created_at)}
                </Typography>
              }
            />
            <CardContent sx={{ py: 0.5, px: 1.5 }}>
              <Typography variant="body2">{tweet.text}</Typography>
            </CardContent>
            
            {tweet.media && tweet.media.length > 0 && tweet.media[0].type === 'photo' && (
              <CardMedia
                component="img"
                image={tweet.media[0].url}
                alt="Tweet media"
                sx={{ maxHeight: 150, objectFit: 'contain' }}
              />
            )}
            
            <Box sx={{ display: 'flex', p: 0.5, pl: 1.5 }}>
              <Typography variant="caption" color="text.secondary" sx={{ mr: 1 }}>
                ♥ {tweet.likes_count}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                ↻ {tweet.retweets_count}
              </Typography>
            </Box>
          </Card>
        ))
      )}
      
      {/* Settings Dialog */}
      <Dialog open={openSettings} onClose={() => setOpenSettings(false)} maxWidth="xs">
        <DialogTitle>X Feed Settings</DialogTitle>
        <DialogContent>
          <Typography variant="subtitle2" sx={{ mb: 1 }}>Add X accounts to follow</Typography>
          
          <Box sx={{ display: 'flex', mb: 2 }}>
            <TextField
              fullWidth
              variant="outlined"
              size="small"
              placeholder="@username"
              value={newHandle}
              onChange={(e) => setNewHandle(e.target.value)}
              sx={{ mr: 1 }}
            />
            <Button 
              variant="contained" 
              size="small"
              onClick={handleAddAccount}
              disabled={!newHandle}
            >
              Add
            </Button>
          </Box>
          
          <Divider sx={{ my: 1 }} />
          
          <Typography variant="subtitle2" sx={{ mb: 1 }}>Followed Accounts</Typography>
          
          {followedAccounts.length === 0 ? (
            <Typography variant="body2" color="text.secondary">
              No accounts added yet
            </Typography>
          ) : (
            <List dense disablePadding>
              {followedAccounts.map(handle => (
                <ListItem
                  key={handle}
                  dense
                  secondaryAction={
                    <IconButton edge="end" onClick={() => handleRemoveAccount(handle)} size="small">
                      <DeleteIcon fontSize="small" />
                    </IconButton>
                  }
                >
                  <Typography variant="body2">@{handle}</Typography>
                </ListItem>
              ))}
            </List>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenSettings(false)} size="small">Close</Button>
        </DialogActions>
      </Dialog>
    </Paper>
  );
};

export default XFeed;
