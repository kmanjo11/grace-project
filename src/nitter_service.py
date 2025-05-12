"""
Nitter Service for Grace - A crypto trading application based on Open Interpreter

This module implements the Nitter service using NTscraper to gather social media data
from a local Nitter instance. It provides a dynamic approach for function generation
based on user requests.
"""

from src.config import get_config

import os
import sys
import json
import time
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import re

from ntscraper import Nitter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("GraceNitterService")

class NitterService:
    """Service for interacting with Nitter to gather social media data."""
    
    def __init__(
        self,
        nitter_instance: str = "http://localhost:8085",
        memory_system = None,
        cache_duration: int = 3600,  # 1 hour cache by default
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the Nitter service.
        
        Args:
            nitter_instance: URL of the Nitter instance
            memory_system: Memory system for storing and retrieving data
            cache_duration: Duration in seconds to cache results
            config: Additional configuration options
        """
        self.nitter_instance = nitter_instance
        self.memory_system = memory_system
        self.cache_duration = cache_duration
        self.config = config or {}
        self.cache = {}
        self.community_seeds = {}
        
        # Initialize Nitter scraper with fallbacks
        nitter_instances = [
            nitter_instance,  # Try user-provided instance first
            "http://nitter:8080",  # Try Docker service name
        ]
        
        for instance in nitter_instances:
            try:
                self.scraper = Nitter(instance)
                logger.info(f"Initialized Nitter scraper with instance: {instance}")
                break
            except Exception:
                continue
        
        if not hasattr(self, 'scraper'):
            logger.warning("Nitter service unavailable - social features will be limited")
            self.scraper = None
    
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
    
    def search_twitter(
        self,
        query: str,
        search_type: str = "tweets",
        count: int = 20,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Search Twitter for tweets matching a query.
        
        Args:
            query: Search query
            search_type: Type of search (tweets, users, hashtags)
            count: Number of results to return
            use_cache: Whether to use cache
            
        Returns:
            Dict[str, Any]: Search results
        """
        if not self.scraper:
            logger.error("Nitter scraper not initialized")
            return {"error": "Nitter scraper not initialized", "results": []}
        
        # Create cache key
        cache_key = f"search_{search_type}_{query}_{count}"
        
        # Check cache
        if use_cache:
            cached_data = self._get_from_cache(cache_key)
            if cached_data:
                return cached_data
        
        try:
            # Perform search based on type
            if search_type == "tweets":
                results = self.scraper.get_tweets(query, count)
            elif search_type == "users":
                results = self.scraper.get_users(query, count)
            elif search_type == "hashtags":
                # Extract hashtag without # if present
                if query.startswith("#"):
                    query = query[1:]
                results = self.scraper.get_hashtag(query, count)
            else:
                logger.error(f"Invalid search type: {search_type}")
                return {"error": f"Invalid search type: {search_type}", "results": []}
            
            # Process results
            processed_results = self._process_search_results(results, search_type)
            
            # Cache results
            response = {
                "query": query,
                "search_type": search_type,
                "count": count,
                "results": processed_results
            }
            
            if use_cache:
                self._add_to_cache(cache_key, response)
            
            return response
        except Exception as e:
            logger.error(f"Error searching Twitter: {str(e)}")
            return {"error": str(e), "results": []}
    
    def _process_search_results(self, results: List[Dict[str, Any]], search_type: str) -> List[Dict[str, Any]]:
        """
        Process search results.
        
        Args:
            results: Raw search results
            search_type: Type of search
            
        Returns:
            List[Dict[str, Any]]: Processed results
        """
        processed_results = []
        
        for result in results:
            if search_type == "tweets":
                processed_result = {
                    "id": result.get("id", ""),
                    "text": result.get("text", ""),
                    "username": result.get("username", ""),
                    "name": result.get("name", ""),
                    "date": result.get("date", ""),
                    "likes": result.get("likes", 0),
                    "retweets": result.get("retweets", 0),
                    "replies": result.get("replies", 0),
                    "is_retweet": result.get("is_retweet", False),
                    "is_pinned": result.get("is_pinned", False),
                    "has_media": result.get("has_media", False),
                    "sentiment": self._analyze_sentiment(result.get("text", ""))
                }
            elif search_type == "users":
                processed_result = {
                    "username": result.get("username", ""),
                    "name": result.get("name", ""),
                    "bio": result.get("bio", ""),
                    "followers": result.get("followers", 0),
                    "following": result.get("following", 0),
                    "tweets": result.get("tweets", 0),
                    "is_verified": result.get("is_verified", False),
                    "profile_image": result.get("profile_image", "")
                }
            elif search_type == "hashtags":
                processed_result = {
                    "id": result.get("id", ""),
                    "text": result.get("text", ""),
                    "username": result.get("username", ""),
                    "name": result.get("name", ""),
                    "date": result.get("date", ""),
                    "likes": result.get("likes", 0),
                    "retweets": result.get("retweets", 0),
                    "replies": result.get("replies", 0),
                    "sentiment": self._analyze_sentiment(result.get("text", ""))
                }
            else:
                processed_result = result
            
            processed_results.append(processed_result)
        
        return processed_results
    
    def get_user_profile(self, username: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        Get a user's profile.
        
        Args:
            username: Twitter username
            use_cache: Whether to use cache
            
        Returns:
            Dict[str, Any]: User profile
        """
        if not self.scraper:
            logger.error("Nitter scraper not initialized")
            return {"error": "Nitter scraper not initialized"}
        
        # Create cache key
        cache_key = f"profile_{username}"
        
        # Check cache
        if use_cache:
            cached_data = self._get_from_cache(cache_key)
            if cached_data:
                return cached_data
        
        try:
            # Get user profile
            profile = self.scraper.get_profile(username)
            
            # Process profile
            processed_profile = {
                "username": profile.get("username", ""),
                "name": profile.get("name", ""),
                "bio": profile.get("bio", ""),
                "location": profile.get("location", ""),
                "website": profile.get("website", ""),
                "joined_date": profile.get("joined_date", ""),
                "followers": profile.get("followers", 0),
                "following": profile.get("following", 0),
                "tweets": profile.get("tweets", 0),
                "is_verified": profile.get("is_verified", False),
                "profile_image": profile.get("profile_image", ""),
                "banner_image": profile.get("banner_image", "")
            }
            
            # Cache profile
            response = {
                "username": username,
                "profile": processed_profile
            }
            
            if use_cache:
                self._add_to_cache(cache_key, response)
            
            return response
        except Exception as e:
            logger.error(f"Error getting user profile: {str(e)}")
            return {"error": str(e)}
    
    def get_user_tweets(
        self,
        username: str,
        count: int = 20,
        include_replies: bool = False,
        include_retweets: bool = False,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Get a user's tweets.
        
        Args:
            username: Twitter username
            count: Number of tweets to return
            include_replies: Whether to include replies
            include_retweets: Whether to include retweets
            use_cache: Whether to use cache
            
        Returns:
            Dict[str, Any]: User tweets
        """
        if not self.scraper:
            logger.error("Nitter scraper not initialized")
            return {"error": "Nitter scraper not initialized", "tweets": []}
        
        # Create cache key
        cache_key = f"tweets_{username}_{count}_{include_replies}_{include_retweets}"
        
        # Check cache
        if use_cache:
            cached_data = self._get_from_cache(cache_key)
            if cached_data:
                return cached_data
        
        try:
            # Get user tweets
            tweets = self.scraper.get_tweets_from_user(
                username,
                count,
                include_replies=include_replies,
                include_retweets=include_retweets
            )
            
            # Process tweets
            processed_tweets = self._process_search_results(tweets, "tweets")
            
            # Cache tweets
            response = {
                "username": username,
                "count": count,
                "include_replies": include_replies,
                "include_retweets": include_retweets,
                "tweets": processed_tweets
            }
            
            if use_cache:
                self._add_to_cache(cache_key, response)
            
            return response
        except Exception as e:
            logger.error(f"Error getting user tweets: {str(e)}")
            return {"error": str(e), "tweets": []}
    
    def _analyze_sentiment(self, text: str) -> str:
        """
        Analyze sentiment of text.
        
        Args:
            text: Text to analyze
            
        Returns:
            str: Sentiment (positive, negative, neutral)
        """
        # Simple sentiment analysis based on keywords
        positive_words = ["bullish", "moon", "up", "gain", "profit", "win", "good", "great", "excellent", "amazing"]
        negative_words = ["bearish", "crash", "down", "loss", "bad", "terrible", "poor", "fail", "scam", "dump"]
        
        text_lower = text.lower()
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count * 1.5:
            return "positive"
        elif negative_count > positive_count * 1.5:
            return "negative"
        else:
            return "neutral"
    
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
        add_handles = add_handles or []
        remove_handles = remove_handles or []
        
        # Initialize community if not exists
        if community not in self.community_seeds:
            self.community_seeds[community] = []
        
        # Add handles
        for handle in add_handles:
            if handle not in self.community_seeds[community]:
                self.community_seeds[community].append(handle)
        
        # Remove handles
        for handle in remove_handles:
            if handle in self.community_seeds[community]:
                self.community_seeds[community].remove(handle)
        
        logger.info(f"Updated community seeds for {community}: {self.community_seeds[community]}")
        
        return {
            "community": community,
            "seeds": self.community_seeds[community]
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
        if community not in self.community_seeds:
            logger.error(f"Community not found: {community}")
            return {"error": f"Community not found: {community}", "pulse": []}
        
        if not self.community_seeds[community]:
            logger.error(f"No seeds for community: {community}")
            return {"error": f"No seeds for community: {community}", "pulse": []}
        
        # Create cache key
        cache_key = f"pulse_{community}_{count}"
        
        # Check cache
        if use_cache:
            cached_data = self._get_from_cache(cache_key)
            if cached_data:
                return cached_data
        
        pulse = []
        
        # Get tweets from each seed
        for handle in self.community_seeds[community]:
            try:
                tweets_response = self.get_user_tweets(
                    handle,
                    count=count,
                    include_replies=False,
                    include_retweets=True,
                    use_cache=use_cache
                )
                
                if "error" not in tweets_response:
                    pulse.extend(tweets_response["tweets"])
            except Exception as e:
                logger.error(f"Error getting tweets for {handle}: {str(e)}")
        
        # Sort by date (newest first)
        pulse.sort(key=lambda x: x.get("date", ""), reverse=True)
        
        # Limit to count * number of seeds
        max_tweets = count * len(self.community_seeds[community])
        pulse = pulse[:max_tweets]
        
        # Calculate overall sentiment
        sentiments = [tweet.get("sentiment", "neutral") for tweet in pulse]
        positive_count = sentiments.count("positive")
        negative_count = sentiments.count("negative")
        neutral_count = sentiments.count("neutral")
        
        if positive_count > (negative_count + neutral_count):
            overall_sentiment = "positive"
        elif negative_count > (positive_count + neutral_count):
            overall_sentiment = "negative"
        else:
            overall_sentiment = "neutral"
        
        # Cache pulse
        response = {
            "community": community,
            "seeds": self.community_seeds[community],
            "overall_sentiment": overall_sentiment,
            "sentiment_counts": {
                "positive": positive_count,
                "negative": negative_count,
                "neutral": neutral_count
            },
            "pulse": pulse
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
        if community not in self.community_seeds:
            logger.error(f"Community not found: {community}")
            return {"error": f"Community not found: {community}", "changes": []}
        
        if not self.community_seeds[community]:
            logger.error(f"No seeds for community: {community}")
            return {"error": f"No seeds for community: {community}", "changes": []}
        
        changes = []
        
        # Get tweets from each seed
        for handle in self.community_seeds[community]:
            try:
                tweets_response = self.get_user_tweets(
                    handle,
                    count=50,
                    include_replies=False,
                    include_retweets=True,
                    use_cache=False  # Don't use cache for discovery
                )
                
                if "error" not in tweets_response:
                    # Look for mentions of new accounts
                    for tweet in tweets_response["tweets"]:
                        text = tweet.get("text", "")
                        
                        # Extract mentions
                        mentions = re.findall(r'@(\w+)', text)
                        
                        for mention in mentions:
                            if mention not in self.community_seeds[community] and mention != handle:
                                # Check if mentioned account is relevant
                                try:
                                    profile_response = self.get_user_profile(mention, use_cache=True)
                                    
                                    if "error" not in profile_response:
                                        profile = profile_response["profile"]
                                        
                                        # Check if profile is relevant to crypto
                                        bio = profile.get("bio", "").lower()
                                        crypto_keywords = ["crypto", "bitcoin", "eth", "blockchain", "web3", "defi", "nft"]
                                        
                                        if any(keyword in bio for keyword in crypto_keywords):
                                            changes.append({
                                                "type": "new_account",
                                                "handle": mention,
                                                "discovered_from": handle,
                                                "tweet_id": tweet.get("id", ""),
                                                "profile": profile
                                            })
                                except Exception as e:
                                    logger.warning(f"Error fetching profile for {mention}: {str(e)}")
                            
                        # Extract hashtags
                        hashtags = re.findall(r'#(\w+)', text)
                        
                        for hashtag in hashtags:
                            changes.append({
                                "type": "hashtag",
                                "hashtag": hashtag,
                                "discovered_from": handle,
                                "tweet_id": tweet.get("id", ""),
                                "tweet_text": text
                            })
            except Exception as e:
                logger.error(f"Error discovering community changes for {handle}: {str(e)}")
        
        # Deduplicate changes
        unique_changes = []
        seen_handles = set()
        seen_hashtags = set()
        
        for change in changes:
            if change["type"] == "new_account":
                handle = change["handle"]
                if handle not in seen_handles:
                    seen_handles.add(handle)
                    unique_changes.append(change)
            elif change["type"] == "hashtag":
                hashtag = change["hashtag"]
                if hashtag not in seen_hashtags:
                    seen_hashtags.add(hashtag)
                    unique_changes.append(change)
        
        return {
            "community": community,
            "seeds": self.community_seeds[community],
            "changes": unique_changes
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
        memory = memory_system or self.memory_system
        
        if not memory:
            logger.error("Memory system not available")
            return {"error": "Memory system not available", "success": False}
        
        try:
            # Search Twitter
            search_response = self.search_twitter(query, search_type="tweets", count=10, use_cache=True)
            
            if "error" in search_response:
                return {"error": search_response["error"], "success": False}
            
            # Process results
            results = search_response["results"]
            
            if not results:
                return {"message": "No results found", "success": False}
            
            # Create memory entries
            for result in results:
                content = f"Tweet from @{result['username']}: {result['text']}"
                source = f"Twitter via Nitter (search: {query})"
                
                # Add to memory
                memory.add_memory(
                    content=content,
                    source=source,
                    entity=entity,
                    priority=0.6  # Medium-high priority for social signals
                )
            
            return {
                "query": query,
                "entity": entity,
                "results_count": len(results),
                "success": True
            }
        except Exception as e:
            logger.error(f"Error associating with entity: {str(e)}")
            return {"error": str(e), "success": False}
    
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
        try:
            # Search Twitter for entity
            search_response = self.search_twitter(entity, search_type="tweets", count=count, use_cache=use_cache)
            
            if "error" in search_response:
                return {"error": search_response["error"], "mentions": []}
            
            # Process results
            results = search_response["results"]
            
            # Calculate sentiment distribution
            sentiments = [result.get("sentiment", "neutral") for result in results]
            positive_count = sentiments.count("positive")
            negative_count = sentiments.count("negative")
            neutral_count = sentiments.count("neutral")
            
            if positive_count > (negative_count + neutral_count):
                overall_sentiment = "positive"
            elif negative_count > (positive_count + neutral_count):
                overall_sentiment = "negative"
            else:
                overall_sentiment = "neutral"
            
            return {
                "entity": entity,
                "mentions_count": len(results),
                "overall_sentiment": overall_sentiment,
                "sentiment_counts": {
                    "positive": positive_count,
                    "negative": negative_count,
                    "neutral": neutral_count
                },
                "mentions": results
            }
        except Exception as e:
            logger.error(f"Error tracking entity mentions: {str(e)}")
            return {"error": str(e), "mentions": []}
    
    def execute_dynamic_function(self, function_name: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a dynamic function based on name and parameters.
        
        Args:
            function_name: Name of function to execute
            **kwargs: Function parameters
            
        Returns:
            Dict[str, Any]: Function result
        """
        # Map function names to methods
        function_map = {
            "search_twitter": self.search_twitter,
            "get_user_profile": self.get_user_profile,
            "get_user_tweets": self.get_user_tweets,
            "update_community_seeds": self.update_community_seeds,
            "get_community_pulse": self.get_community_pulse,
            "discover_community_changes": self.discover_community_changes,
            "associate_with_entity": self.associate_with_entity,
            "track_entity_mentions": self.track_entity_mentions
        }
        
        if function_name not in function_map:
            logger.error(f"Unknown function: {function_name}")
            return {"error": f"Unknown function: {function_name}"}
        
        try:
            # Execute function
            result = function_map[function_name](**kwargs)
            return result
        except Exception as e:
            logger.error(f"Error executing dynamic function {function_name}: {str(e)}")
            return {"error": str(e)}

# Example usage
if __name__ == "__main__":
    # Initialize Nitter service
    nitter_service = NitterService(nitter_instance = get_config().get("nitter_instance"))
    
    # Search Twitter
    result = nitter_service.search_twitter("bitcoin")
    print(json.dumps(result, indent=2))
