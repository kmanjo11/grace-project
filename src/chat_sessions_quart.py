"""
Chat Sessions Module for Quart

This module provides chat session management endpoints for the Grace application.
It's designed to work with the Quart framework instead of FastAPI.
"""

import os
import json
import uuid
from datetime import datetime
import aioredis
from quart import Blueprint, request, jsonify

# Create a blueprint for chat sessions
chat_blueprint = Blueprint("chat_sessions", __name__)

# Redis client configuration
redis_host = os.environ.get("REDIS_HOST", "localhost")
redis_port = int(os.environ.get("REDIS_PORT", 6379))
redis = None  # Will be initialized in init_app

# In-memory fallback storage for when Redis is unavailable
IN_MEMORY_STORAGE = {
    "sessions": {},  # user_id -> [session_ids]
    "metadata": {},  # session_id -> metadata
    "messages": {},  # session_id -> messages list
}

# Flag to track if we're using fallback storage
USING_FALLBACK = False

# Add proper logging
import logging

logger = logging.getLogger("chat_sessions")


async def init_redis():
    """Initialize Redis connection with robust error handling."""
    global redis, USING_FALLBACK
    try:
        redis_url = f"redis://{redis_host}:{redis_port}"
        logger.info(f"Attempting to connect to Redis at {redis_url}")
        
        redis = await aioredis.from_url(
            redis_url,
            encoding="utf-8",
            decode_responses=True,
            socket_timeout=5,
            socket_connect_timeout=5,
            retry_on_timeout=True
        )
        # Test the connection
        await redis.ping()
        logger.info("Successfully connected to Redis")
        USING_FALLBACK = False
        return True
        USING_FALLBACK = False
        logger.info("Successfully connected to Redis")
        return True
    except Exception as e:
        logger.error(f"Redis connection error: {e}", exc_info=True)
        logger.warning(
            "Falling back to in-memory storage for chat sessions. "
            "Data will not persist between restarts!"
        )
        redis = None
        USING_FALLBACK = True
        return False


async def get_user_id_from_request():
    """Extract user ID from the request's token verification and register active token."""
    try:
        # Extract the token from the request header
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return None

        token = auth_header.replace("Bearer ", "")

        # We'll use the token verification from the main app
        from api_server import verify_token_and_get_user_id

        result = await verify_token_and_get_user_id()

        if result.get("success"):
            user_id = result.get("user_id")

            # Register this token as an active session
            try:
                # Initialize Redis if needed
                if not redis and not USING_FALLBACK:
                    await init_redis()

                if not USING_FALLBACK and redis:
                    # Store token in active sessions in Redis
                    logger.info(
                        f"Registering token for user {user_id} in active sessions"
                    )
                    await redis.sadd("active_tokens", token)
                    # Also create user's sessions set if it doesn't exist
                    await redis.sadd(f"user:{user_id}:sessions", f"default_{user_id}")

                    # Add default session metadata if needed
                    session_key = f"chat:default_{user_id}:meta"
                    session_exists = await redis.exists(session_key)

                    if not session_exists:
                        # Create default session
                        timestamp = datetime.utcnow().isoformat()
                        await redis.hmset_dict(
                            session_key,
                            {
                                "id": f"default_{user_id}",
                                "session_id": f"default_{user_id}",
                                "created": timestamp,
                                "lastActivity": timestamp,
                                "name": "New Chat",
                                "topic": "New Chat",
                            },
                        )
                else:
                    # In-memory fallback
                    logger.info(f"Using in-memory registry for user {user_id} token")
                    # Ensure user exists in sessions directory
                    if user_id not in IN_MEMORY_STORAGE["sessions"]:
                        IN_MEMORY_STORAGE["sessions"][user_id] = []

                    # Create default session if needed
                    default_session_id = f"default_{user_id}"
                    if default_session_id not in IN_MEMORY_STORAGE["sessions"][user_id]:
                        IN_MEMORY_STORAGE["sessions"][user_id].append(
                            default_session_id
                        )
                        timestamp = datetime.utcnow().isoformat()
                        IN_MEMORY_STORAGE["metadata"][default_session_id] = {
                            "id": default_session_id,
                            "session_id": default_session_id,
                            "created": timestamp,
                            "lastActivity": timestamp,
                            "name": "New Chat",
                            "topic": "New Chat",
                        }
                        IN_MEMORY_STORAGE["messages"][default_session_id] = []
            except Exception as reg_error:
                logger.error(f"Error registering token: {reg_error}")
                # Still return the user_id even if registration fails

            return user_id
    except Exception as e:
        logger.error(f"Error getting user ID: {e}")
    return None


@chat_blueprint.route("/api/chat/sessions", methods=["GET"])
async def list_sessions():
    """List all chat sessions for the authenticated user."""
    user_id = await get_user_id_from_request()
    if not user_id:
        return jsonify({"error": "Authentication required"}), 401

    try:
        # Initialize Redis if needed, fallback to in-memory if Redis fails
        if not redis and not USING_FALLBACK:
            await init_redis()

        result = []

        # Use appropriate storage based on Redis availability
        if USING_FALLBACK:
            # Use in-memory fallback storage
            logger.info(f"Using in-memory fallback for user sessions: {user_id}")
            user_sessions = IN_MEMORY_STORAGE["sessions"].get(user_id, [])
            for sid in user_sessions:
                meta = IN_MEMORY_STORAGE["metadata"].get(sid, {})
                if meta:
                    result.append(meta)
        else:
            # Use Redis
            # Get all session IDs for user
            session_ids = await redis.smembers(f"user:{user_id}:sessions")

            for sid in session_ids:
                # Get metadata for each session
                meta = await redis.hgetall(f"chat:{sid}:meta")
                if meta:
                    result.append(meta)

        # Sort by created timestamp, most recent first
        result.sort(key=lambda x: x.get("created", ""), reverse=True)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error retrieving sessions: {e}")
        return (
            jsonify(
                {
                    "error": f"Error retrieving sessions: {str(e)}",
                    "using_fallback": USING_FALLBACK,
                }
            ),
            500,
        )


@chat_blueprint.route("/api/chat/session/new", methods=["POST"])
async def create_session():
    """Create a new chat session."""
    user_id = await get_user_id_from_request()
    if not user_id:
        return jsonify({"error": "Authentication required"}), 401

    try:
        # Initialize Redis if needed
        if not redis and not USING_FALLBACK:
            await init_redis()

        # Generate new session ID
        session_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()

        # Create session metadata
        session_data = {
            "id": session_id,  # For React frontend
            "session_id": session_id,  # For compatibility
            "created": timestamp,
            "lastActivity": timestamp,  # For React frontend
            "name": "New Chat",  # For React frontend
            "topic": "New Chat",  # For compatibility
            "messages": [],  # Empty messages array
        }

        # Store session data based on storage availability
        if USING_FALLBACK:
            # Use in-memory fallback
            logger.info(
                f"Using in-memory fallback to create session for user: {user_id}"
            )
            # Initialize user's sessions list if it doesn't exist
            if user_id not in IN_MEMORY_STORAGE["sessions"]:
                IN_MEMORY_STORAGE["sessions"][user_id] = []

            # Store session ID in user's sessions
            IN_MEMORY_STORAGE["sessions"][user_id].append(session_id)

            # Store session metadata
            IN_MEMORY_STORAGE["metadata"][session_id] = session_data

            # Initialize empty messages list
            IN_MEMORY_STORAGE["messages"][session_id] = []
        else:
            # Use Redis
            await redis.sadd(f"user:{user_id}:sessions", session_id)
            await redis.hmset_dict(f"chat:{session_id}:meta", session_data)

        return jsonify({"session_id": session_id, "id": session_id})
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        return (
            jsonify(
                {
                    "error": f"Error creating session: {str(e)}",
                    "using_fallback": USING_FALLBACK,
                }
            ),
            500,
        )


@chat_blueprint.route("/api/chat/history/<session_id>", methods=["GET"])
async def get_history(session_id):
    """Get message history for a specific chat session."""
    user_id = await get_user_id_from_request()
    if not user_id:
        return jsonify({"error": "Authentication required"}), 401

    try:
        # Initialize Redis if needed
        if not redis and not USING_FALLBACK:
            await init_redis()

        # Initialize messages list
        messages = []

        # Use appropriate storage based on Redis availability
        if USING_FALLBACK:
            # Use in-memory fallback
            logger.info(
                f"Using in-memory fallback to get chat history for session: {session_id}"
            )

            # Verify session belongs to user
            user_sessions = IN_MEMORY_STORAGE["sessions"].get(user_id, [])
            if session_id not in user_sessions:
                return jsonify({"error": "Session not found or unauthorized"}), 403

            # Get messages from in-memory storage
            raw_messages = IN_MEMORY_STORAGE["messages"].get(session_id, [])

            for msg in raw_messages:
                # Messages in memory are already in the right format
                messages.append(msg)
        else:
            # Verify session belongs to user
            is_member = await redis.sismember(f"user:{user_id}:sessions", session_id)
            if not is_member:
                return jsonify({"error": "Session not found or unauthorized"}), 403

            # Get messages from Redis
            raw_messages = await redis.lrange(f"chat:{session_id}:messages", 0, -1)

            for msg_json in raw_messages:
                try:
                    msg = json.loads(msg_json)
                    # Convert to format expected by React frontend
                    if "user" in msg:
                        messages.append(
                            {
                                "sender": "user",
                                "text": msg["user"],
                                "timestamp": msg.get(
                                    "timestamp", datetime.utcnow().isoformat()
                                ),
                            }
                        )
                    elif "bot" in msg:
                        messages.append(
                            {
                                "sender": "grace",
                                "text": msg["bot"],
                                "timestamp": msg.get(
                                    "timestamp", datetime.utcnow().isoformat()
                                ),
                            }
                        )
                except json.JSONDecodeError:
                    logger.warning(f"Could not parse message JSON: {msg_json}")
                    continue

        # Sort messages by timestamp if available
        messages.sort(key=lambda x: x.get("timestamp", ""), reverse=False)

        return jsonify(messages)
    except Exception as e:
        logger.error(f"Error retrieving chat history: {e}")
        return (
            jsonify(
                {
                    "error": f"Error retrieving chat history: {str(e)}",
                    "using_fallback": USING_FALLBACK,
                }
            ),
            500,
        )


# Modify the existing chat message endpoint to work with sessions
async def handle_chat_message_with_session(user_id, message, session_id=None):
    """Process a chat message with session support."""
    try:
        # Initialize Redis if needed
        if not redis and not USING_FALLBACK:
            await init_redis()

        timestamp = datetime.utcnow().isoformat()

        # Create session if none provided
        if not session_id:
            session_id = str(uuid.uuid4())
            session_data = {
                "id": session_id,
                "session_id": session_id,
                "created": timestamp,
                "lastActivity": timestamp,
                "name": "New Chat",
                "topic": "New Chat",
                "messages": [],
            }

            # Store session data based on storage availability
            if USING_FALLBACK:
                # Use in-memory fallback
                logger.info(
                    f"Using in-memory fallback to create session for message from user: {user_id}"
                )
                # Initialize user's sessions list if it doesn't exist
                if user_id not in IN_MEMORY_STORAGE["sessions"]:
                    IN_MEMORY_STORAGE["sessions"][user_id] = []

                # Store session ID in user's sessions
                IN_MEMORY_STORAGE["sessions"][user_id].append(session_id)

                # Store session metadata
                IN_MEMORY_STORAGE["metadata"][session_id] = session_data

                # Initialize empty messages list
                IN_MEMORY_STORAGE["messages"][session_id] = []
            else:
                # Use Redis
                await redis.sadd(f"user:{user_id}:sessions", session_id)
                await redis.hmset_dict(f"chat:{session_id}:meta", session_data)

        # Create user message with appropriate format
        user_message = {"sender": "user", "text": message, "timestamp": timestamp}

        # For compatibility with existing API that expects user/bot format
        user_msg_data = {"user": message, "timestamp": timestamp}

        # Store user message based on storage availability
        if USING_FALLBACK:
            # Use in-memory fallback
            # Add message to session messages
            if session_id not in IN_MEMORY_STORAGE["messages"]:
                IN_MEMORY_STORAGE["messages"][session_id] = []

            IN_MEMORY_STORAGE["messages"][session_id].append(user_message)

            # Update session lastActivity
            if session_id in IN_MEMORY_STORAGE["metadata"]:
                IN_MEMORY_STORAGE["metadata"][session_id]["lastActivity"] = timestamp

                # Set topic if it's the first message
                topic = IN_MEMORY_STORAGE["metadata"][session_id].get("topic")
                if not topic or topic == "New Chat":
                    # Use first few words as topic
                    words = message.split()
                    new_topic = " ".join(words[:3]) + ("..." if len(words) > 3 else "")
                    IN_MEMORY_STORAGE["metadata"][session_id]["topic"] = new_topic
                    IN_MEMORY_STORAGE["metadata"][session_id][
                        "name"
                    ] = new_topic  # For React frontend
        else:
            # Use Redis
            # Store user message
            await redis.rpush(f"chat:{session_id}:messages", json.dumps(user_msg_data))

            # Update session last activity
            await redis.hset(f"chat:{session_id}:meta", "lastActivity", timestamp)

            # Set topic if it's the first message
            meta_key = f"chat:{session_id}:meta"
            topic = await redis.hget(meta_key, "topic")
            if not topic or topic == "New Chat":
                # Use first few words as topic
                words = message.split()
                new_topic = " ".join(words[:3]) + ("..." if len(words) > 3 else "")
                await redis.hset(meta_key, "topic", new_topic)
                await redis.hset(meta_key, "name", new_topic)  # For React frontend

        # We'll let the main process_chat_message handle the actual response generation
        return {"session_id": session_id, "using_fallback": USING_FALLBACK}
    except Exception as e:
        logger.error(f"Error in handle_chat_message_with_session: {e}")
        return {
            "error": str(e),
            "session_id": session_id,
            "using_fallback": USING_FALLBACK,
        }
