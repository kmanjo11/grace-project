"""
Asynchronous Memory System for Grace - A crypto trading application based on Open Interpreter

This module implements a sophisticated memory system with three components:
1. Core Memory - Bridges new information to existing knowledge
2. User-Specific Memory - Personal memory collections for each user
3. Global Memory - Shared knowledge base accessible to all users

All memory is stored in Chroma DB for efficient vector-based retrieval.
The entire system is implemented using async/await for optimal performance.
"""

import os
import json
import time
import uuid
import hashlib
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union

import chromadb
from chromadb.config import Settings
from chromadb.api.models.Collection import Collection
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.schema import Document

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("GraceMemory")

class AsyncMemoryManager:
    """
    Main memory management system for Grace.
    Handles interactions with Chroma DB and manages different memory types.
    Fully asynchronous implementation.
    """
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Initialize the memory manager with a connection to Chroma DB.
        
        Args:
            persist_directory: Directory to store Chroma DB files
        """
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize embedding model
        self.embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # Initialize Chroma client
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Initialize collections
        self.core_collection = self._get_or_create_collection("core_memory")
        self.global_collection = self._get_or_create_collection("global_memory")
        self.user_collections = {}  # Will be populated as users are added
        
        # Authorized users for global memory updates
        self.authorized_users = ["kmanjo11@gmail.com"]
        
        # Lock for thread safety
        self._lock = asyncio.Lock()
        
        # Event logger
        self.event_logger = AsyncEventLogger("memory_events.log")
    
    def _get_or_create_collection(self, collection_name: str) -> Collection:
        """
        Get an existing collection or create a new one if it doesn't exist.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Collection: The requested collection
        """
        try:
            return self.client.get_collection(collection_name)
        except:
            return self.client.create_collection(collection_name)
    
    async def _get_user_collection(self, username: str) -> Collection:
        """
        Get a user's personal memory collection.
        
        Args:
            username: Username to get collection for
            
        Returns:
            Collection: The user's collection
        """
        # Sanitize collection name to avoid conflicts
        sanitized_name = self._sanitize_collection_name(username)
        
        async with self._lock:
            if sanitized_name not in self.user_collections:
                self.user_collections[sanitized_name] = self._get_or_create_collection(sanitized_name)
            
            return self.user_collections[sanitized_name]
    
    def _sanitize_collection_name(self, username: str) -> str:
        """
        Create a sanitized collection name from a username.
        
        Args:
            username: Username to sanitize
            
        Returns:
            str: Sanitized collection name
        """
        # Create a hash of the username to ensure uniqueness and avoid special characters
        hashed = hashlib.md5(username.encode()).hexdigest()
        return f"user_{hashed}"
    
    async def add_to_core_memory(self, text: str, metadata: Dict[str, Any] = None) -> str:
        """
        Add information to core memory.
        
        Args:
            text: Text content to add
            metadata: Additional metadata for the memory
            
        Returns:
            str: ID of the created memory
        """
        if metadata is None:
            metadata = {}
        
        # Generate a unique ID for the memory
        memory_id = str(uuid.uuid4())
        
        # Add timestamp
        metadata["timestamp"] = time.time()
        metadata["type"] = "core"
        
        try:
            # Add to core collection
            self.core_collection.add(
                documents=[text],
                metadatas=[metadata],
                ids=[memory_id]
            )
            
            # Log the event
            await self.event_logger.log_event(
                "add_memory", 
                {"type": "core", "id": memory_id, "text_length": len(text)}
            )
            
            return memory_id
        except Exception as e:
            logger.error(f"Error adding to core memory: {str(e)}")
            await self.event_logger.log_event(
                "error", 
                {"operation": "add_to_core_memory", "error": str(e)}
            )
            raise
    
    async def add_to_user_memory(self, username: str, text: str, metadata: Dict[str, Any] = None) -> str:
        """
        Add information to a user's personal memory.
        
        Args:
            username: User to add memory for
            text: Text content to add
            metadata: Additional metadata for the memory
            
        Returns:
            str: ID of the created memory
        """
        if metadata is None:
            metadata = {}
        
        # Generate a unique ID for the memory
        memory_id = str(uuid.uuid4())
        
        # Add timestamp and user info
        metadata["timestamp"] = time.time()
        metadata["username"] = username
        metadata["type"] = "user"
        
        try:
            # Get user collection and add memory
            user_collection = await self._get_user_collection(username)
            user_collection.add(
                documents=[text],
                metadatas=[metadata],
                ids=[memory_id]
            )
            
            # Log the event
            await self.event_logger.log_event(
                "add_memory", 
                {"type": "user", "user": username, "id": memory_id, "text_length": len(text)}
            )
            
            return memory_id
        except Exception as e:
            logger.error(f"Error adding to user memory: {str(e)}")
            await self.event_logger.log_event(
                "error", 
                {"operation": "add_to_user_memory", "user": username, "error": str(e)}
            )
            raise
    
    async def add_to_global_memory(self, text: str, author: str, metadata: Dict[str, Any] = None) -> str:
        """
        Add information to global memory.
        
        Args:
            text: Text content to add
            author: Author of the memory
            metadata: Additional metadata for the memory
            
        Returns:
            str: ID of the created memory
        """
        if metadata is None:
            metadata = {}
        
        # Generate a unique ID for the memory
        memory_id = str(uuid.uuid4())
        
        # Add timestamp and author info
        metadata["timestamp"] = time.time()
        metadata["author"] = author
        metadata["type"] = "global"
        
        try:
            # Add to global collection
            self.global_collection.add(
                documents=[text],
                metadatas=[metadata],
                ids=[memory_id]
            )
            
            # Log the event
            await self.event_logger.log_event(
                "add_memory", 
                {"type": "global", "author": author, "id": memory_id, "text_length": len(text)}
            )
            
            return memory_id
        except Exception as e:
            logger.error(f"Error adding to global memory: {str(e)}")
            await self.event_logger.log_event(
                "error", 
                {"operation": "add_to_global_memory", "author": author, "error": str(e)}
            )
            raise
    
    async def command_learn(self, entity: str, update: str, author: str) -> bool:
        """
        Process a !grace.learn command to update global memory.
        
        Args:
            entity: Entity to update
            update: New information about the entity
            author: User issuing the command
            
        Returns:
            bool: True if successful, False if unauthorized
        """
        # Check if user is authorized
        if author not in self.authorized_users:
            await self.event_logger.log_event(
                "unauthorized_access", 
                {"operation": "command_learn", "author": author}
            )
            return False
        
        # Format the memory text
        memory_text = f"{entity}: {update}"
        
        # Add metadata about the command
        metadata = {
            "entity": entity,
            "command": "grace.learn",
            "author": author,
            "priority": "high"  # Mark as high priority
        }
        
        try:
            # Add to global memory
            await self.add_to_global_memory(memory_text, author, metadata)
            
            # Log the successful command
            await self.event_logger.log_event(
                "command_executed", 
                {"command": "grace.learn", "entity": entity, "author": author}
            )
            
            return True
        except Exception as e:
            logger.error(f"Error processing command_learn: {str(e)}")
            await self.event_logger.log_event(
                "error", 
                {"operation": "command_learn", "author": author, "error": str(e)}
            )
            return False
    
    async def query_memory(
        self, 
        query: str, 
        username: Optional[str] = None, 
        memory_types: List[str] = ["core", "global", "user"],
        limit: int = 5
    ) -> Dict[str, List[Dict]]:
        """
        Query memories across different collections based on relevance.
        
        Args:
            query: Query text
            username: Username for user-specific memories
            memory_types: Types of memory to query
            limit: Maximum number of results per memory type
            
        Returns:
            Dict: Results organized by memory type
        """
        results = {}
        tasks = []
        
        # Get embeddings for the query
        query_embedding = self.embedding_model.embed_query(query)
        
        # Create tasks for each memory type
        if "core" in memory_types:
            tasks.append(self._query_core_memory(query_embedding, limit))
        
        if "global" in memory_types:
            tasks.append(self._query_global_memory(query_embedding, limit))
        
        if "user" in memory_types and username:
            tasks.append(self._query_user_memory(username, query_embedding, limit))
        
        # Run all queries concurrently
        completed_tasks = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for task_result in completed_tasks:
            if isinstance(task_result, Exception):
                logger.error(f"Error in query task: {str(task_result)}")
                continue
                
            memory_type, memory_results = task_result
            results[memory_type] = memory_results
        
        # Log the query event
        await self.event_logger.log_event(
            "query_memory", 
            {
                "query_length": len(query), 
                "memory_types": memory_types,
                "results_count": {k: len(v) for k, v in results.items()}
            }
        )
        
        return results
    
    async def _query_core_memory(self, query_embedding, limit):
        """Helper method to query core memory"""
        try:
            core_results = self.core_collection.query(
                query_embeddings=[query_embedding],
                n_results=limit
            )
            return "core", self._format_results(core_results)
        except Exception as e:
            logger.error(f"Error querying core memory: {str(e)}")
            await self.event_logger.log_event(
                "error", 
                {"operation": "_query_core_memory", "error": str(e)}
            )
            return "core", []
    
    async def _query_global_memory(self, query_embedding, limit):
        """Helper method to query global memory"""
        try:
            global_results = self.global_collection.query(
                query_embeddings=[query_embedding],
                n_results=limit
            )
            return "global", self._format_results(global_results)
        except Exception as e:
            logger.error(f"Error querying global memory: {str(e)}")
            await self.event_logger.log_event(
                "error", 
                {"operation": "_query_global_memory", "error": str(e)}
            )
            return "global", []
    
    async def _query_user_memory(self, username, query_embedding, limit):
        """Helper method to query user memory"""
        try:
            user_collection = await self._get_user_collection(username)
            user_results = user_collection.query(
                query_embeddings=[query_embedding],
                n_results=limit
            )
            return "user", self._format_results(user_results)
        except Exception as e:
            logger.error(f"Error querying user memory: {str(e)}")
            await self.event_logger.log_event(
                "error", 
                {"operation": "_query_user_memory", "user": username, "error": str(e)}
            )
            return "user", []
    
    def _format_results(self, chroma_results):
        """
        Format Chroma results into a more usable structure.
        
        Args:
            chroma_results: Results from Chroma query
            
        Returns:
            List: Formatted results
        """
        formatted_results = []
        
        # Handle empty results
        if not chroma_results or not chroma_results.get("ids") or not chroma_results["ids"][0]:
            return formatted_results
        
        for i in range(len(chroma_results.get("ids", [[]])[0])):
            result = {
                "id": chroma_results["ids"][0][i],
                "text": chroma_results["documents"][0][i],
                "metadata": chroma_results["metadatas"][0][i],
                "distance": chroma_results.get("distances", [[0]])[0][i]
            }
            
            # Prioritize results from authorized users or with high priority
            if (result["metadata"].get("author") in self.authorized_users or 
                result["metadata"].get("priority") == "high"):
                result["priority"] = "high"
            else:
                result["priority"] = "normal"
                
            formatted_results.append(result)
        
        # Sort by priority (high first) then by distance
        formatted_results.sort(
            key=lambda x: (0 if x["priority"] == "high" else 1, x["distance"])
        )
        
        return formatted_results
    
    async def get_memory_by_id(self, memory_id: str, memory_type: str, username: Optional[str] = None):
        """
        Retrieve a specific memory by ID.
        
        Args:
            memory_id: ID of the memory to retrieve
            memory_type: Type of memory (core, global, user)
            username: Username for user memories
            
        Returns:
            Dict: Memory data if found
        """
        collection = None
        
        if memory_type == "core":
            collection = self.core_collection
        elif memory_type == "global":
            collection = self.global_collection
        elif memory_type == "user" and username:
            collection = await self._get_user_collection(username)
        
        if not collection:
            return None
        
        try:
            result = collection.get(ids=[memory_id])
            
            if result["ids"]:
                return {
                    "id": result["ids"][0],
                    "text": result["documents"][0],
                    "metadata": result["metadatas"][0]
                }
        except Exception as e:
            logger.error(f"Error getting memory by ID: {str(e)}")
            await self.event_logger.log_event(
                "error", 
                {"operation": "get_memory_by_id", "memory_id": memory_id, "error": str(e)}
            )
            
        return None


class AsyncEntityLinker:
    """
    Handles linking between entities across different memory types.
    Fully asynchronous implementation.
    """
    
    def __init__(self, memory_manager: AsyncMemoryManager):
        """
        Initialize the entity linker.
        
        Args:
            memory_manager: AsyncMemoryManager instance
        """
        self.memory_manager = memory_manager
        self.logger = logging.getLogger("GraceEntityLinker")
    
    async def find_related_memories(
        self, 
        text: str, 
        username: Optional[str] = None, 
        limit: int = 3
    ) -> Dict[str, List[Dict]]:
        """
        Find memories related to the input text.
        
        Args:
            text: Input text
            username: Username for user context
            limit: Maximum number of related memories per type
            
        Returns:
            Dict: Related memories by type
        """
        # Query all memory types
        try:
            results = await self.memory_manager.query_memory(
                query=text,
                username=username,
                memory_types=["core", "global", "user"],
                limit=limit
            )
            
            return results
        except Exception as e:
            self.logger.error(f"Error finding related memories: {str(e)}")
            await self.memory_manager.event_logger.log_event(
                "error", 
                {"operation": "find_related_memories", "error": str(e)}
            )
            return {"core": [], "global": [], "user": []}
    
    async def connect_new_information(
        self, 
        new_text: str, 
        username: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Connect new information to existing memories.
        
        Args:
            new_text: New information to connect
            username: Username for user context
            
        Returns:
            Dict: Connection information
        """
        try:
            # Find related existing memories
            related_memories = await self.find_related_memories(new_text, username)
            
            # Store the new information in appropriate memory
            if username:
                memory_id = await self.memory_manager.add_to_user_memory(
                    username=username,
                    text=new_text,
                    metadata={"connected_to": str(related_memories)}  # Convert to string for storage
                )
            else:
                memory_id = await self.memory_manager.add_to_global_memory(
                    text=new_text,
                    author="system",
                    metadata={"connected_to": str(related_memories)}  # Convert to string for storage
                )
            
            return {
                "memory_id": memory_id,
                "related_memories": related_memories
            }
        except Exception as e:
            self.logger.error(f"Error connecting new information: {str(e)}")
            await self.memory_manager.event_logger.log_event(
                "error", 
                {"operation": "connect_new_information", "error": str(e)}
            )
            return {
                "memory_id": None,
                "related_memories": None,
                "error": str(e)
            }


class AsyncMemoryRouter:
    """
    Routes memory operations to appropriate memory stores based on context.
    Fully asynchronous implementation.
    """
    
    def __init__(self, memory_manager: AsyncMemoryManager, entity_linker: AsyncEntityLinker):
        """
        Initialize the memory router.
        
        Args:
            memory_manager: AsyncMemoryManager instance
            entity_linker: AsyncEntityLinker instance
        """
        self.memory_manager = memory_manager
        self.entity_linker = entity_linker
        self.logger = logging.getLogger("GraceMemoryRouter")
    
    async def process_input(
        self, 
        text: str, 
        username: Optional[str] = None, 
        is_command: bool = False
    ) -> Dict[str, Any]:
        """
        Process input text and route to appropriate memory operations.
        
        Args:
            text: Input text
            username: Username for user context
            is_command: Whether the input is a command
            
        Returns:
            Dict: Processing results
        """
        result = {
            "processed": True,
            "memory_updated": False,
            "command_processed": False,
            "related_memories": None
        }
        
        try:
            # Check if this is a command
            if is_command and text.startswith("!grace.learn"):
                # Parse command
                try:
                    # Format should be: !grace.learn entity:update
                    command_parts = text.split(" ", 1)[1]  # Remove !grace.learn
                    entity, update = command_parts.split(":", 1)
                    
                    # Process command
                    success = await self.memory_manager.command_learn(
                        entity=entity.strip(),
                        update=update.strip(),
                        author=username
                    )
                    
                    result["command_processed"] = success
                    result["memory_updated"] = success
                    
                    await self.memory_manager.event_logger.log_event(
                        "command_processed", 
                        {"command": "grace.learn", "success": success, "user": username}
                    )
                    
                    return result
                except Exception as e:
                    self.logger.error(f"Error processing command: {str(e)}")
                    await self.memory_manager.event_logger.log_event(
                        "error", 
                        {"operation": "process_command", "command": text, "error": str(e)}
                    )
                    result["command_processed"] = False
                    return result
            
            # Not a command, process as regular input
            # Find related memories
            related_memories = await self.entity_linker.find_related_memories(text, username)
            result["related_memories"] = related_memories
            
            # Connect new information if it seems significant
            # This is a simplified heuristic - in production you would use more sophisticated methods
            if len(text.split()) > 10:  # Only store longer, more meaningful texts
                connection = await self.entity_linker.connect_new_information(text, username)
                result["memory_updated"] = True
                result["connection"] = connection
            
            return result
        except Exception as e:
            self.logger.error(f"Error in process_input: {str(e)}")
            await self.memory_manager.event_logger.log_event(
                "error", 
                {"operation": "process_input", "error": str(e)}
            )
            result["processed"] = False
            result["error"] = str(e)
            return result


class AsyncEventLogger:
    """
    Asynchronous event logging system for memory operations.
    """
    
    def __init__(self, log_file: str):
        """
        Initialize the event logger.
        
        Args:
            log_file: Path to the log file
        """
        self.log_file = log_file
        self.logger = logging.getLogger("GraceEventLogger")
        self._lock = asyncio.Lock()
    
    async def log_event(self, event_type: str, event_data: Dict[str, Any]):
        """
        Log an event asynchronously.
        
        Args:
            event_type: Type of event
            event_data: Event data
        """
        try:
            event = {
                "timestamp": time.time(),
                "type": event_type,
                "data": event_data
            }
            
            async with self._lock:
                with open(self.log_file, "a") as f:
                    f.write(json.dumps(event) + "\n")
        except Exception as e:
            self.logger.error(f"Error logging event: {str(e)}")


# Initialize the memory system
async def create_memory_system(persist_directory: str = "./chroma_db"):
    """
    Create and initialize the complete memory system asynchronously.
    
    Args:
        persist_directory: Directory to store Chroma DB files
        
    Returns:
        Tuple: (AsyncMemoryManager, AsyncEntityLinker, AsyncMemoryRouter)
    """
    memory_manager = AsyncMemoryManager(persist_directory)
    entity_linker = AsyncEntityLinker(memory_manager)
    memory_router = AsyncMemoryRouter(memory_manager, entity_linker)
    
    return memory_manager, entity_linker, memory_router
