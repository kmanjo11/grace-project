"""
Memory System for Grace - A crypto trading application based on Open Interpreter

This module implements a sophisticated memory system with three components:
1. Core Memory - Bridges new information to existing knowledge
2. User-Specific Memory - Personal memory collections for each user
3. Global Memory - Shared knowledge base accessible to all users

All memory is stored in Chroma DB for efficient vector-based retrieval.
"""

import os
import json
import time
import uuid
import hashlib
from typing import Dict, List, Optional, Any, Union

import chromadb
from chromadb.config import Settings
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.schema import Document

class MemoryManager:
    """
    Main memory management system for Grace.
    Handles interactions with Chroma DB and manages different memory types.
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
    
    def _get_or_create_collection(self, collection_name: str):
        """
        Get an existing collection or create a new one if it doesn't exist.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            ChromaCollection: The requested collection
        """
        try:
            return self.client.get_collection(collection_name)
        except:
            return self.client.create_collection(collection_name)
    
    def _get_user_collection(self, username: str):
        """
        Get a user's personal memory collection.
        
        Args:
            username: Username to get collection for
            
        Returns:
            ChromaCollection: The user's collection
        """
        # Sanitize collection name to avoid conflicts
        sanitized_name = self._sanitize_collection_name(username)
        
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
    
    def add_to_core_memory(self, text: str, metadata: Dict[str, Any] = None):
        """
        Add information to core memory.
        
        Args:
            text: Text content to add
            metadata: Additional metadata for the memory
        """
        if metadata is None:
            metadata = {}
        
        # Generate a unique ID for the memory
        memory_id = str(uuid.uuid4())
        
        # Add timestamp
        metadata["timestamp"] = time.time()
        metadata["type"] = "core"
        
        # Add to core collection
        self.core_collection.add(
            documents=[text],
            metadatas=[metadata],
            ids=[memory_id]
        )
        
        return memory_id
    
    def add_to_user_memory(self, username: str, text: str, metadata: Dict[str, Any] = None):
        """
        Add information to a user's personal memory.
        
        Args:
            username: User to add memory for
            text: Text content to add
            metadata: Additional metadata for the memory
        """
        if metadata is None:
            metadata = {}
        
        # Generate a unique ID for the memory
        memory_id = str(uuid.uuid4())
        
        # Add timestamp and user info
        metadata["timestamp"] = time.time()
        metadata["username"] = username
        metadata["type"] = "user"
        
        # Get user collection and add memory
        user_collection = self._get_user_collection(username)
        user_collection.add(
            documents=[text],
            metadatas=[metadata],
            ids=[memory_id]
        )
        
        return memory_id
    
    def add_to_global_memory(self, text: str, author: str, metadata: Dict[str, Any] = None):
        """
        Add information to global memory.
        
        Args:
            text: Text content to add
            author: Author of the memory
            metadata: Additional metadata for the memory
        """
        if metadata is None:
            metadata = {}
        
        # Generate a unique ID for the memory
        memory_id = str(uuid.uuid4())
        
        # Add timestamp and author info
        metadata["timestamp"] = time.time()
        metadata["author"] = author
        metadata["type"] = "global"
        
        # Add to global collection
        self.global_collection.add(
            documents=[text],
            metadatas=[metadata],
            ids=[memory_id]
        )
        
        return memory_id
    
    def command_learn(self, entity: str, update: str, author: str):
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
            return False
        
        # Format the memory text
        memory_text = f"{entity}: {update}"
        
        # Add metadata about the command
        metadata = {
            "entity": entity,
            "command": "grace.learn",
            "author": author
        }
        
        # Add to global memory
        self.add_to_global_memory(memory_text, author, metadata)
        
        return True
    
    def query_memory(self, query: str, username: Optional[str] = None, 
                    memory_types: List[str] = ["core", "global", "user"],
                    limit: int = 5):
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
        
        # Get embeddings for the query
        query_embedding = self.embedding_model.embed_query(query)
        
        # Query core memory if requested
        if "core" in memory_types:
            core_results = self.core_collection.query(
                query_embeddings=[query_embedding],
                n_results=limit
            )
            results["core"] = self._format_results(core_results)
        
        # Query global memory if requested
        if "global" in memory_types:
            global_results = self.global_collection.query(
                query_embeddings=[query_embedding],
                n_results=limit
            )
            results["global"] = self._format_results(global_results)
        
        # Query user memory if requested and username provided
        if "user" in memory_types and username:
            user_collection = self._get_user_collection(username)
            user_results = user_collection.query(
                query_embeddings=[query_embedding],
                n_results=limit
            )
            results["user"] = self._format_results(user_results)
        
        return results
    
    def _format_results(self, chroma_results):
        """
        Format Chroma results into a more usable structure.
        
        Args:
            chroma_results: Results from Chroma query
            
        Returns:
            List: Formatted results
        """
        formatted_results = []
        
        for i in range(len(chroma_results.get("ids", [[]])[0])):
            result = {
                "id": chroma_results["ids"][0][i],
                "text": chroma_results["documents"][0][i],
                "metadata": chroma_results["metadatas"][0][i],
                "distance": chroma_results.get("distances", [[0]])[0][i]
            }
            formatted_results.append(result)
        
        return formatted_results
    
    def link_entities(self, text: str, username: Optional[str] = None):
        """
        Find and link entities in text to existing memories.
        
        Args:
            text: Text to analyze for entities
            username: Username for user-specific context
            
        Returns:
            Dict: Linked entities with their memory references
        """
        # This is a simplified implementation
        # In a production system, you would use NER (Named Entity Recognition)
        # to extract entities and then link them to memories
        
        # For now, we'll just do a simple keyword search
        words = text.split()
        unique_words = set([word.lower().strip('.,!?;:()[]{}""\'') for word in words if len(word) > 3])
        
        linked_entities = {}
        
        for word in unique_words:
            # Query all memory types for this entity
            results = self.query_memory(
                query=word,
                username=username,
                memory_types=["core", "global", "user"],
                limit=2
            )
            
            # Only include if we found matches
            if any(results.get(mem_type, []) for mem_type in results):
                linked_entities[word] = results
        
        return linked_entities
    
    def get_memory_by_id(self, memory_id: str, memory_type: str, username: Optional[str] = None):
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
            collection = self._get_user_collection(username)
        
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
        except:
            pass
        
        return None


class EntityLinker:
    """
    Handles linking between entities across different memory types.
    """
    
    def __init__(self, memory_manager: MemoryManager):
        """
        Initialize the entity linker.
        
        Args:
            memory_manager: MemoryManager instance
        """
        self.memory_manager = memory_manager
    
    def find_related_memories(self, text: str, username: Optional[str] = None, limit: int = 3):
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
        results = self.memory_manager.query_memory(
            query=text,
            username=username,
            memory_types=["core", "global", "user"],
            limit=limit
        )
        
        return results
    
    def connect_new_information(self, new_text: str, username: Optional[str] = None):
        """
        Connect new information to existing memories.
        
        Args:
            new_text: New information to connect
            username: Username for user context
            
        Returns:
            Dict: Connection information
        """
        # Find related existing memories
        related_memories = self.find_related_memories(new_text, username)
        
        # Store the new information in appropriate memory
        if username:
            memory_id = self.memory_manager.add_to_user_memory(
                username=username,
                text=new_text,
                metadata={"connected_to": related_memories}
            )
        else:
            memory_id = self.memory_manager.add_to_global_memory(
                text=new_text,
                author="system",
                metadata={"connected_to": related_memories}
            )
        
        return {
            "memory_id": memory_id,
            "related_memories": related_memories
        }


class MemoryRouter:
    """
    Routes memory operations to appropriate memory stores based on context.
    """
    
    def __init__(self, memory_manager: MemoryManager, entity_linker: EntityLinker):
        """
        Initialize the memory router.
        
        Args:
            memory_manager: MemoryManager instance
            entity_linker: EntityLinker instance
        """
        self.memory_manager = memory_manager
        self.entity_linker = entity_linker
    
    def process_input(self, text: str, username: Optional[str] = None, is_command: bool = False):
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
        
        # Check if this is a command
        if is_command and text.startswith("!grace.learn"):
            # Parse command
            try:
                # Format should be: !grace.learn entity:update
                command_parts = text.split(" ", 1)[1]  # Remove !grace.learn
                entity, update = command_parts.split(":", 1)
                
                # Process command
                success = self.memory_manager.command_learn(
                    entity=entity.strip(),
                    update=update.strip(),
                    author=username
                )
                
                result["command_processed"] = success
                result["memory_updated"] = success
                
                return result
            except:
                result["command_processed"] = False
                return result
        
        # Not a command, process as regular input
        # Find related memories
        related_memories = self.entity_linker.find_related_memories(text, username)
        result["related_memories"] = related_memories
        
        # Connect new information if it seems significant
        # This is a simplified heuristic - in production you would use more sophisticated methods
        if len(text.split()) > 10:  # Only store longer, more meaningful texts
            connection = self.entity_linker.connect_new_information(text, username)
            result["memory_updated"] = True
            result["connection"] = connection
        
        return result


# Initialize the memory system
def create_memory_system(persist_directory: str = "./chroma_db"):
    """
    Create and initialize the complete memory system.
    
    Args:
        persist_directory: Directory to store Chroma DB files
        
    Returns:
        Tuple: (MemoryManager, EntityLinker, MemoryRouter)
    """
    memory_manager = MemoryManager(persist_directory)
    entity_linker = EntityLinker(memory_manager)
    memory_router = MemoryRouter(memory_manager, entity_linker)
    
    return memory_manager, entity_linker, memory_router
