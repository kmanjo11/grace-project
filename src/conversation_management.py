"""
Conversation Management System for Grace - A crypto trading application based on Open Interpreter

This module implements a sophisticated conversation management system with:
- Data searches and background/trade facilitation tasks
- Session-based agent interactions
- Context preservation across conversations
- Memory-augmented responses
- Topic tracking and active context management
"""

import os
import json
import time
import uuid
import logging
import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from collections import deque

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("GraceConversation")

class ConversationContext:
    """
    Represents the context of a conversation, including topics, entities, and state.
    """
    
    def __init__(self, user_id: str, session_id: str, max_history: int = 20):
        """
        Initialize a conversation context.
        
        Args:
            user_id: User ID
            session_id: Session ID
            max_history: Maximum number of messages to keep in history
        """
        self.user_id = user_id
        self.session_id = session_id
        self.created_at = time.time()
        self.last_updated = time.time()
        self.history = deque(maxlen=max_history)
        self.active_topics = []
        self.entities = {}
        self.background_tasks = {}
        self.state = "active"
        self.context_id = str(uuid.uuid4())
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Add a message to the conversation history.
        
        Args:
            role: Message role (user or assistant)
            content: Message content
            metadata: Additional metadata
        """
        if metadata is None:
            metadata = {}
            
        message = {
            "role": role,
            "content": content,
            "timestamp": time.time(),
            "metadata": metadata
        }
        
        self.history.append(message)
        self.last_updated = time.time()
    
    def add_topic(self, topic: str, confidence: float = 1.0):
        """
        Add a topic to the active topics list.
        
        Args:
            topic: Topic name
            confidence: Confidence score (0-1)
        """
        # Check if topic already exists
        for existing_topic in self.active_topics:
            if existing_topic["name"] == topic:
                # Update confidence if higher
                if confidence > existing_topic["confidence"]:
                    existing_topic["confidence"] = confidence
                    existing_topic["last_mentioned"] = time.time()
                return
        
        # Add new topic
        self.active_topics.append({
            "name": topic,
            "confidence": confidence,
            "first_mentioned": time.time(),
            "last_mentioned": time.time()
        })
        
        # Sort topics by confidence
        self.active_topics.sort(key=lambda x: x["confidence"], reverse=True)
    
    def update_topic(self, topic: str, confidence: float = None):
        """
        Update a topic's last mentioned time and optionally confidence.
        
        Args:
            topic: Topic name
            confidence: New confidence score (optional)
        """
        for existing_topic in self.active_topics:
            if existing_topic["name"] == topic:
                existing_topic["last_mentioned"] = time.time()
                if confidence is not None:
                    existing_topic["confidence"] = confidence
                return
    
    def add_entity(self, entity: str, entity_type: str, value: Any, confidence: float = 1.0):
        """
        Add an entity to the context.
        
        Args:
            entity: Entity name
            entity_type: Entity type
            value: Entity value
            confidence: Confidence score (0-1)
        """
        if entity not in self.entities:
            self.entities[entity] = {
                "type": entity_type,
                "value": value,
                "confidence": confidence,
                "first_mentioned": time.time(),
                "last_mentioned": time.time()
            }
        else:
            # Update existing entity
            self.entities[entity]["last_mentioned"] = time.time()
            if confidence > self.entities[entity]["confidence"]:
                self.entities[entity]["value"] = value
                self.entities[entity]["confidence"] = confidence
    
    def add_background_task(self, task_id: str, task_type: str, status: str = "pending", data: Any = None):
        """
        Add a background task to the context.
        
        Args:
            task_id: Task ID
            task_type: Task type
            status: Task status
            data: Task data
        """
        self.background_tasks[task_id] = {
            "type": task_type,
            "status": status,
            "created_at": time.time(),
            "updated_at": time.time(),
            "data": data
        }
    
    def update_background_task(self, task_id: str, status: str, data: Any = None):
        """
        Update a background task's status and data.
        
        Args:
            task_id: Task ID
            status: New status
            data: New data (optional)
        """
        if task_id in self.background_tasks:
            self.background_tasks[task_id]["status"] = status
            self.background_tasks[task_id]["updated_at"] = time.time()
            if data is not None:
                self.background_tasks[task_id]["data"] = data
    
    def get_recent_messages(self, count: int = 5) -> List[Dict[str, Any]]:
        """
        Get the most recent messages from the conversation history.
        
        Args:
            count: Number of messages to retrieve
            
        Returns:
            List: Recent messages
        """
        return list(self.history)[-count:]
    
    def get_active_topics(self, count: int = 3) -> List[Dict[str, Any]]:
        """
        Get the most active topics.
        
        Args:
            count: Number of topics to retrieve
            
        Returns:
            List: Active topics
        """
        # Sort by last mentioned time and confidence
        sorted_topics = sorted(
            self.active_topics,
            key=lambda x: (time.time() - x["last_mentioned"], -x["confidence"])
        )
        return sorted_topics[:count]
    
    def get_relevant_entities(self, topic: Optional[str] = None) -> Dict[str, Any]:
        """
        Get entities relevant to a topic or all entities if no topic specified.
        
        Args:
            topic: Topic to filter by (optional)
            
        Returns:
            Dict: Relevant entities
        """
        if topic is None:
            return self.entities
        
        # Simple relevance check - in a real system, this would be more sophisticated
        relevant_entities = {}
        for entity, entity_data in self.entities.items():
            if topic.lower() in entity.lower() or entity.lower() in topic.lower():
                relevant_entities[entity] = entity_data
        
        return relevant_entities
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the context to a dictionary for serialization.
        
        Returns:
            Dict: Context as dictionary
        """
        return {
            "context_id": self.context_id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "created_at": self.created_at,
            "last_updated": self.last_updated,
            "history": list(self.history),
            "active_topics": self.active_topics,
            "entities": self.entities,
            "background_tasks": self.background_tasks,
            "state": self.state
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationContext':
        """
        Create a context from a dictionary.
        
        Args:
            data: Dictionary data
            
        Returns:
            ConversationContext: Created context
        """
        context = cls(data["user_id"], data["session_id"])
        context.context_id = data["context_id"]
        context.created_at = data["created_at"]
        context.last_updated = data["last_updated"]
        context.history = deque(data["history"], maxlen=context.history.maxlen)
        context.active_topics = data["active_topics"]
        context.entities = data["entities"]
        context.background_tasks = data["background_tasks"]
        context.state = data["state"]
        return context


class TopicDetector:
    """
    Detects topics in conversation messages.
    """
    
    def __init__(self):
        """
        Initialize the topic detector.
        """
        self.logger = logging.getLogger("GraceTopicDetector")
    
    async def detect_topics(self, message: str) -> List[Dict[str, Any]]:
        """
        Detect topics in a message.
        
        Args:
            message: Message content
            
        Returns:
            List: Detected topics with confidence scores
        """
        # This is a simplified implementation
        # In a production system, you would use NLP techniques or an LLM
        
        # Define some common crypto-related topics
        crypto_topics = {
            "bitcoin": ["bitcoin", "btc", "satoshi"],
            "ethereum": ["ethereum", "eth", "vitalik", "smart contract"],
            "solana": ["solana", "sol", "phantom"],
            "trading": ["trade", "trading", "buy", "sell", "price", "market"],
            "wallet": ["wallet", "address", "key", "seed phrase"],
            "liquidity": ["liquidity", "pool", "swap", "amm"],
            "defi": ["defi", "yield", "farm", "stake", "lending"]
        }
        
        # Check for topics in message
        detected_topics = []
        message_lower = message.lower()
        
        for topic, keywords in crypto_topics.items():
            for keyword in keywords:
                if keyword in message_lower:
                    # Calculate a simple confidence score based on keyword prominence
                    confidence = 0.5
                    if keyword in message_lower.split():  # Exact word match
                        confidence = 0.8
                    if message_lower.count(keyword) > 1:  # Multiple mentions
                        confidence = min(confidence + 0.1 * message_lower.count(keyword), 1.0)
                    
                    detected_topics.append({
                        "name": topic,
                        "confidence": confidence
                    })
                    break  # Only add topic once
        
        return detected_topics


class EntityExtractor:
    """
    Extracts entities from conversation messages.
    """
    
    def __init__(self):
        """
        Initialize the entity extractor.
        """
        self.logger = logging.getLogger("GraceEntityExtractor")
    
    async def extract_entities(self, message: str) -> List[Dict[str, Any]]:
        """
        Extract entities from a message.
        
        Args:
            message: Message content
            
        Returns:
            List: Extracted entities
        """
        # This is a simplified implementation
        # In a production system, you would use NER or an LLM
        
        entities = []
        
        # Simple regex-like patterns for common crypto entities
        # In a real system, these would be more sophisticated
        
        # Check for crypto symbols
        crypto_symbols = {
            "BTC": "Bitcoin",
            "ETH": "Ethereum",
            "SOL": "Solana",
            "USDT": "Tether",
            "USDC": "USD Coin"
        }
        
        words = message.split()
        for word in words:
            clean_word = word.strip(".,!?;:()[]{}\"'").upper()
            if clean_word in crypto_symbols:
                entities.append({
                    "entity": clean_word,
                    "type": "crypto_symbol",
                    "value": crypto_symbols[clean_word],
                    "confidence": 0.9
                })
        
        # Check for wallet addresses (simplified)
        # In a real system, you would use proper validation
        for word in words:
            if len(word) > 30 and (word.startswith("0x") or word.startswith("1") or word.startswith("3")):
                entities.append({
                    "entity": word,
                    "type": "wallet_address",
                    "value": word,
                    "confidence": 0.7
                })
        
        # Check for amounts
        import re
        amount_pattern = r'\b(\d+(\.\d+)?)\s*(btc|eth|sol|usdt|usdc)\b'
        matches = re.finditer(amount_pattern, message.lower())
        for match in matches:
            amount = float(match.group(1))
            currency = match.group(3).upper()
            entities.append({
                "entity": f"{amount} {currency}",
                "type": "crypto_amount",
                "value": {
                    "amount": amount,
                    "currency": currency
                },
                "confidence": 0.8
            })
        
        return entities


class BackgroundTaskManager:
    """
    Manages background tasks for data searches and trade facilitation.
    """
    
    def __init__(self):
        """
        Initialize the background task manager.
        """
        self.tasks = {}
        self.logger = logging.getLogger("GraceBackgroundTask")
        self._lock = asyncio.Lock()
    
    async def create_task(self, task_type: str, params: Dict[str, Any]) -> str:
        """
        Create a new background task.
        
        Args:
            task_type: Type of task
            params: Task parameters
            
        Returns:
            str: Task ID
        """
        task_id = str(uuid.uuid4())
        
        task = {
            "id": task_id,
            "type": task_type,
            "params": params,
            "status": "pending",
            "created_at": time.time(),
            "updated_at": time.time(),
            "result": None,
            "error": None
        }
        
        async with self._lock:
            self.tasks[task_id] = task
        
        # Start task execution
        asyncio.create_task(self._execute_task(task_id))
        
        return task_id
    
    async def get_task(self, task_id: str) -> Dict[str, Any]:
        """
        Get a task by ID.
        
        Args:
            task_id: Task ID
            
        Returns:
            Dict: Task data
        """
        if task_id not in self.tasks:
            return None
        
        return self.tasks[task_id]
    
    async def _execute_task(self, task_id: str):
        """
        Execute a background task.
        
        Args:
            task_id: Task ID
        """
        if task_id not in self.tasks:
            return
        
        task = self.tasks[task_id]
        
        try:
            # Update status to running
            async with self._lock:
                task["status"] = "running"
                task["updated_at"] = time.time()
            
            # Execute task based on type
            if task["type"] == "data_search":
                result = await self._execute_data_search(task["params"])
            elif task["type"] == "price_check":
                result = await self._execute_price_check(task["params"])
            elif task["type"] == "trade_preparation":
                result = await self._execute_trade_preparation(task["params"])
            else:
                raise ValueError(f"Unknown task type: {task['type']}")
            
            # Update task with result
            async with self._lock:
                task["status"] = "completed"
                task["result"] = result
                task["updated_at"] = time.time()
            
            self.logger.info(f"Task {task_id} completed successfully")
            
        except Exception as e:
            self.logger.error(f"Error executing task {task_id}: {str(e)}")
            
            # Update task with error
            async with self._lock:
                task["status"] = "failed"
                task["error"] = str(e)
                task["updated_at"] = time.time()
    
    async def _execute_data_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a data search task.
        
        Args:
            params: Task parameters
            
        Returns:
            Dict: Search results
        """
        # Simulate a data search
        await asyncio.sleep(2)  # Simulate network delay
        
        query = params.get("query", "")
        
        # Mock results
        results = {
            "query": query,
            "timestamp": time.time(),
            "results": [
                {
                    "title": f"Information about {query}",
                    "snippet": f"This is some information about {query} that was found in the search.",
                    "source": "mock_search_engine"
                },
                {
                    "title": f"Latest news on {query}",
                    "snippet": f"Recent developments related to {query} in the crypto market.",
                    "source": "mock_news_api"
                }
            ]
        }
        
        return results
    
    async def _execute_price_check(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a price check task.
        
        Args:
            params: Task parameters
            
        Returns:
            Dict: Price data
        """
        # Simulate a price check
        await asyncio.sleep(1)  # Simulate network delay
        
        symbol = params.get("symbol", "BTC")
        
        # Mock price data
        import random
        price = random.uniform(10, 50000)  # Random price based on typical ranges
        
        if symbol == "BTC":
            price = random.uniform(30000, 50000)
        elif symbol == "ETH":
            price = random.uniform(1500, 3000)
        elif symbol == "SOL":
            price = random.uniform(50, 150)
        
        price_data = {
            "symbol": symbol,
            "price": price,
            "currency": "USD",
            "timestamp": time.time(),
            "source": "mock_price_api"
        }
        
        return price_data
    
    async def _execute_trade_preparation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a trade preparation task.
        
        Args:
            params: Task parameters
            
        Returns:
            Dict: Trade preparation data
        """
        # Simulate trade preparation
        await asyncio.sleep(3)  # Simulate complex calculation
        
        symbol = params.get("symbol", "BTC")
        amount = params.get("amount", 0.1)
        action = params.get("action", "buy")
        
        # Mock price and fee calculation
        import random
        price = random.uniform(10, 50000)  # Random price based on typical ranges
        
        if symbol == "BTC":
            price = random.uniform(30000, 50000)
        elif symbol == "ETH":
            price = random.uniform(1500, 3000)
        elif symbol == "SOL":
            price = random.uniform(50, 150)
        
        total_value = price * amount
        fee = total_value * 0.001  # 0.1% fee
        
        trade_data = {
            "symbol": symbol,
            "amount": amount,
            "action": action,
            "price": price,
            "total_value": total_value,
            "fee": fee,
            "estimated_total": total_value + fee if action == "buy" else total_value - fee,
            "timestamp": time.time()
        }
        
        return trade_data


class ConversationManager:
    """Manages conversations and their contexts with enhanced state persistence."""
    
    def __init__(self, storage_dir: str = "./conversation_data", max_contexts_per_user: int = 10):
        """
        Initialize the conversation manager with improved state handling.
        
        Args:
            storage_dir: Directory to store conversation data
            max_contexts_per_user: Maximum number of active contexts per user
        """
        self.storage_dir = storage_dir
        self.max_contexts_per_user = max_contexts_per_user
        self.topic_detector = TopicDetector()
        self.entity_extractor = EntityExtractor()
        self.background_task_manager = BackgroundTaskManager()
        self.active_contexts = {}  # user_id -> {context_id -> context}
        self.context_locks = {}  # context_id -> lock
        self.pending_operations = {}  # Track operations in progress
        self._shutdown_requested = False
        self._state_ready = False  # Flag to track if state is ready
        
        # Create storage directory if it doesn't exist
        os.makedirs(storage_dir, exist_ok=True)
        os.makedirs(os.path.join(storage_dir, "contexts"), exist_ok=True)
        os.makedirs(os.path.join(storage_dir, "sessions"), exist_ok=True)
        
        # Create a directory for state snapshots and recovery
        os.makedirs(os.path.join(storage_dir, "snapshots"), exist_ok=True)
        
        self.logger = logging.getLogger("GraceConversationManager")
        
        # Start background task for periodic state saving
        self._start_periodic_state_persistence()
        
        # Load any existing contexts
        self._load_existing_contexts()
        
        # Mark state as ready
        self._state_ready = True
        self._lock = asyncio.Lock()
    
    async def create_context(self, user_id: str, session_id: str) -> ConversationContext:
        """
        Create a new conversation context with state consistency checks.
        
        Args:
            user_id: User ID
            session_id: Session ID
            
        Returns:
            ConversationContext: Created context
        """
        # Wait for state to be ready before creating new contexts
        if not self._state_ready:
            self.logger.warning("Creating context before state is fully ready")
        
        # Create the context
        context = ConversationContext(user_id, session_id)
        context_id = context.context_id
        
        # Initialize a lock for this context
        self.context_locks[context_id] = asyncio.Lock()
        
        # Store in active contexts with proper initialization
        if user_id not in self.active_contexts:
            self.active_contexts[user_id] = {}
        self.active_contexts[user_id][context_id] = context
        
        # Schedule an async save
        asyncio.create_task(self._async_save_new_context(context))
        
        return context
    
    async def load_context(self, context_id: str) -> Optional[ConversationContext]:
        """
        Load a conversation context from disk with improved error handling and recovery.
        
        Args:
            context_id: Context ID to load
            
        Returns:
            ConversationContext: Loaded context or None if not found
        """
        if not self._state_ready:
            self.logger.warning("Attempted to load context before state is ready")
            await self._wait_for_state_ready()
        
        # Set operation as pending
        operation_id = str(uuid.uuid4())
        self.pending_operations[operation_id] = {
            "type": "load",
            "context_id": context_id,
            "start_time": time.time()
        }
        
        try:
            # Define the context paths - primary and recovery locations
            context_path = os.path.join(self.storage_dir, "contexts", f"{context_id}.json")
            snapshot_path = os.path.join(self.storage_dir, "snapshots", f"{context_id}.json")
            
            # Try the primary path first
            if os.path.exists(context_path):
                try:
                    with open(context_path, 'r') as f:
                        context_data = json.load(f)
                        context = ConversationContext.from_dict(context_data)
                        
                        # Add to active contexts if not already there
                        if context.user_id not in self.active_contexts:
                            self.active_contexts[context.user_id] = {}
                        self.active_contexts[context.user_id][context_id] = context
                        
                        self.logger.debug(f"Loaded context {context_id} from primary storage")
                        return context
                except json.JSONDecodeError:
                    self.logger.warning(f"JSON decode error for {context_id}, trying recovery snapshot")
                except Exception as e:
                    self.logger.error(f"Error loading context {context_id} from primary: {str(e)}")
            
            # If primary failed or doesn't exist, try the snapshot
            if os.path.exists(snapshot_path):
                try:
                    with open(snapshot_path, 'r') as f:
                        snapshot_data = json.load(f)
                        context = ConversationContext.from_dict(snapshot_data)
                        
                        # Add to active contexts
                        if context.user_id not in self.active_contexts:
                            self.active_contexts[context.user_id] = {}
                        self.active_contexts[context.user_id][context_id] = context
                        
                        # Save to primary path (repair)
                        await self.save_context(context)
                        
                        self.logger.info(f"Recovered context {context_id} from snapshot")
                        return context
                except Exception as e:
                    self.logger.error(f"Error loading context {context_id} from snapshot: {str(e)}")
            
            self.logger.warning(f"Context {context_id} not found in any storage location")
            return None
        finally:
            # Remove the pending operation
            if operation_id in self.pending_operations:
                del self.pending_operations[operation_id]
    
    async def get_context(self, context_id: str, user_id: str) -> Optional[ConversationContext]:
        """
        Get a conversation context.
        
        Args:
            context_id: Context ID
            user_id: User ID
            
        Returns:
            ConversationContext: Context if found, None otherwise
        """
        # Check active contexts
        if user_id in self.active_contexts and context_id in self.active_contexts[user_id]:
            return self.active_contexts[user_id][context_id]
        
        # Check stored contexts
        try:
            context_file = os.path.join(self.storage_dir, f"{user_id}_{context_id}.json")
            if os.path.exists(context_file):
                with open(context_file, "r") as f:
                    context_data = json.load(f)
                
                context = ConversationContext.from_dict(context_data)
                
                # Add to active contexts
                async with self._lock:
                    if user_id not in self.active_contexts:
                        self.active_contexts[user_id] = {}
                    
                    self.active_contexts[user_id][context_id] = context
                
                return context
        except Exception as e:
            self.logger.error(f"Error loading context {context_id}: {str(e)}")
        
        return None
    
    async def get_or_create_context(self, user_id: str, session_id: str) -> ConversationContext:
        """
        Get an existing context for a session or create a new one.
        
        Args:
            user_id: User ID
            session_id: Session ID
            
        Returns:
            ConversationContext: Context
        """
        # Check if there's an active context for this session
        if user_id in self.active_contexts:
            for context_id, context in self.active_contexts[user_id].items():
                if context.session_id == session_id and context.state == "active":
                    return context
        
        # Create new context
        return await self.create_context(user_id, session_id)
    
    async def save_context(self, context: ConversationContext):
        """
        Save conversation context to disk with improved error handling and atomic writes.
        
        Args:
            context: Conversation context to save
        """
        if not self._state_ready:
            self.logger.warning("Attempted to save context before state is ready")
            return
            
        # Generate paths for context and session files
        context_path = os.path.join(self.storage_dir, "contexts", f"{context.context_id}.json")
        session_path = os.path.join(self.storage_dir, "sessions", f"{context.session_id}.json")
        
        # Create temporary files for atomic writes
        temp_context_path = f"{context_path}.tmp"
        temp_session_path = f"{session_path}.tmp"
        
        # Acquire a lock for this context if needed
        context_lock = self.context_locks.setdefault(context.context_id, asyncio.Lock())
        
        # Set operation as pending to prevent race conditions
        operation_id = str(uuid.uuid4())
        self.pending_operations[operation_id] = {
            "type": "save",
            "context_id": context.context_id,
            "session_id": context.session_id,
            "start_time": time.time()
        }
        
        try:
            async with context_lock:
                # Update last_updated time
                context.last_updated = time.time()
                
                # Prepare context data
                context_data = context.to_dict()
                
                # Create session metadata
                session_data = {
                    "user_id": context.user_id,
                    "session_id": context.session_id,
                    "context_id": context.context_id,
                    "created_at": context.created_at,
                    "last_updated": context.last_updated,
                    "state": context.state,
                    "active_topics": [topic["name"] for topic in context.active_topics[:3]],
                    "message_count": len(context.history)
                }
                
                # Write to temporary files first (atomic write pattern)
                try:
                    with open(temp_context_path, 'w') as f:
                        json.dump(context_data, f, indent=2)
                        
                    with open(temp_session_path, 'w') as f:
                        json.dump(session_data, f, indent=2)
                    
                    # Now rename the temp files to the actual files (atomic operation)
                    os.replace(temp_context_path, context_path)
                    os.replace(temp_session_path, session_path)
                    
                    # Also save a snapshot for recovery purposes
                    await self._save_state_snapshot(context)
                    
                    self.logger.debug(f"Saved context {context.context_id} for session {context.session_id}")
                except Exception as e:
                    self.logger.error(f"Error during context save: {str(e)}")
                    # Clean up temporary files if they exist
                    for temp_file in [temp_context_path, temp_session_path]:
                        if os.path.exists(temp_file):
                            try:
                                os.remove(temp_file)
                            except:
                                pass
                    raise
        except Exception as e:
            self.logger.error(f"Error saving context: {str(e)}")
            raise
        finally:
            # Remove the pending operation
            if operation_id in self.pending_operations:
                del self.pending_operations[operation_id]
    
    async def process_message(
        self,
        context_id: str,
        user_id: str,
        message: str,
        role: str = "user",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a message in a conversation context.
        
        Args:
            context_id: Context ID
            user_id: User ID
            message: Message content
            role: Message role
            metadata: Additional metadata
            
        Returns:
            Dict: Processing result
        """
        # Get context
        context = await self.get_context(context_id, user_id)
        
        if not context:
            return {"success": False, "error": "Context not found"}
        
        # Add message to context
        context.add_message(role, message, metadata)
        
        # Process message content
        processing_result = {
            "topics": [],
            "entities": [],
            "background_tasks": []
        }
        
        # Detect topics
        if role == "user":  # Only process user messages
            topics = await self.topic_detector.detect_topics(message)
            for topic in topics:
                context.add_topic(topic["name"], topic["confidence"])
                processing_result["topics"].append(topic)
            
            # Extract entities
            entities = await self.entity_extractor.extract_entities(message)
            for entity in entities:
                context.add_entity(
                    entity["entity"],
                    entity["type"],
                    entity["value"],
                    entity["confidence"]
                )
                processing_result["entities"].append(entity)
            
            # Check for potential background tasks
            background_tasks = await self._identify_background_tasks(message, entities)
            for task in background_tasks:
                task_id = await self.background_task_manager.create_task(
                    task["type"],
                    task["params"]
                )
                context.add_background_task(task_id, task["type"])
                processing_result["background_tasks"].append({
                    "task_id": task_id,
                    "type": task["type"]
                })
        
        # Save context
        await self.save_context(context)
        
        return {
            "success": True,
            "context_id": context_id,
            "processing_result": processing_result
        }
    
    async def generate_context_aware_prompt(
        self,
        context_id: str,
        user_id: str,
        query: str
    ) -> Dict[str, Any]:
        """
        Generate a context-aware prompt for the LLM.
        
        Args:
            context_id: Context ID
            user_id: User ID
            query: User query
            
        Returns:
            Dict: Prompt data
        """
        # Get context
        context = await self.get_context(context_id, user_id)
        
        if not context:
            return {"success": False, "error": "Context not found"}
        
        # Get recent messages
        recent_messages = context.get_recent_messages()
        
        # Get active topics
        active_topics = context.get_active_topics()
        
        # Get relevant entities
        relevant_entities = {}
        for topic in active_topics:
            topic_entities = context.get_relevant_entities(topic["name"])
            relevant_entities.update(topic_entities)
        
        # Check for completed background tasks
        completed_tasks = []
        for task_id, task_data in context.background_tasks.items():
            if task_data["status"] != "completed":
                # Update task status from background task manager
                bg_task = await self.background_task_manager.get_task(task_id)
                if bg_task and bg_task["status"] == "completed":
                    context.update_background_task(task_id, "completed", bg_task["result"])
                    completed_tasks.append({
                        "task_id": task_id,
                        "type": task_data["type"],
                        "result": bg_task["result"]
                    })
        
        # Construct context information
        context_info = {
            "active_topics": active_topics,
            "relevant_entities": relevant_entities,
            "completed_tasks": completed_tasks
        }
        
        # Construct prompt enhancement
        prompt_enhancement = self._format_context_for_prompt(context_info)
        
        # Save updated context
        await self.save_context(context)
        
        return {
            "success": True,
            "context_id": context_id,
            "conversation_history": recent_messages,
            "context_info": context_info,
            "prompt_enhancement": prompt_enhancement
        }
    
    def _format_context_for_prompt(self, context_info: Dict[str, Any]) -> str:
        """
        Format context information for inclusion in a prompt.
        
        Args:
            context_info: Context information
            
        Returns:
            str: Formatted context
        """
        prompt_parts = ["### Context Information:"]
        
        # Add topics
        if context_info["active_topics"]:
            prompt_parts.append("\nCurrent topics of conversation:")
            for topic in context_info["active_topics"]:
                prompt_parts.append(f"- {topic['name']}")
        
        # Add entities
        if context_info["relevant_entities"]:
            prompt_parts.append("\nRelevant entities mentioned:")
            for entity, entity_data in context_info["relevant_entities"].items():
                prompt_parts.append(f"- {entity} ({entity_data['type']})")
        
        # Add task results
        if context_info["completed_tasks"]:
            prompt_parts.append("\nBackground information:")
            for task in context_info["completed_tasks"]:
                if task["type"] == "price_check" and "result" in task:
                    result = task["result"]
                    prompt_parts.append(f"- Current price of {result['symbol']}: ${result['price']:.2f} USD")
                elif task["type"] == "data_search" and "result" in task:
                    result = task["result"]
                    prompt_parts.append(f"- Search results for '{result['query']}':")
                    for item in result["results"]:
                        prompt_parts.append(f"  * {item['title']}: {item['snippet']}")
                elif task["type"] == "trade_preparation" and "result" in task:
                    result = task["result"]
                    prompt_parts.append(
                        f"- Trade preparation for {result['action']} {result['amount']} {result['symbol']}:"
                    )
                    prompt_parts.append(f"  * Price: ${result['price']:.2f}")
                    prompt_parts.append(f"  * Total value: ${result['total_value']:.2f}")
                    prompt_parts.append(f"  * Fee: ${result['fee']:.2f}")
                    prompt_parts.append(f"  * Estimated total: ${result['estimated_total']:.2f}")
        
        prompt_parts.append("\n### End of Context Information")
        
        return "\n".join(prompt_parts)
    
    async def _identify_background_tasks(
        self,
        message: str,
        entities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Identify potential background tasks from a message.
        
        Args:
            message: Message content
            entities: Extracted entities
            
        Returns:
            List: Potential background tasks
        """
        tasks = []
        message_lower = message.lower()
        
        # Check for price check requests
        price_keywords = ["price", "how much", "worth", "value", "cost"]
        if any(keyword in message_lower for keyword in price_keywords):
            # Look for crypto symbols in entities
            for entity in entities:
                if entity["type"] == "crypto_symbol":
                    tasks.append({
                        "type": "price_check",
                        "params": {
                            "symbol": entity["entity"]
                        }
                    })
        
        # Check for data search requests
        search_keywords = ["search", "find", "look up", "information", "news", "what is"]
        if any(keyword in message_lower for keyword in search_keywords):
            # Extract potential search query
            # This is simplified - in a real system, you would use NLP
            search_query = message
            for keyword in search_keywords:
                if keyword in message_lower:
                    parts = message.split(keyword, 1)
                    if len(parts) > 1:
                        search_query = parts[1].strip()
                        break
            
            tasks.append({
                "type": "data_search",
                "params": {
                    "query": search_query
                }
            })
        
        # Check for trade preparation requests
        trade_keywords = ["trade", "buy", "sell", "swap"]
        if any(keyword in message_lower for keyword in trade_keywords):
            # Look for crypto amounts in entities
            for entity in entities:
                if entity["type"] == "crypto_amount":
                    action = "buy"
                    if "sell" in message_lower:
                        action = "sell"
                    
                    tasks.append({
                        "type": "trade_preparation",
                        "params": {
                            "symbol": entity["value"]["currency"],
                            "amount": entity["value"]["amount"],
                            "action": action
                        }
                    })
        
        return tasks
    
    def process_task(self, task_content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a task from the agent framework.
        
        Args:
            task_content: Task content and parameters
            
        Returns:
            Dict[str, Any]: Task result
        """
        task_type = task_content.get("type")
        logger.info(f"Processing conversation task of type: {task_type}")
        
        if task_type == "process_message":
            message = task_content.get("message")
            user_id = task_content.get("user_id")
            session_id = task_content.get("session_id", str(uuid.uuid4()))
            context = task_content.get("context", {})
            
            if not message:
                logger.error("Message is required for processing")
                return {"status": "error", "message": "Message is required"}
                
            if not user_id:
                logger.error("User ID is required for processing")
                return {"status": "error", "message": "User ID is required"}
            
            # Extract entities and topics
            entities = self.entity_extractor.extract_entities(message)
            topics = self.topic_detector.detect_topics(message)
            
            # Identify potential background tasks
            background_tasks = self.background_task_manager.identify_tasks(message, entities)
            
            # Generate a response using context information
            system_message = context.get("system_message", "You are Grace, a helpful AI assistant.")
            memories = context.get("memories", [])
            conversation_context = context.get("conversation_context", {})
            
            # Build response context
            response_context = {
                "entities": entities,
                "topics": topics,
                "background_tasks": background_tasks,
                "memories": memories,
                "conversation_history": conversation_context.get("conversation_history", [])
            }
            
            # Generate a response based on the available context
            # In a real implementation, this would use an LLM or other AI system
            # For now, we'll return a placeholder response
            response = f"I've processed your message about {', '.join([t['name'] for t in topics[:2]])} and understand your request."
            
            if memories:
                response += f" I recall our previous discussions about this topic."
            
            if background_tasks:
                response += f" I'll help you with the {len(background_tasks)} tasks you've requested."
            
            return {
                "status": "success",
                "response": response,
                "context": response_context,
                "entities": entities,
                "topics": topics,
                "background_tasks": background_tasks
            }
        
        return {"status": "error", "message": f"Unknown task type: {task_type}"}
    
    async def _prune_old_contexts(self, user_id: str):
        """
        Prune old contexts for a user.
        
        Args:
            user_id: User ID
        """
        if user_id not in self.active_contexts:
            return
        
        # Check if we need to prune
        if len(self.active_contexts[user_id]) <= self.max_contexts_per_user:
            return
        
        # Sort contexts by last updated time
        sorted_contexts = sorted(
            self.active_contexts[user_id].items(),
            key=lambda x: x[1].last_updated
        )
        
        # Prune oldest contexts
        contexts_to_prune = sorted_contexts[:-self.max_contexts_per_user]
        
        for context_id, context in contexts_to_prune:
            # Save context before removing
            await self.save_context(context)
            
            # Remove from active contexts
            del self.active_contexts[user_id][context_id]


# Initialize the conversation management system
async def create_conversation_management_system(storage_dir: str = "./conversation_data"):
    """
    Create and initialize the complete conversation management system.
    
    Args:
        storage_dir: Directory to store conversation data
        
    Returns:
        ConversationManager: Initialized conversation manager
    """
    conversation_manager = ConversationManager(storage_dir)
    
    # Allow time for initialization to complete
    await asyncio.sleep(0.5)
    
    # Verify state is ready
    if hasattr(conversation_manager, '_wait_for_state_ready'):
        await conversation_manager._wait_for_state_ready()
    
    return conversation_manager


# Helper methods for ConversationManager class

async def _async_save_new_context(self, context: ConversationContext):
    """Helper method to asynchronously save a new context."""
    try:
        await self.save_context(context)
    except Exception as e:
        self.logger.error(f"Error in async save of new context: {str(e)}")

def _start_periodic_state_persistence(self):
    """Start a background task for periodic state persistence."""
    self.logger.info("Setting up periodic state persistence")
    
    # Instead of creating an asyncio task immediately, we'll store the coroutine
    # for later execution when an event loop is available
    async def periodic_save():
        try:
            while True:
                # Save all active contexts every 5 minutes
                await asyncio.sleep(300)  # 5 minutes
                
                self.logger.info("Running periodic state persistence")
                
                # Save each active context
                for user_id, contexts in self.active_contexts.items():
                    for context_id, context in contexts.items():
                        try:
                            await self.save_context(context)
                        except Exception as e:
                            self.logger.error(f"Error in periodic save for context {context_id}: {str(e)}")
        except asyncio.CancelledError:
            self.logger.info("Periodic state persistence task cancelled")
        except Exception as e:
            self.logger.error(f"Error in periodic state persistence: {str(e)}")
    
    # Store the coroutine for later scheduling instead of creating a task immediately
    self._persistence_coroutine = periodic_save
    self.logger.info("Prepared periodic state persistence function")
    
    # We'll create a method to start the task when an event loop is available
    def schedule_persistence_task():
        loop = asyncio.get_event_loop_policy().get_event_loop()
        if loop.is_running():
            self._persistence_task = loop.create_task(self._persistence_coroutine())
            self.logger.info("Started periodic state persistence task")
        else:
            self.logger.warning("No running event loop, persistence task not scheduled")
    
    # Try to schedule now if possible, otherwise it will be scheduled later
    try:
        schedule_persistence_task()
    except RuntimeError:
        self.logger.info("Will schedule persistence task when event loop is available")
    
    # Store the scheduler function for later use
    self._schedule_persistence_task = schedule_persistence_task
    
    # Store a reference to the pending contexts coroutine if it exists
    if hasattr(self, '_pending_contexts_coro'):
        self._schedule_pending_contexts()

async def _save_state_snapshot(self, context: ConversationContext):
    """Save a state snapshot for recovery purposes."""
    snapshot_path = os.path.join(self.storage_dir, "snapshots", f"{context.context_id}.json")
    
    try:
        # Create a snapshot file
        with open(snapshot_path, 'w') as f:
            json.dump(context.to_dict(), f, indent=2)
    except Exception as e:
        self.logger.error(f"Error saving state snapshot for {context.context_id}: {str(e)}")

def _load_existing_contexts(self):
    """Load existing contexts from storage during initialization."""
    if not os.path.exists(self.storage_dir):
        self.logger.info("Storage directory does not exist, no contexts to load")
        return
            
    # Load session files
    sessions_dir = os.path.join(self.storage_dir, "sessions")
    if not os.path.exists(sessions_dir):
        self.logger.info("Sessions directory does not exist, no contexts to load")
        return
            
    # Queue loading of existing contexts
    session_files = [f for f in os.listdir(sessions_dir) if f.endswith('.json')]
    self.logger.info(f"Queued loading of existing contexts from {len(session_files)} session files")
        
    # Store the context info for later loading when there's an event loop
    self._pending_contexts = []
    for session_file in session_files:
        try:
            # Load session file to get context_id and user_id
            with open(os.path.join(sessions_dir, session_file), 'r', encoding='utf-8') as f:
                session_data = json.load(f)
                    
            context_id = session_data.get('context_id')
            user_id = session_data.get('user_id')
                
            if context_id and user_id:
                self._pending_contexts.append((context_id, user_id, session_file))
                    
        except Exception as e:
            self.logger.error(f"Error loading session file {session_file}: {str(e)}")
                
    # Start a task to process the pending contexts once the event loop is running
    async def _process_pending_contexts():
        for context_id, user_id, session_file in getattr(self, '_pending_contexts', []):
            try:
                await self._async_load_context(context_id, user_id)
            except Exception as e:
                self.logger.error(f"Error loading context from {session_file}: {str(e)}")
            
    # Schedule the task to run when the event loop starts
    if hasattr(self, '_pending_contexts') and self._pending_contexts:
        # Create a task factory that will be called when we have a running loop
        async def create_context_loading_task():
            try:
                await _process_pending_contexts()
            except Exception as e:
                self.logger.error(f"Error in pending context loading: {str(e)}")
                
        # Store the coroutine to be run when the loop starts
        self._pending_contexts_coro = create_context_loading_task()
        
        # Try to schedule it now if we're in an async context
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self._pending_contexts_coro)
        except RuntimeError:
            # No running loop, will be scheduled by _schedule_pending_contexts
            pass
            
    self.logger.info(f"Queued loading of existing contexts from {len(session_files)} session files")

async def _async_load_context(self, context_id: str, user_id: str):
    """Asynchronously load a context and add it to active contexts."""
    try:
        context = await self.load_context(context_id)
        if context:
            # Add to active contexts if not already there
            if user_id not in self.active_contexts:
                self.active_contexts[user_id] = {}
            self.active_contexts[user_id][context_id] = context
    except Exception as e:
        self.logger.error(f"Error in async load of context {context_id}: {str(e)}")

async def _wait_for_state_ready(self, timeout: float = 30.0):
    """Wait for the state to be ready with timeout."""
    start_time = time.time()
    while not self._state_ready and time.time() - start_time < timeout:
        await asyncio.sleep(0.1)
    
    if not self._state_ready:
        self.logger.warning(f"Timed out waiting for state to be ready after {timeout} seconds")
    
    return self._state_ready

def _schedule_pending_contexts(self):
    """Schedule the pending contexts loading when the event loop is available."""
    if not hasattr(self, '_pending_contexts_coro'):
        return
        
    try:
        # Try to get the running loop
        loop = asyncio.get_running_loop()
        # If we get here, we can create the task
        loop.create_task(self._pending_contexts_coro)
        self.logger.info("Started loading pending contexts in the event loop")
        # Clear the coroutine reference to avoid running it again
        del self._pending_contexts_coro
    except RuntimeError:
        # No running loop yet, will be scheduled when the loop starts
        self.logger.info("Will schedule pending contexts loading when event loop starts")
        # Use call_soon_threadsafe to schedule when the loop starts
        try:
            loop = asyncio.get_event_loop()
            loop.call_soon_threadsafe(self._schedule_pending_contexts)
        except RuntimeError:
            # Still no loop, will be scheduled later
            pass

# Add the helper methods to the ConversationManager class
ConversationManager._async_save_new_context = _async_save_new_context
ConversationManager._start_periodic_state_persistence = _start_periodic_state_persistence
ConversationManager._save_state_snapshot = _save_state_snapshot
ConversationManager._load_existing_contexts = _load_existing_contexts
ConversationManager._async_load_context = _async_load_context
ConversationManager._wait_for_state_ready = _wait_for_state_ready
ConversationManager._schedule_pending_contexts = _schedule_pending_contexts
