"""
Simplified API Server for testing authentication endpoints
"""

import json
import logging
import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import jwt
import shortuuid
from quart import Quart, request, jsonify
from quart_cors import cors

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("AuthTestServer")

# Initialize Quart app
app = Quart(__name__)
app = cors(app, allow_origin="*")

# JWT Configuration
JWT_SECRET = "dev_secret_key_replace_in_production"
JWT_EXPIRY = 3600 * 24  # 24 hours

# In-memory data stores - would be a database in production
users = {
    # Sample user for testing
    "test_user": {
        "username": "test_user",
        "email": "test@example.com",
        "password": "password123",  # In a real app, this would be hashed
        "user_id": "user_001",
        "created_at": datetime.utcnow().isoformat(),
        "profile": {"first_name": "Test", "last_name": "User"},
    }
}

# Active sessions - would be in Redis or another store in production
active_sessions = {}


def generate_jwt_token(user_id: str, expiry_seconds: int = JWT_EXPIRY) -> str:
    """Generate a JWT token for the given user_id."""
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(seconds=expiry_seconds),
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return token


def verify_jwt_token(token: str) -> Dict[str, Any]:
    """Verify a JWT token and check if session is active."""
    try:
        if not token:
            logger.warning("Empty token received")
            return {"success": False, "message": "Empty token"}

        if token not in active_sessions:
            logger.warning(f"Token not found in active sessions: {token[:10]}...")
            return {"success": False, "message": "Session not found or expired"}

        # Decode and verify token
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])

        # Check for required claims
        user_id = payload.get("user_id")
        if not user_id:
            logger.warning("Token missing user_id claim")
            return {"success": False, "message": "Invalid token format"}

        # Update last activity timestamp to keep session fresh
        active_sessions[token]["last_activity"] = datetime.utcnow().isoformat()

        return {
            "success": True,
            "user_id": user_id,
            "username": active_sessions[token].get("username"),
        }

    except jwt.ExpiredSignatureError:
        logger.warning(f"Expired token received: {token[:10]}...")
        if token in active_sessions:
            del active_sessions[token]
        return {"success": False, "message": "Token expired"}

    except jwt.InvalidTokenError as e:
        logger.error(f"Invalid token error: {e}")
        return {"success": False, "message": f"Invalid token: {str(e)}"}


async def get_token_from_request() -> Optional[str]:
    """Extract token from Authorization header."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    return auth_header[7:].strip()  # Remove 'Bearer ' prefix


@app.route("/")
async def index():
    """Root endpoint."""
    return jsonify(
        {
            "message": "Auth Test Server API is running",
            "status": "ok",
            "timestamp": datetime.utcnow().isoformat(),
        }
    )


@app.route("/api/auth/register", methods=["POST"])
async def register():
    """Handle user registration."""
    try:
        data = await request.get_json()
        if (
            not data
            or not data.get("username")
            or not data.get("email")
            or not data.get("password")
        ):
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Missing required fields: username, email, password",
                    }
                ),
                400,
            )

        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        # Check if username already exists
        if username in users:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": f"Username {username} is already taken",
                    }
                ),
                400,
            )

        # Create user (in a real app, you'd hash the password)
        user_id = shortuuid.uuid()
        users[username] = {
            "username": username,
            "email": email,
            "password": password,  # Should be hashed in production
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "profile": {},
        }

        # Generate token and create session
        token = generate_jwt_token(user_id)

        # Store session
        active_sessions[token] = {
            "user_id": user_id,
            "username": username,
            "created_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat(),
            "ip_address": request.remote_addr,
            "user_agent": request.headers.get("User-Agent", "Unknown"),
        }

        logger.info(f"User registered: {username} (user_id: {user_id})")

        return (
            jsonify(
                {
                    "success": True,
                    "token": token,
                    "user": {
                        "id": user_id,
                        "username": username,
                        "email": email,
                        "created_at": users[username]["created_at"],
                    },
                }
            ),
            201,
        )

    except Exception as e:
        logger.error(f"Error during registration: {str(e)}", exc_info=True)
        return (
            jsonify({"success": False, "message": f"Internal server error: {str(e)}"}),
            500,
        )


@app.route("/api/auth/login", methods=["POST"])
async def login():
    """Handle user login and session creation."""
    try:
        data = await request.get_json()
        if not data or not data.get("username") or not data.get("password"):
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Missing required fields: username, password",
                    }
                ),
                400,
            )

        username = data.get("username")
        password = data.get("password")
        remember_me = data.get("remember_me", False)

        # Authenticate user
        user = users.get(username)
        if not user or user.get("password") != password:
            return (
                jsonify({"success": False, "message": "Invalid username or password"}),
                401,
            )

        user_id = user.get("user_id")

        # Generate token with longer expiry for remember_me
        expiry = (
            JWT_EXPIRY * 30 if remember_me else JWT_EXPIRY
        )  # 30 days if remember_me
        token = generate_jwt_token(user_id, expiry)

        # Clean up existing sessions for this user if they have too many
        user_sessions = [
            t for t, s in active_sessions.items() if s.get("user_id") == user_id
        ]
        if len(user_sessions) > 5:  # Limit sessions per user
            # Sort by last activity, remove oldest
            sorted_sessions = sorted(
                user_sessions,
                key=lambda t: active_sessions[t].get("last_activity", "0"),
            )
            for old_token in sorted_sessions[:-5]:  # Keep 5 most recent
                if old_token in active_sessions:
                    del active_sessions[old_token]

        # Store session with comprehensive data
        active_sessions[token] = {
            "user_id": user_id,
            "username": username,
            "created_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat(),
            "ip_address": request.remote_addr,
            "user_agent": request.headers.get("User-Agent", "Unknown"),
            "remember_me": remember_me,
        }

        logger.info(f"User logged in: {username} (user_id: {user_id})")

        return jsonify(
            {
                "success": True,
                "token": token,
                "user": {
                    "id": user_id,
                    "username": username,
                    "email": user.get("email"),
                    "profile": user.get("profile", {}),
                },
            }
        )

    except Exception as e:
        logger.error(f"Error during login: {str(e)}", exc_info=True)
        return (
            jsonify({"success": False, "message": f"Internal server error: {str(e)}"}),
            500,
        )


@app.route("/api/auth/verify", methods=["GET"])
async def verify_token_endpoint():
    """Verify a token and return user info if valid."""
    token = await get_token_from_request()
    if not token:
        return jsonify({"success": False, "message": "No token provided"}), 401

    verification = verify_jwt_token(token)
    if not verification.get("success"):
        return jsonify(verification), 401

    user_id = verification.get("user_id")
    username = verification.get("username")

    # Find user by user_id
    user = None
    for u in users.values():
        if u.get("user_id") == user_id:
            user = u
            break

    if not user:
        logger.warning(f"User not found for verified token: {user_id}")
        return jsonify({"success": False, "message": "User not found"}), 404

    # Get session data
    session_data = active_sessions.get(token, {})

    return jsonify(
        {
            "success": True,
            "user": {
                "id": user_id,
                "username": user.get("username"),
                "email": user.get("email"),
                "profile": user.get("profile", {}),
            },
            "session": {
                "created_at": session_data.get("created_at"),
                "last_activity": session_data.get("last_activity"),
                "ip_address": session_data.get("ip_address"),
                "user_agent": session_data.get("user_agent"),
            },
        }
    )


@app.route("/api/auth/logout", methods=["POST"])
async def logout():
    """Handle user logout and session cleanup."""
    token = await get_token_from_request()
    if not token:
        return jsonify({"success": False, "message": "No token provided"}), 401

    if token not in active_sessions:
        return (
            jsonify(
                {"success": False, "message": "Session not found or already expired"}
            ),
            404,
        )

    # Get user_id before deleting session
    user_id = active_sessions[token].get("user_id")
    username = active_sessions[token].get("username")

    # Find and remove all sessions for this user
    sessions_removed = 0
    sessions_to_remove = [
        t for t, s in active_sessions.items() if s.get("user_id") == user_id
    ]
    for t in sessions_to_remove:
        del active_sessions[t]
        sessions_removed += 1

    logger.info(
        f"User logged out: {username} (user_id: {user_id}, sessions removed: {sessions_removed})"
    )

    return jsonify(
        {
            "success": True,
            "message": "Logged out successfully",
            "sessions_removed": sessions_removed,
        }
    )


if __name__ == "__main__":
    logger.info("Starting Auth Test Server...")
    logger.info(f"Preloaded test user: 'test_user' with password 'password123'")
    app.run(host="0.0.0.0", port=8000)
