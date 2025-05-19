"""
Social Media Service for Grace - A crypto trading application based on Open Interpreter

This module implements a social media service using snscrape to gather social media data.
It provides a dynamic approach for function generation based on user requests.
"""

import logging
import time
from typing import Dict, List, Optional, Any, Union, Iterator
from datetime import datetime, timedelta
import snscrape.modules.twitter as sntwitter
from snscrape.base import ScraperException
import backoff  # For exponential backoff on rate limits

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("GraceSocialMediaService")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("GraceSocialMediaService")

class SocialMediaService:
    """Service for interacting with social media platforms using snscrape."""
    
    def __init__(
        self,
        memory_system = None,
        cache_duration: int = 3600,  # 1 hour cache by default
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the Social Media service.
        
        Args:
            memory_system: Memory system for storing and retrieving data
            cache_duration: Duration in seconds to cache results
            config: Additional configuration options
        """
        self.memory_system = memory_system
        self.cache_duration = cache_duration
        self.config = config or {}
        self.cache = {}
        self.community_seeds = {}
        
        logger.info("Initialized Social Media service with snscrape")
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Get data from cache if available and not expired.
        
        Args:
            cache_key: Cache key
            
        Returns:
            Optional[Dict[str, Any]]: Cached data or None
        """
        if cache_key in self.cache:
            cache_entry = self.cache[cache_key]
            if datetime.now() < cache_entry["expires_at"]:
                logger.info(f"Cache hit for key: {cache_key}")
                return cache_entry["data"]
            else:
                logger.info(f"Cache expired for key: {cache_key}")
                del self.cache[cache_key]
        
        return None
    
    def _add_to_cache(self, cache_key: str, data: Dict[str, Any], duration: Optional[int] = None) -> None:
        """
        Add data to cache.
        
        Args:
            cache_key: Cache key
            data: Data to cache
            duration: Cache duration in seconds (overrides default)
        """
        cache_duration = duration or self.cache_duration
        expires_at = datetime.now() + timedelta(seconds=cache_duration)
        
        self.cache[cache_key] = {
            "data": data,
            "expires_at": expires_at
        }
        
        logger.info(f"Added to cache with key: {cache_key}, expires at: {expires_at}")
    
    @backoff.on_exception(
        backoff.expo,
        (ScraperException, Exception),
        max_tries=3,
        max_time=30
    )
    def search_twitter(
        self,
        query: str,
        search_type: str = "tweets",
        count: int = 20,
        use_cache: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Search Twitter for tweets, users, or hashtags using snscrape.
        
        Args:
            query: Search query (username, hashtag, or search term)
            search_type: Type of search (tweets, users, hashtags)
            count: Maximum number of results to return (default: 20, max: 1000)
            use_cache: Whether to use cache (default: True)
            **kwargs: Additional search parameters
                - since: datetime - Return tweets after this date
                - until: datetime - Return tweets before this date
                - lang: str - Filter by language (e.g., 'en')
                - include_retweets: bool - Include retweets (default: False)
                - include_replies: bool - Include replies (default: False)
                - min_faves: int - Minimum number of likes
                - min_retweets: int - Minimum number of retweets
        
        Returns:
            Dict[str, Any]: Search results with metadata
        """
        # Validate count
        count = max(1, min(count, 1000))  # Enforce reasonable limits
        
        # Create cache key
        cache_key = f"search_{search_type}_{query}_{count}"
        
        # Check cache
        if use_cache:
            cached_data = self._get_from_cache(cache_key)
            if cached_data:
                return cached_data
        
        try:
            results = []
            search_query = self._build_search_query(query, search_type, **kwargs)
            
            # Create appropriate scraper based on search type
            if search_type == "tweets":
                scraper = sntwitter.TwitterSearchScraper(search_query, top=True)
            elif search_type == "users":
                scraper = sntwitter.TwitterUserScraper(query)
            elif search_type == "hashtags":
                if not query.startswith("#"):
                    query = f"#{query}"
                scraper = sntwitter.TwitterHashtagScraper(query[1:])  # Remove # for the scraper
            else:
                raise ValueError(f"Unsupported search type: {search_type}")
            
            # Process items with rate limiting
            for i, item in enumerate(scraper.get_items()):
                if i >= count:
                    break
                results.append(item)
                # Add small delay between requests to be nice to the API
                time.sleep(0.1)
            
            # Process results
            processed_results = self._process_search_results(results, search_type)
            
            # Cache results
            response = {
                "query": query,
                "search_type": search_type,
                "count": len(processed_results),
                "results": processed_results
            }
            
            if use_cache and processed_results:  # Only cache if we have results
                self._add_to_cache(cache_key, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Error searching Twitter: {str(e)}", exc_info=True)
            return {"error": f"Error performing search: {str(e)}", "results": []}
    
    def _build_search_query(self, query: str, search_type: str, **kwargs) -> str:
        """
        Build a search query for snscrape based on parameters.
        
        Args:
            query: The base search query
            search_type: Type of search (tweets, users, hashtags)
            **kwargs: Additional search parameters
                - since: datetime - Return tweets after this date
                - until: datetime - Return tweets before this date
                - lang: str - Filter by language (e.g., 'en')
                - include_retweets: bool - Include retweets (default: False)
                - include_replies: bool - Include replies (default: False)
                - min_faves: int - Minimum number of likes
                - min_retweets: int - Minimum number of retweets
        
        Returns:
            str: Formatted search query
        """
        query_parts = []
        
        # Clean and validate the base query
        query = query.strip()
        if not query:
            raise ValueError("Query cannot be empty")
        
        # Handle different search types
        if search_type == "users":
            # For user search, we just want the username
            return query.lstrip('@')
        
        # For tweets and hashtags, build a more complex query
        if search_type == "hashtags":
            query = query.lstrip('#')
            query_parts.append(f"#{query}")
        else:
            query_parts.append(query)
        
        # Add filters based on parameters
        if not kwargs.get('include_replies', False):
            query_parts.append("-filter:replies")
            
        if not kwargs.get('include_retweets', False):
            query_parts.append("-filter:retweets")
        
        # Add date filters
        if 'since' in kwargs and kwargs['since']:
            if isinstance(kwargs['since'], str):
                since_date = kwargs['since']
            else:
                since_date = kwargs['since'].strftime('%Y-%m-%d')
            query_parts.append(f"since:{since_date}")
            
        if 'until' in kwargs and kwargs['until']:
            if isinstance(kwargs['until'], str):
                until_date = kwargs['until']
            else:
                until_date = kwargs['until'].strftime('%Y-%m-%d')
            query_parts.append(f"until:{until_date}")
        
        # Add language filter
        if 'lang' in kwargs and kwargs['lang']:
            query_parts.append(f"lang:{kwargs['lang']}")
        
        # Add engagement filters
        if 'min_faves' in kwargs and kwargs['min_faves']:
            query_parts.append(f"min_faves:{int(kwargs['min_faves'])}")
            
        if 'min_retweets' in kwargs and kwargs['min_retweets']:
            query_parts.append(f"min_retweets:{int(kwargs['min_retweets'])}")
        
        # Join all query parts with spaces
        return ' '.join(query_parts)
    
    def _process_search_results(self, results: List[Any], search_type: str) -> List[Dict[str, Any]]:
        """
        Process raw search results from snscrape into a consistent format.
        
        Args:
            results: List of raw result objects from snscrape
            search_type: Type of search (tweets, users, hashtags)
            
        Returns:
            List[Dict[str, Any]]: Processed results with consistent structure
        """
        processed_results = []
        
        for result in results:
            try:
                if search_type in ["tweets", "hashtags"]:
                    # Handle tweet objects with null checks
                    user = getattr(result, 'user', None)
                    tweet_id = getattr(result, 'id', '')
                    
                    # Get media information
                    media = []
                    if hasattr(result, 'media') and result.media:
                        for m in result.media:
                            if hasattr(m, 'previewUrl'):
                                media.append({
                                    'type': m.__class__.__name__,
                                    'url': getattr(m, 'previewUrl', ''),
                                    'full_url': getattr(m, 'fullUrl', '')
                                })
                    
                    # Get quoted tweet if exists
                    quoted_tweet = None
                    if hasattr(result, 'quotedTweet') and result.quotedTweet:
                        quoted_tweet = {
                            'id': str(getattr(result.quotedTweet, 'id', '')),
                            'username': getattr(getattr(result.quotedTweet, 'user', {}), 'username', '')
                        }
                    
                    # Get retweet info if this is a retweet
                    retweeted_tweet = None
                    if hasattr(result, 'retweetedTweet') and result.retweetedTweet:
                        retweeted_tweet = {
                            'id': str(getattr(result.retweetedTweet, 'id', '')),
                            'username': getattr(getattr(result.retweetedTweet, 'user', {}), 'username', '')
                        }
                    
                    processed_result = {
                        "id": str(tweet_id),
                        "text": getattr(result, 'rawContent', ''),
                        "username": getattr(user, 'username', '') if user else '',
                        "name": getattr(user, 'displayname', '') if user else '',
                        "date": getattr(result, 'date', '').isoformat() if hasattr(result, 'date') and result.date else '',
                        "likes": getattr(result, 'likeCount', 0) or 0,
                        "retweets": getattr(result, 'retweetCount', 0) or 0,
                        "replies": getattr(result, 'replyCount', 0) or 0,
                        "quotes": getattr(result, 'quoteCount', 0) or 0,
                        "is_retweet": bool(retweeted_tweet),
                        "is_quote": bool(quoted_tweet),
                        "has_media": len(media) > 0,
                        "media": media,
                        "url": f"https://twitter.com/{getattr(user, 'username', '')}/status/{tweet_id}" if user else f"https://twitter.com/i/web/status/{tweet_id}",
                        "language": getattr(result, 'lang', ''),
                        "source": getattr(result, 'sourceLabel', ''),
                        "quoted_tweet": quoted_tweet,
                        "retweeted_tweet": retweeted_tweet,
                        "sentiment": self._analyze_sentiment(getattr(result, 'rawContent', '')),
                        "scraped_at": datetime.utcnow().isoformat()
                    }
                    
                elif search_type == "users":
                    # Handle user objects with null checks
                    processed_result = {
                        "id": str(getattr(result, 'id', '')),
                        "username": getattr(result, 'username', ''),
                        "name": getattr(result, 'displayname', ''),
                        "bio": getattr(result, 'description', '') or "",
                        "location": getattr(result, 'location', '') or "",
                        "website": getattr(result, 'linkUrl', '') or "",
                        "joined_date": getattr(result, 'created', '').isoformat() if hasattr(result, 'created') and result.created else "",
                        "followers": getattr(result, 'followersCount', 0) or 0,
                        "following": getattr(result, 'friendsCount', 0) or 0,
                        "tweets": getattr(result, 'statusesCount', 0) or 0,
                        "is_verified": getattr(result, 'verified', False) or False,
                        "protected": getattr(result, 'protected', False) or False,
                        "profile_image": (getattr(result, 'profileImageUrl', '') or '').replace('_normal', ''),  # Full-size image
                        "banner_image": getattr(result, 'profileBannerUrl', '') or "",
                        "url": f"https://twitter.com/{getattr(result, 'username', '')}",
                        "scraped_at": datetime.utcnow().isoformat()
                    }
                else:
                    # Fallback for unknown result types
                    processed_result = {
                        "raw_data": str(result),
                        "type": result.__class__.__name__,
                        "scraped_at": datetime.utcnow().isoformat()
                    }
                
                processed_results.append(processed_result)
                
            except Exception as e:
                logger.error(f"Error processing result: {str(e)}", exc_info=True)
                continue
        
        return processed_results
    
    @backoff.on_exception(
        backoff.expo,
        (ScraperException, StopIteration, Exception),
        max_tries=3,
        max_time=30
    )
    async def get_user_profile(
        self, 
        username: str, 
        use_cache: bool = True,
        include_media: bool = True,
        include_timeline: bool = False,
        timeline_count: int = 10
    ) -> Dict[str, Any]:
        """
        Get a user's Twitter profile with enhanced media and link handling.
        
        Args:
            username: Twitter username (with or without @)
            use_cache: Whether to use cached results (default: True)
            include_media: Whether to include media in the profile (default: True)
            include_timeline: Whether to include recent tweets in the response (default: False)
            timeline_count: Number of recent tweets to include if include_timeline is True (default: 10)
            
        Returns:
            Dict[str, Any]: User profile information with optional media and timeline
        """
        # Remove @ if present and normalize username
        username = username.lstrip('@').lower()
        cache_key = f"user_profile:{username}:{include_media}:{include_timeline}:{timeline_count}"
        
        # Try to get from cache
        if use_cache:
            cached = self._get_from_cache(cache_key)
            if cached is not None:
                return cached
        
        try:
            # Get user profile using TwitterUserScraper
            scraper = sntwitter.TwitterUserScraper(username)
            
            # Get the first item (user profile)
            try:
                user = next(scraper.get_items()).user
            except StopIteration:
                return {"error": f"User @{username} not found or profile is private"}
            
            # Initialize profile data with basic user information
            profile_data = {
                'id': str(user.id) if hasattr(user, 'id') else None,
                'username': getattr(user, 'username', username),
                'display_name': getattr(user, 'displayname', ''),
                'description': getattr(user, 'rawDescription', ''),
                'location': getattr(user, 'location', ''),
                'url': getattr(user, 'url', ''),
                'followers_count': getattr(user, 'followersCount', 0),
                'friends_count': getattr(user, 'friendsCount', 0),
                'listed_count': getattr(user, 'listedCount', 0),
                'favourites_count': getattr(user, 'likeCount', 0),
                'statuses_count': getattr(user, 'statusesCount', 0),
                'created_at': user.created.isoformat() if hasattr(user, 'created') and user.created else None,
                'profile_image_url': getattr(user, 'profileImageUrl', ''),
                'profile_banner_url': getattr(user, 'profileBannerUrl', ''),
                'default_profile': False,
                'default_profile_image': False,
                'verified': getattr(user, 'verified', False),
                'protected': getattr(user, 'protected', False),
                'media_count': 0,
                'media': []
            }
            
            # Skip timeline if user is protected and we don't have access
            if getattr(user, 'protected', False):
                logger.warning(f"User @{username} has a protected account. Cannot fetch timeline.")
                return profile_data
            
            # Get user's timeline for media if requested
            if include_media or include_timeline:
                try:
                    # Use TwitterSearchScraper to get user's tweets
                    query = f"from:{username} filter:media" if include_media else f"from:{username}"
                    timeline_scraper = sntwitter.TwitterSearchScraper(query)
                    timeline_tweets = []
                    media_count = 0
                    
                    # Process timeline tweets
                    for i, tweet in enumerate(timeline_scraper.get_items()):
                        if i >= max(10, timeline_count if include_timeline else 0):
                            break
                        
                        try:
                            tweet_data = {
                                'id': str(tweet.id),
                                'content': getattr(tweet, 'rawContent', ''),
                                'created_at': tweet.date.isoformat() if hasattr(tweet, 'date') else None,
                                'likes': getattr(tweet, 'likeCount', 0),
                                'retweets': getattr(tweet, 'retweetCount', 0),
                                'replies': getattr(tweet, 'replyCount', 0)
                            }
                            
                            # Process media if requested and available
                            if include_media and hasattr(tweet, 'media') and tweet.media:
                                media_items = self._process_media(tweet.media)
                                if media_items:
                                    tweet_data['media'] = media_items
                                    media_count += len(media_items)
                                    
                                    # Add to profile media if we don't have enough yet
                                    if len(profile_data['media']) < 10:  # Max 10 media items in profile
                                        profile_data['media'].extend(media_items[:10 - len(profile_data['media'])])
                            
                            # Process links if requested
                            if include_timeline:
                                tweet_data['links'] = self._process_links(tweet)
                                
                                # Add quoted tweet if present
                                if hasattr(tweet, 'quotedTweet') and tweet.quotedTweet:
                                    quoted = tweet.quotedTweet
                                    quoted_data = {
                                        'id': str(quoted.id) if hasattr(quoted, 'id') else None,
                                        'username': getattr(quoted.user, 'username', '') if hasattr(quoted, 'user') else '',
                                        'content': getattr(quoted, 'rawContent', ''),
                                        'created_at': quoted.date.isoformat() if hasattr(quoted, 'date') else None
                                    }
                                    if include_media and hasattr(quoted, 'media') and quoted.media:
                                        quoted_data['media'] = self._process_media(quoted.media)
                                    tweet_data['quoted_tweet'] = quoted_data
                            
                            if include_timeline:
                                timeline_tweets.append(tweet_data)
                                
                        except Exception as e:
                            logger.warning(f"Error processing tweet: {str(e)}")
                            continue
                    
                    # Update profile with media and timeline data
                    profile_data['media_count'] = media_count
                    if include_timeline:
                        profile_data['timeline'] = timeline_tweets
                except Exception as e:
                    logger.warning(f"Could not fetch user timeline: {str(e)}")
            
            # Cache the results
            self._add_to_cache(cache_key, profile_data, duration=86400)  # Cache for 24 hours
            
            return profile_data
            
        except Exception as e:
            error_msg = f"Error getting user profile for @{username}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {"error": error_msg}
    
    @backoff.on_exception(
        backoff.expo,
        (ScraperException, Exception),
        max_tries=3,
        max_time=30
    )
    def get_user_tweets(
        self,
        username: str,
        count: int = 20,
        include_replies: bool = False,
        include_retweets: bool = False,
        use_cache: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get tweets from a specific user using snscrape.
        
        Args:
            username: Twitter username (with or without @)
            count: Maximum number of tweets to return (default: 20, max: 1000)
            include_replies: Include replies in results (default: False)
            include_retweets: Include retweets in results (default: False)
            use_cache: Use cached results if available (default: True)
            **kwargs: Additional parameters:
                - since: datetime - Return tweets after this date
                - until: datetime - Return tweets before this date
                - min_faves: int - Minimum number of likes
                - min_retweets: int - Minimum number of retweets
        
        Returns:
            Dict[str, Any]: Tweets and metadata or error information
        """
        # Clean username and validate count
        username = str(username).lstrip('@')
        count = max(1, min(count, 1000))  # Enforce reasonable limits
        
        # Create cache key
        cache_key = f"tweets_{username.lower()}_{count}_{include_replies}_{include_retweets}"
        
        # Check cache
        if use_cache:
            cached_data = self._get_from_cache(cache_key)
            if cached_data:
                return cached_data
        
        try:
            # Build query based on parameters
            query_parts = [f"from:{username}"]
            
            if not include_replies:
                query_parts.append("-filter:replies")
            if not include_retweets:
                query_parts.append("-filter:retweets")
            
            # Add date filters if provided
            if 'since' in kwargs and kwargs['since']:
                query_parts.append(f"since:{kwargs['since'].strftime('%Y-%m-%d')}")
            if 'until' in kwargs and kwargs['until']:
                query_parts.append(f"until:{kwargs['until'].strftime('%Y-%m-%d')}")
                
            # Add engagement filters if provided
            if 'min_faves' in kwargs and kwargs['min_faves']:
                query_parts.append(f"min_faves:{kwargs['min_faves']}")
            if 'min_retweets' in kwargs and kwargs['min_retweets']:
                query_parts.append(f"min_retweets:{kwargs['min_retweets']}")
            
            query = ' '.join(query_parts)
            
            # Get tweets with rate limiting
            tweets = []
            scraper = sntwitter.TwitterSearchScraper(query, top=True)
            
            # Use a timeout to prevent hanging on large accounts
            start_time = time.time()
            timeout = 30  # seconds
            
            try:
                for i, tweet in enumerate(scraper.get_items()):
                    if i >= count or (time.time() - start_time) > timeout:
                        break
                    tweets.append(tweet)
                    # Add small delay between requests
                    time.sleep(0.1)
            except Exception as e:
                logger.warning(f"Error fetching tweets for @{username}: {str(e)}")
            
            # Process tweets
            processed_tweets = self._process_search_results(tweets, "tweets")
            
            # Cache tweets (with shorter TTL for more dynamic content)
            response = {
                "username": username,
                "count": len(processed_tweets),
                "include_replies": include_replies,
                "include_retweets": include_retweets,
                "tweets": processed_tweets,
                "query_used": query  # For debugging
            }
            
            if use_cache and processed_tweets:  # Only cache if we have results
                self._add_to_cache(cache_key, response, duration=1800)  # Cache for 30 minutes
            
            return response
            
        except Exception as e:
            logger.error(f"Error getting tweets for @{username}: {str(e)}", exc_info=True)
            return {"error": f"Error retrieving tweets: {str(e)}", "tweets": []}
    
    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of text with more detailed scoring.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dict[str, Any]: Sentiment analysis with score and confidence
        """
        if not text or not isinstance(text, str):
            return {
                "sentiment": "neutral",
                "score": 0.0,
                "confidence": 0.0,
                "positive": 0.0,
                "negative": 0.0,
                "neutral": 1.0
            }
            
        text_lower = text.lower()
        
        # Define sentiment indicators with weights
        positive_indicators = {
            # Crypto/Finance specific
            "bullish": 2.0, "moon": 1.5, "up": 1.0, "gain": 1.2, "profit": 1.3,
            "win": 1.2, "good": 0.8, "great": 1.0, "excellent": 1.3, "amazing": 1.2,
            "buy": 1.0, "long": 0.8, "strong": 0.7, "growth": 0.9, "success": 1.1,
            "🚀": 1.5, "💎": 1.2, "📈": 1.3, "🔥": 1.1, "🚀🚀": 2.0,
            # General positive
            "love": 1.2, "like": 0.8, "awesome": 1.3, "perfect": 1.4, "best": 1.1,
            "recommend": 1.0, "enjoy": 0.9, "happy": 1.1, "excited": 1.2, "impressed": 1.1
        }
        
        negative_indicators = {
            # Crypto/Finance specific
            "bearish": 2.0, "crash": 2.5, "down": 1.0, "loss": 1.5, "bad": 0.8,
            "terrible": 1.3, "poor": 0.9, "fail": 1.2, "scam": 2.0, "dump": 1.8,
            "sell": 1.0, "short": 0.8, "weak": 0.7, "drop": 1.2, "fraud": 2.0,
            "📉": 1.5, "💀": 1.8, "😱": 1.3, "🔥": 1.2, "scam": 2.0,
            # General negative
            "hate": 1.5, "worst": 1.4, "terrible": 1.3, "awful": 1.4, "poor": 1.1,
            "disappoint": 1.2, "avoid": 1.3, "waste": 1.1, "problem": 1.0, "issue": 1.0
        }
        
        # Calculate sentiment scores with weights
        positive_score = sum(weight for word, weight in positive_indicators.items() 
                           if word in text_lower)
        negative_score = sum(weight for word, weight in negative_indicators.items() 
                           if word in text_lower)
        
        # Handle emojis and special characters
        emoji_positive = sum(1 for char in text_lower if char in ["🚀", "💎", "📈", "🔥"])
        emoji_negative = sum(1 for char in text_lower if char in ["📉", "💀", "😱"])
        
        positive_score += emoji_positive * 1.2
        negative_score += emoji_negative * 1.2
        
        # Calculate sentiment (normalize scores)
        total = positive_score + negative_score
        
        if total > 0:
            positive_norm = positive_score / total
            negative_norm = negative_score / total
            
            # Calculate confidence based on the difference between positive and negative
            confidence = abs(positive_norm - negative_norm)
            
            # Determine sentiment with a threshold
            if positive_score > negative_score * 1.3:  # 30% more positive
                sentiment = "positive"
                score = positive_norm
            elif negative_score > positive_score * 1.3:  # 30% more negative
                sentiment = "negative"
                score = -negative_norm
            else:
                sentiment = "neutral"
                score = 0
                confidence = 1.0 - confidence  # Low confidence for neutral
        else:
            sentiment = "neutral"
            score = 0.0
            confidence = 0.0
        
        return {
            "sentiment": sentiment,
            "score": round(score, 4),
            "confidence": round(confidence, 4),
            "positive": round(positive_score, 4),
            "negative": round(negative_score, 4),
            "neutral": round(max(0, 1 - (positive_score + negative_score) / 10), 4)  # Neutral decreases with strong signals
        }
    
    # The following methods maintain compatibility with the NitterService interface
    # but may not be fully implemented or may have limited functionality
    
    def update_community_seeds(
        self,
        community: str,
        add_handles: List[str] = None,
        remove_handles: List[str] = None
    ) -> Dict[str, Any]:
        """
        Update community seeds.
        
        Args:
            community: Community name
            add_handles: Handles to add
            remove_handles: Handles to remove
            
        Returns:
            Dict[str, Any]: Updated community seeds
        """
        if community not in self.community_seeds:
            self.community_seeds[community] = set()
        
        if add_handles:
            self.community_seeds[community].update(
                handle.lower().lstrip('@') for handle in add_handles
            )
        
        if remove_handles:
            for handle in remove_handles:
                handle = handle.lower().lstrip('@')
                if handle in self.community_seeds[community]:
                    self.community_seeds[community].remove(handle)
        
        return {
            "community": community,
            "seeds": list(self.community_seeds.get(community, [])),
            "seed_count": len(self.community_seeds.get(community, []))
        }
    
    def get_community_pulse(self, community: str, count: int = 5, use_cache: bool = True) -> Dict[str, Any]:
        """
        Get community pulse.
        
        Args:
            community: Community name
            count: Number of tweets per seed
            use_cache: Whether to use cache
            
        Returns:
            Dict[str, Any]: Community pulse
        """
        cache_key = f"community_pulse_{community}_{count}"
        
        if use_cache:
            cached_data = self._get_from_cache(cache_key)
            if cached_data:
                return cached_data
        
        seeds = self.community_seeds.get(community, set())
        if not seeds:
            return {
                "community": community,
                "seed_count": 0,
                "tweets": [],
                "message": f"No seeds found for community '{community}'. Add seeds using update_community_seeds."
            }
        
        all_tweets = []
        
        for seed in seeds:
            try:
                # Get user's tweets
                user_tweets = self.get_user_tweets(
                    username=seed,
                    count=count,
                    include_replies=False,
                    include_retweets=False,
                    use_cache=use_cache
                )
                
                if "tweets" in user_tweets:
                    all_tweets.extend(user_tweets["tweets"])
                    
            except Exception as e:
                logger.error(f"Error getting tweets for seed {seed}: {str(e)}")
        
        # Sort tweets by date (newest first)
        all_tweets.sort(key=lambda x: x.get("date", ""), reverse=True)
        
        response = {
            "community": community,
            "seed_count": len(seeds),
            "tweet_count": len(all_tweets),
            "tweets": all_tweets[:count * 5]  # Limit total number of tweets
        }
        
        if use_cache:
            self._add_to_cache(cache_key, response)
        
        return response
    
    def discover_community_changes(self, community: str) -> Dict[str, Any]:
        """
        Discover changes in community.
        
        Args:
            community: Community name
            
        Returns:
            Dict[str, Any]: Discovered changes
        """
        # This is a simplified implementation
        # In a real-world scenario, you would compare current state with a previous state
        
        # Get current community pulse
        current_pulse = self.get_community_pulse(community, count=10, use_cache=False)
        
        # This is a placeholder for change detection logic
        # In a real implementation, you would compare with previous state
        changes = {
            "new_tweets": current_pulse.get("tweets", [])[:5],
            "trending_topics": [],
            "sentiment_changes": {}
        }
        
        return {
            "community": community,
            "changes": changes,
            "timestamp": datetime.now().isoformat()
        }
    
    def associate_with_entity(self, query: str, entity: str, memory_system = None) -> Dict[str, Any]:
        """
        Associate search results with an entity in memory.
        
        Args:
            query: Search query
            entity: Entity to associate with
            memory_system: Memory system (overrides instance memory_system)
            
        Returns:
            Dict[str, Any]: Association result
        """
        # This is a simplified implementation
        memory = memory_system or self.memory_system
        
        if not memory:
            return {
                "success": False,
                "error": "No memory system available",
                "query": query,
                "entity": entity
            }
        
        try:
            # Search for the query
            search_results = self.search_twitter(query, count=5)
            
            # Store the association in memory
            memory.store(
                key=f"entity_association:{entity}:{int(time.time())}",
                value={
                    "query": query,
                    "results": search_results.get("results", []),
                    "timestamp": datetime.now().isoformat()
                },
                metadata={
                    "entity": entity,
                    "query": query,
                    "result_count": len(search_results.get("results", [])),
                    "source": "twitter_search"
                }
            )
            
            return {
                "success": True,
                "query": query,
                "entity": entity,
                "result_count": len(search_results.get("results", [])),
                "message": f"Successfully associated {len(search_results.get('results', []))} results with entity '{entity}'"
            }
            
        except Exception as e:
            logger.error(f"Error associating with entity: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "query": query,
                "entity": entity
            }
    
    def track_entity_mentions(self, entity: str, count: int = 20, use_cache: bool = False) -> Dict[str, Any]:
        """
        Track mentions of an entity.
        
        Args:
            entity: Entity to track
            count: Number of results to return
            use_cache: Whether to use cache
            
        Returns:
            Dict[str, Any]: Tracking result
        """
        # This is a simplified implementation that just does a search
        return self.search_twitter(
            query=entity,
            search_type="tweets",
            count=count,
            use_cache=use_cache
        )
    
    def execute_dynamic_function(self, function_name: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a dynamic function based on name and parameters.
        
        Args:
            function_name: Name of function to execute
            **kwargs: Function parameters
            
        Returns:
            Dict[str, Any]: Function result
        """
        if not hasattr(self, function_name):
            return {
                "error": f"Function '{function_name}' not found",
                "available_functions": [
                    "search_twitter",
                    "get_user_profile",
                    "get_user_tweets",
                    "update_community_seeds",
                    "get_community_pulse",
                    "discover_community_changes",
                    "associate_with_entity",
                    "track_entity_mentions"
                ]
            }
        
        try:
            result = getattr(self, function_name)(**kwargs)
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
