
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from uuid import uuid4
from datetime import datetime
import redis
import json

router = APIRouter()
r = redis.Redis(host="grace-redis", port=6379, decode_responses=True)

# User extraction placeholder
def get_user_id(request: Request):
    return request.headers.get("x-user-id") or "testuser"

class Message(BaseModel):
    message: str
    session_id: str

class NewSessionResponse(BaseModel):
    session_id: str

@router.post("/api/chat/session/new", response_model=NewSessionResponse)
def create_session(request: Request):
    user_id = get_user_id(request)
    session_id = str(uuid4())
    timestamp = datetime.utcnow().isoformat()
    session_data = {"session_id": session_id, "created": timestamp, "topic": "New Chat"}
    r.sadd(f"user:{user_id}:sessions", session_id)
    r.hset(f"chat:{session_id}:meta", mapping=session_data)
    return {"session_id": session_id}

@router.get("/api/chat/sessions")
def list_sessions(request: Request):
    user_id = get_user_id(request)
    ids = r.smembers(f"user:{user_id}:sessions")
    result = []
    for sid in ids:
        meta = r.hgetall(f"chat:{sid}:meta")
        if meta:
            result.append(meta)
    return sorted(result, key=lambda x: x.get("created", ""), reverse=True)

@router.get("/api/chat/history/{session_id}")
def get_history(session_id: str):
    raw = r.lrange(f"chat:{session_id}:messages", 0, -1)
    return [json.loads(m) for m in raw]

@router.post("/api/chat/message")
def handle_message(payload: Message, request: Request):
    user_id = get_user_id(request)
    session_id = payload.session_id
    user_msg = payload.message
    # Store user message
    r.rpush(f"chat:{session_id}:messages", json.dumps({"user": user_msg}))
    # Auto-generate response (placeholder)
    bot_msg = f"Echo: {user_msg}"
    r.rpush(f"chat:{session_id}:messages", json.dumps({"bot": bot_msg}))
    # Set topic if it's the first message
    meta_key = f"chat:{session_id}:meta"
    if not r.hexists(meta_key, "topic") or r.hget(meta_key, "topic") == "New Chat":
        r.hset(meta_key, "topic", user_msg[:32])
    return {"response": bot_msg}
