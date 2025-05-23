"""
Social Media API Router

Handles all social media related endpoints including:
- Sentiment analysis
- Trending topics
- Influential accounts
- Community tracking
- Entity relationships
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
from ...grace_core import get_grace

logger = logging.getLogger("SocialMediaAPI")
router = APIRouter()


# Rate limiting setup
class RateLimiter:
    def __init__(self, requests: int = 100, window: int = 60):
        self.requests = requests
        self.window = window
        self.requests_log = {}

    async def check_rate_limit(self, request: Request) -> bool:
        client_ip = request.client.host
        current_time = time.time()

        if client_ip not in self.requests_log:
            self.requests_log[client_ip] = {"count": 1, "start_time": current_time}
        else:
            # Reset counter if window has passed
            if current_time - self.requests_log[client_ip]["start_time"] > self.window:
                self.requests_log[client_ip] = {"count": 1, "start_time": current_time}
            else:
                self.requests_log[client_ip]["count"] += 1

        return self.requests_log[client_ip]["count"] <= self.requests


# Initialize rate limiter (100 requests per minute per IP)
rate_limiter = RateLimiter(requests=100, window=60)


@router.get("/sentiment")
async def get_sentiment_analysis(
    request: Request,
    query: str,
    days: int = Query(7, ge=1, le=30, description="Number of days to analyze"),
    grace=Depends(get_grace),
):
    """
    Get sentiment analysis for a given query

    Args:
        query: Search query to analyze
        days: Number of days to look back (1-30)

    Returns:
        Dict with sentiment analysis results
    """
    # Check rate limit
    if not await rate_limiter.check_rate_limit(request):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    try:
        sentiment = await grace.social_media_service.analyze_sentiment(
            query=query, days=days
        )
        return {"success": True, "data": sentiment}
    except Exception as e:
        logger.error(f"Error in sentiment analysis: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trending")
async def get_trending_topics(
    request: Request,
    limit: int = Query(10, ge=1, le=50, description="Number of topics to return"),
    grace=Depends(get_grace),
):
    """Get currently trending topics"""
    if not await rate_limiter.check_rate_limit(request):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    try:
        topics = await grace.social_media_service.get_trending_topics(limit=limit)
        return {"success": True, "data": topics}
    except Exception as e:
        logger.error(f"Error getting trending topics: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/influential")
async def get_influential_accounts(
    request: Request,
    topic: Optional[str] = Query(
        None, description="Topic to find influential accounts for"
    ),
    limit: int = Query(20, ge=1, le=100, description="Number of accounts to return"),
    grace=Depends(get_grace),
):
    """Get influential accounts for a topic"""
    if not await rate_limiter.check_rate_limit(request):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    try:
        accounts = await grace.social_media_service.get_influential_accounts(
            topic=topic, limit=limit
        )
        return {"success": True, "data": accounts}
    except Exception as e:
        logger.error(f"Error getting influential accounts: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tweets")
async def get_tweets(
    request: Request,
    query: str,
    limit: int = Query(20, ge=1, le=100, description="Number of tweets to return"),
    include_media: bool = Query(True, description="Include media in results"),
    grace=Depends(get_grace),
):
    """Search for tweets matching a query"""
    if not await rate_limiter.check_rate_limit(request):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    try:
        tweets = await grace.social_media_service.search_twitter(
            query=query, search_type="tweets", count=limit, include_media=include_media
        )
        return {"success": True, "data": tweets}
    except Exception as e:
        logger.error(f"Error searching tweets: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/communities")
async def get_communities(request: Request, grace=Depends(get_grace)):
    """Get tracked communities"""
    if not await rate_limiter.check_rate_limit(request):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    try:
        communities = await grace.social_media_service.get_tracked_communities()
        return {"success": True, "data": communities}
    except Exception as e:
        logger.error(f"Error getting communities: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/entities")
async def get_entities(
    request: Request,
    entity_type: Optional[str] = Query(None, description="Type of entity to filter by"),
    grace=Depends(get_grace),
):
    """Get tracked entities and their relationships"""
    if not await rate_limiter.check_rate_limit(request):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    try:
        entities = await grace.social_media_service.get_entities(
            entity_type=entity_type
        )
        return {"success": True, "data": entities}
    except Exception as e:
        logger.error(f"Error getting entities: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/feed")
async def get_social_feed(
    request: Request,
    limit: int = Query(20, ge=1, le=100, description="Number of feed items to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    grace=Depends(get_grace),
):
    """
    Get a personalized social media feed

    Returns a mix of content from followed accounts, trending topics, and recommended content
    """
    if not await rate_limiter.check_rate_limit(request):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    try:
        # Get user ID from auth token
        user_id = (
            request.state.user.get("id") if hasattr(request.state, "user") else None
        )

        # Get feed items from social media service
        feed = await grace.social_media_service.get_feed(
            user_id=user_id, limit=limit, offset=offset
        )

        return {"success": True, "data": feed}
    except Exception as e:
        logger.error(f"Error getting social feed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/connections")
async def get_social_connections(
    request: Request,
    connection_type: Optional[str] = Query(
        None,
        description="Type of connections to retrieve (e.g., 'following', 'followers', 'mutual')",
    ),
    limit: int = Query(50, ge=1, le=200, description="Number of connections to return"),
    grace=Depends(get_grace),
):
    """
    Get social connections (following/followers)

    Returns the user's social graph connections based on the specified type
    """
    if not await rate_limiter.check_rate_limit(request):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    try:
        # Get user ID from auth token
        user_id = (
            request.state.user.get("id") if hasattr(request.state, "user") else None
        )
        if not user_id:
            raise HTTPException(status_code=401, detail="Authentication required")

        # Get connections from social media service
        connections = await grace.social_media_service.get_connections(
            user_id=user_id, connection_type=connection_type, limit=limit
        )

        return {"success": True, "data": connections}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting social connections: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
