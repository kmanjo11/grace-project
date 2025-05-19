import os
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, Tuple
import chromadb
from chromadb.utils import embedding_functions
import uuid
import re


from src.user_profile import UserProfileSystem
class MemorySystem:
    """
    Grace's three-layer memory system with ChromaDB integration.
    
    Layers:
    - Short-term: Active context window for immediate conversations
    - Medium-term: Personal user memories that persist across sessions
    - Long-term: Global shared knowledge accessible to all users
    """
    
    def __init__(self, chroma_db_path: str, user_profile_system: 'UserProfileSystem'):
        """Initialize the memory system with ChromaDB."""
        self.chroma_client = chromadb.PersistentClient(path=chroma_db_path)
        self.user_profile_system = user_profile_system
        
        # Create embedding function
        self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
        
        # Initialize collections
        self._initialize_collections()
        
        # Time-based decay settings
        self.short_term_ttl = 60 * 60 * 24  # 1 day in seconds
        self.medium_term_ttl = 60 * 60 * 24 * 30  # 30 days in seconds
        
    def _initialize_collections(self):
        """Initialize ChromaDB collections for each memory layer."""
        # Global long-term memory collection
        self.global_collection = self._get_or_create_collection("global_memory")
        
        # System configuration collection
        self.system_collection = self._get_or_create_collection("system_config")
        
        # User-specific collections are created on demand
        self.user_collections = {}
    
    def _get_or_create_collection(self, name: str):
        """Get or create a ChromaDB collection."""
        try:
            return self.chroma_client.get_collection(
                name=name,
                embedding_function=self.embedding_function
            )
        except ValueError:
            return self.chroma_client.create_collection(
                name=name,
                embedding_function=self.embedding_function
            )
    
    def _get_user_collection(self, user_id: str):
        """Get or create a user-specific collection."""
        # Sanitize user_id for collection name
        sanitized_id = re.sub(r'[^a-zA-Z0-9_]', '', user_id)
        collection_name = f"user_{sanitized_id}_memory"
        
        if collection_name not in self.user_collections:
            self.user_collections[collection_name] = self._get_or_create_collection(collection_name)
        
        return self.user_collections[collection_name]
    
    def add_to_short_term(self, user_id: str, text: str, metadata: Dict[str, Any] = None) -> str:
        """Add memory to short-term (token allocation system)."""
        if metadata is None:
            metadata = {}
        
        # Add timestamp for decay
        metadata["timestamp"] = time.time()
        metadata["memory_type"] = "short_term"
        
        # Generate a unique ID for this memory
        memory_id = str(uuid.uuid4())
        
        # Get user collection
        user_collection = self._get_user_collection(user_id)
        
        # Add to ChromaDB
        user_collection.add(
            ids=[memory_id],
            documents=[text],
            metadatas=[metadata]
        )
        
        return memory_id
    
    def add_to_medium_term(self, user_id: str, text: str, metadata: Dict[str, Any] = None) -> str:
        """Add memory to medium-term (personal user memories)."""
        if metadata is None:
            metadata = {}
        
        # Add timestamp for decay
        metadata["timestamp"] = time.time()
        metadata["memory_type"] = "medium_term"
        
        # Generate a unique ID for this memory
        memory_id = str(uuid.uuid4())
        
        # Get user collection
        user_collection = self._get_user_collection(user_id)
        
        # Add to ChromaDB
        user_collection.add(
            ids=[memory_id],
            documents=[text],
            metadatas=[metadata]
        )
        
        return memory_id
    
    def add_to_long_term(self, text: str, entity: str = None, metadata: Dict[str, Any] = None, 
                         user_id: str = None) -> str:
        """
        Add memory to long-term (global shared knowledge).
        
        If user_id is provided, checks if user is authorized for global updates.
        """
        if metadata is None:
            metadata = {}
        
        # Check authorization if user_id is provided
        if user_id and self.user_profile_system:
            if not self.user_profile_system.is_authorized_user(user_id):
                raise PermissionError(f"User {user_id} is not authorized for global memory updates")
        
        # Add timestamp and entity
        metadata["timestamp"] = time.time()
        metadata["memory_type"] = "long_term"
        if entity:
            metadata["entity"] = entity
        
        # Generate a unique ID for this memory
        memory_id = str(uuid.uuid4())
        
        # Add to global collection
        self.global_collection.add(
            ids=[memory_id],
            documents=[text],
            metadatas=[metadata]
        )
        
        return memory_id
    
    def process_grace_learn_command(self, user_id: str, command: str) -> Dict[str, Any]:
        """
        Process !grace.learn command from authorized users.
        
        Format: !grace.learn entity:update
        Example: !grace.learn Drake:new album cancelled
        """
        if not self.user_profile_system or not self.user_profile_system.is_authorized_user(user_id):
            raise PermissionError(f"User {user_id} is not authorized for !grace.learn commands")
        
        # Remove command prefix
        content = command.replace("!grace.learn", "").strip()
        
        # Parse entity and update
        parts = content.split(":", 1)
        if len(parts) != 2:
            raise ValueError("Invalid format. Use: !grace.learn entity:update")
        
        entity = parts[0].strip()
        update = parts[1].strip()
        
        if not entity or not update:
            raise ValueError("Both entity and update must be provided")
        
        # Add to long-term memory
        memory_id = self.add_to_long_term(
            text=update,
            entity=entity,
            metadata={
                "source": "grace_learn_command",
                "user_id": user_id,
                "command": command,
                "priority": "high"  # High priority for authorized updates
            }
        )
        
        return {
            "memory_id": memory_id,
            "entity": entity,
            "update": update,
            "status": "success"
        }
    
    def query_memory(self, query: str, user_id: Optional[str] = None, 
                     memory_types: List[str] = None, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Query memory across specified layers.
        
        Args:
            query: The query text
            user_id: User ID for personal memories (required for short/medium term)
            memory_types: List of memory types to query ("short_term", "medium_term", "long_term")
            n_results: Number of results to return per memory type
            
        Returns:
            List of memory entries with relevance scores
        """
        if memory_types is None:
            memory_types = ["short_term", "medium_term", "long_term"]
        
        results = []
        
        # Query short-term and medium-term memories (user-specific)
        if user_id and ("short_term" in memory_types or "medium_term" in memory_types):
            user_collection = self._get_user_collection(user_id)
            
            # Build where clause for memory types
            where_clause = {"$or": []}
            if "short_term" in memory_types:
                where_clause["$or"].append({"memory_type": "short_term"})
            if "medium_term" in memory_types:
                where_clause["$or"].append({"memory_type": "medium_term"})
            
            # Query user collection
            user_results = user_collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_clause
            )
            
            # Process results
            if user_results["documents"]:
                for i, doc in enumerate(user_results["documents"][0]):
                    if i < len(user_results["metadatas"][0]) and i < len(user_results["distances"][0]):
                        results.append({
                            "text": doc,
                            "metadata": user_results["metadatas"][0][i],
                            "relevance": 1.0 - min(user_results["distances"][0][i], 1.0),
                            "id": user_results["ids"][0][i]
                        })
        
        # Query long-term memories (global)
        if "long_term" in memory_types:
            global_results = self.global_collection.query(
                query_texts=[query],
                n_results=n_results,
                where={"memory_type": "long_term"}
            )
            
            # Process results
            if global_results["documents"]:
                for i, doc in enumerate(global_results["documents"][0]):
                    if i < len(global_results["metadatas"][0]) and i < len(global_results["distances"][0]):
                        results.append({
                            "text": doc,
                            "metadata": global_results["metadatas"][0][i],
                            "relevance": 1.0 - min(global_results["distances"][0][i], 1.0),
                            "id": global_results["ids"][0][i]
                        })
        
        # Sort by relevance
        results.sort(key=lambda x: x["relevance"], reverse=True)
        
        return results
    
    def query_by_entity(self, entity: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Query long-term memory by entity."""
        global_results = self.global_collection.query(
            query_texts=[entity],
            n_results=n_results,
            where={"memory_type": "long_term"}
        )
        
        results = []
        
        # Process results
        if global_results["documents"]:
            for i, doc in enumerate(global_results["documents"][0]):
                if i < len(global_results["metadatas"][0]) and i < len(global_results["distances"][0]):
                    results.append({
                        "text": doc,
                        "metadata": global_results["metadatas"][0][i],
                        "relevance": 1.0 - min(global_results["distances"][0][i], 1.0),
                        "id": global_results["ids"][0][i]
                    })
        return results
    
    def prune_expired_memories(self):
        """Prune expired memories based on TTL settings."""
        current_time = time.time()
        
        # Prune short-term memories
        self._prune_memories_by_type("short_term", current_time - self.short_term_ttl)
        
        # Prune medium-term memories
        self._prune_memories_by_type("medium_term", current_time - self.medium_term_ttl)
        
        logger.info("Completed memory pruning")
        
    def process_task(self, task_content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a task from the agent framework.
        
        Args:
            task_content: Task content and parameters
            
        Returns:
            Dict[str, Any]: Task result
        """
        task_type = task_content.get("type")
        logger.info(f"Processing memory task of type: {task_type}")
        
        if task_type == "query_memory":
            query = task_content.get("query")
            user_id = task_content.get("user_id")
            memory_types = task_content.get("memory_types", ["short_term", "medium_term", "long_term"])
            n_results = task_content.get("n_results", 5)
            
            if not query:
                logger.error("Query is required for memory search")
                return {"status": "error", "message": "Query is required"}
                
            if not user_id:
                logger.error("User ID is required for memory search")
                return {"status": "error", "message": "User ID is required"}
                
            results = self.query_memory(query, user_id, memory_types, n_results)
            return {"status": "success", "results": results}
            
        elif task_type == "add_memory" or task_type == "remember":
            text = task_content.get("text")
            user_id = task_content.get("user_id")
            memory_type = task_content.get("memory_type", "medium_term")
            metadata = task_content.get("metadata", {})
            
            if not text:
                logger.error("Text is required for adding memory")
                return {"status": "error", "message": "Text is required"}
                
            if not user_id:
                logger.error("User ID is required for adding memory")
                return {"status": "error", "message": "User ID is required"}
                
            # Add to appropriate memory layer
            if memory_type == "short_term":
                memory_id = self.add_to_short_term(user_id, text, metadata)
            elif memory_type == "medium_term":
                memory_id = self.add_to_medium_term(user_id, text, metadata)
            elif memory_type == "long_term":
                memory_id = self.add_to_long_term(text, metadata=metadata, user_id=user_id)
            else:
                return {"status": "error", "message": f"Unknown memory type: {memory_type}"}
            
            return {"status": "success", "message": f"Added to {memory_type} memory", "memory_id": memory_id}
        
        elif task_type == "prune_memory":
            self.prune_expired_memories()
            return {"status": "success", "message": "Memory pruning completed"}
            
        return {"status": "error", "message": f"Unknown task type: {task_type}"}
        
    def _prune_memories_by_type(self, memory_type: str, cutoff_time: float):
        """Prune memories of a specific type that are older than the cutoff time."""
        for collection_name, collection in self.user_collections.items():
            # Find expired memories of the specified type
            expired_memories = collection.query(
                query_texts=[""],
                where={
                    "memory_type": memory_type,
                    "timestamp": {"$lt": cutoff_time}
                },
                n_results=100
            )
            
            # Delete expired memories
            if expired_memories["ids"] and expired_memories["ids"][0]:
                collection.delete(ids=expired_memories["ids"][0])
                logger.info(f"Pruned {len(expired_memories['ids'][0])} {memory_type} memories from {collection_name}")
    
    def get_conversation_context(self, user_id: str, n_messages: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversation context for a user."""
        user_collection = self._get_user_collection(user_id)
        
        # Query recent short-term memories without order_by (which isn't supported in some ChromaDB versions)
        results = user_collection.query(
            query_texts=[""],
            where={"memory_type": "short_term"},
            n_results=n_messages
        )
        
        context = []
        
        # Process results
        if results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                if i < len(results["metadatas"][0]):
                    context.append({
                        "text": doc,
                        "metadata": results["metadatas"][0][i],
                        "id": results["ids"][0][i]
                    })
            
            # Sort manually by timestamp (descending) to get most recent messages first
            if context and all("timestamp" in item["metadata"] for item in context):
                context.sort(key=lambda x: x["metadata"]["timestamp"], reverse=True)
        
        return context
    
    def merge_related_memories(self, threshold: float = 0.85):
        """Merge highly similar memories to avoid duplication."""
        # This is a simplified implementation
        # In a production system, this would use more sophisticated clustering
        
        # Get all long-term memories
        all_memories = self.global_collection.query(
            query_texts=[""],
            where={"memory_type": "long_term"},
            n_results=1000
        )
        
        if not all_memories["documents"] or not all_memories["documents"][0]:
            return
        
        # Group by entity
        entities = {}
        for i, doc in enumerate(all_memories["documents"][0]):
            if i < len(all_memories["metadatas"][0]) and "entity" in all_memories["metadatas"][0][i]:
                entity = all_memories["metadatas"][0][i]["entity"]
                if entity not in entities:
                    entities[entity] = []
                
                entities[entity].append({
                    "id": all_memories["ids"][0][i],
                    "text": doc,
                    "metadata": all_memories["metadatas"][0][i]
                })
        
        # For each entity, find similar memories
        for entity, memories in entities.items():
            if len(memories) <= 1:
                continue
            
            # Compare each memory with others
            for i in range(len(memories)):
                for j in range(i + 1, len(memories)):
                    # Query similarity
                    similarity = self.global_collection.query(
                        query_texts=[memories[i]["text"]],
                        where={"memory_type": "long_term", "entity": entity},
                        ids=[memories[j]["id"]]
                    )
                    
                    # If similar enough, merge
                    if similarity["distances"] and similarity["distances"][0] and similarity["distances"][0][0] < (1.0 - threshold):
                        # Create merged memory
                        merged_text = f"{memories[i]['text']} {memories[j]['text']}"
                        
                        # Add merged memory
                        self.add_to_long_term(
                            text=merged_text,
                            entity=entity,
                            metadata={"merged": True}
                        )
                        
                        # Delete old memories
                        self.global_collection.delete(ids=[memories[i]["id"], memories[j]["id"]])
                        
                        # Skip to next memory
                        break
                        
    def process_task(self, task_content: Dict[str, Any]) -> Dict[str, Any]:
        """Process a task from the agent framework.
        
        Args:
            task_content: Task content and parameters
            
        Returns:
            Dict: Task result
        """
        task_type = task_content.get("type")
        
        if task_type == "query_memory":
            query = task_content.get("query")
            user_id = task_content.get("user_id")
            memory_types = task_content.get("memory_types", ["short_term", "medium_term", "long_term"])
            limit = task_content.get("limit", 5)
            
            results = self.query_memory(query, user_id, memory_types, limit)
            return {"results": results, "status": "success"}
            
        elif task_type == "add_memory" or task_type == "remember":
            text = task_content.get("text")
            user_id = task_content.get("user_id")
            memory_type = task_content.get("memory_type", "medium_term")
            metadata = task_content.get("metadata", {})
            
            if memory_type == "short_term":
                memory_id = self.add_to_short_term(user_id, text, metadata)
            elif memory_type == "medium_term":
                memory_id = self.add_to_medium_term(user_id, text, metadata)
            elif memory_type == "long_term":
                entity = task_content.get("entity")
                if not entity:
                    return {"status": "error", "message": "Entity is required for long-term memory"}
                memory_id = self.add_to_long_term(text, entity, metadata, user_id)
            else:
                return {"status": "error", "message": f"Unknown memory type: {memory_type}"}
            
            return {"status": "success", "message": f"Added to {memory_type} memory", "memory_id": memory_id}
        
        elif task_type == "prune_memory":
            self.prune_expired_memories()
            return {"status": "success", "message": "Memory pruning completed"}
            
        return {"status": "error", "message": f"Unknown task type: {task_type}"}

class MemoryBridgeSystem:
    """
    System for bridging between different memory layers and Open Interpreter.
    
    This system:
    1. Connects new information to existing knowledge
    2. Routes memory operations to appropriate layers
    3. Maintains entity relationships
    4. Provides context-aware memory retrieval
    """
    
    def __init__(self, memory_system: MemorySystem):
        """Initialize with memory system."""
        self.memory_system = memory_system
        
        # Entity tracking
        self.active_entities = set()
        self.entity_relationships = {}
    
    def process_message(self, message: str, user_id: str, is_user: bool = True) -> Dict[str, Any]:
        """
        Process a message and update memory accordingly.
        
        Args:
            message: The message text
            user_id: User ID
            is_user: Whether the message is from the user (True) or Grace (False)
            
        Returns:
            Dict with processing results
        """
        # Check for !grace.learn command
        if is_user and message.strip().startswith("!grace.learn"):
            try:
                result = self.memory_system.process_grace_learn_command(user_id, message)
                return {
                    "type": "command",
                    "result": result
                }
            except (PermissionError, ValueError) as e:
                return {
                    "type": "error",
                    "error": str(e)
                }
        
        # Extract entities
        entities = self._extract_entities(message)
        
        # Update active entities
        self.active_entities.update(entities)
        
        # Store in short-term memory
        metadata = {
            "is_user": is_user,
            "entities": list(entities),
            "timestamp": time.time()
        }
        
        memory_id = self.memory_system.add_to_short_term(
            user_id=user_id,
            text=message,
            metadata=metadata
        )
        
        # If it's a significant message, also store in medium-term
        if self._is_significant(message, entities):
            self.memory_system.add_to_medium_term(
                user_id=user_id,
                text=message,
                metadata=metadata
            )
        
        return {
            "type": "message",
            "memory_id": memory_id,
            "entities": list(entities)
        }
    
    def _extract_entities(self, text: str) -> set:
        """
        Extract entities from text.
        
        This is a simplified implementation. In a production system,
        this would use NER models or more sophisticated techniques.
        """
        # Simple regex-based entity extraction
        # Look for capitalized words, hashtags, and @mentions
        entities = set()
        
        # Capitalized words (potential named entities)
        for match in re.finditer(r'\b[A-Z][a-zA-Z]+\b', text):
            entities.add(match.group(0))
        
        # Hashtags
        for match in re.finditer(r'#(\w+)', text):
            entities.add(match.group(1))
        
        # @mentions
        for match in re.finditer(r'@(\w+)', text):
            entities.add(match.group(1))
        
        return entities
    
    def _is_significant(self, text: str, entities: set) -> bool:
        """
        Determine if a message is significant enough for medium-term storage.
        
        Criteria:
        - Contains entities
        - Contains questions
        - Contains important keywords
        - Longer than threshold
        """
        # Has entities
        if entities:
            return True
        
        # Contains question
        if '?' in text:
            return True
        
        # Contains important keywords
        important_keywords = ['remember', 'important', 'forget', 'key', 'critical', 'essential']
        if any(keyword in text.lower() for keyword in important_keywords):
            return True
        
        # Longer than threshold
        if len(text.split()) > 20:
            return True
        
        return False
    
    def get_relevant_context(self, query: str, user_id: str, max_items: int = 5) -> List[Dict[str, Any]]:
        """
        Get relevant context for a query from all memory layers.
        
        This method:
        1. Queries all memory layers
        2. Prioritizes results based on relevance and recency
        3. Returns a combined context
        """
        # Extract entities from query
        entities = self._extract_entities(query)
        
        # Update active entities
        self.active_entities.update(entities)
        
        # Query all memory types
        results = self.memory_system.query_memory(
            query=query,
            user_id=user_id,
            memory_types=["short_term", "medium_term", "long_term"],
            n_results=max_items * 2  # Get more results than needed for filtering
        )
        
        # If entities were found, also query by entity
        entity_results = []
        for entity in entities:
            entity_results.extend(self.memory_system.query_by_entity(entity, n_results=3))
        
        # Combine results
        all_results = results + entity_results
        
        # Remove duplicates
        unique_results = {}
        for result in all_results:
            if result["id"] not in unique_results:
                unique_results[result["id"]] = result
        
        # Sort by combined score of relevance and recency
        sorted_results = list(unique_results.values())
        sorted_results.sort(key=self._get_combined_score, reverse=True)
        
        # Return top results
        return sorted_results[:max_items]
    
    def _get_combined_score(self, result: Dict[str, Any]) -> float:
        """
        Calculate combined score based on relevance and recency.
        
        Formula: 0.7 * relevance + 0.3 * recency
        """
        relevance = result["relevance"]
        
        # Calculate recency (0-1 scale, 1 being most recent)
        timestamp = result["metadata"].get("timestamp", 0)
        current_time = time.time()
        time_diff = current_time - timestamp
        
        # Max age considered is 30 days
        max_age = 60 * 60 * 24 * 30
        recency = max(0, 1 - (time_diff / max_age))
        
        # Memory type bonus
        memory_type = result["metadata"].get("memory_type", "")
        type_bonus = 0
        if memory_type == "short_term":
            type_bonus = 0.2
        elif memory_type == "medium_term":
            type_bonus = 0.1
        
        # Calculate combined score
        return (0.6 * relevance) + (0.3 * recency) + type_bonus
    
    def update_entity_relationships(self):
        """Update relationships between entities based on co-occurrence."""
        # This is a simplified implementation
        # In a production system, this would use more sophisticated techniques
        
        # Get recent messages
        for collection_name, collection in self.memory_system.user_collections.items():
            # Query without order_by (which isn't supported in some ChromaDB versions)
            recent_messages = collection.query(
                query_texts=[""],
                where={"memory_type": "short_term"},
                n_results=100
            )
            
            # Sort manually by timestamp if needed
            if recent_messages["documents"] and recent_messages["documents"][0] and len(recent_messages["metadatas"]) > 0:
                # Create a list of (doc, metadata, id) tuples for sorting
                items = []
                for i, doc in enumerate(recent_messages["documents"][0]):
                    if i < len(recent_messages["metadatas"][0]) and "timestamp" in recent_messages["metadatas"][0][i]:
                        items.append((doc, recent_messages["metadatas"][0][i], recent_messages["ids"][0][i]))
                
                # Sort by timestamp (descending)
                items.sort(key=lambda x: x[1].get("timestamp", 0), reverse=True)
                
                # Rebuild the results structure
                if items:
                    recent_messages["documents"] = [[item[0] for item in items]]
                    recent_messages["metadatas"] = [[item[1] for item in items]]
                    recent_messages["ids"] = [[item[2] for item in items]]
            
            if not recent_messages["documents"] or not recent_messages["documents"][0]:
                continue
            
            # Process messages
            for i, doc in enumerate(recent_messages["documents"][0]):
                if i < len(recent_messages["metadatas"][0]) and "entities" in recent_messages["metadatas"][0][i]:
                    entities = recent_messages["metadatas"][0][i]["entities"]
                    
                    # Update co-occurrence
                    for j in range(len(entities)):
                        for k in range(j + 1, len(entities)):
                            entity1 = entities[j]
                            entity2 = entities[k]
                            
                            # Update relationship for entity1
                            if entity1 not in self.entity_relationships:
                                self.entity_relationships[entity1] = {}
                            
                            if entity2 not in self.entity_relationships[entity1]:
                                self.entity_relationships[entity1][entity2] = 0
                            
                            self.entity_relationships[entity1][entity2] += 1
                            
                            # Update relationship for entity2
                            if entity2 not in self.entity_relationships:
                                self.entity_relationships[entity2] = {}
                            
                            if entity1 not in self.entity_relationships[entity2]:
                                self.entity_relationships[entity2][entity1] = 0
                            
                            self.entity_relationships[entity2][entity1] += 1
    
    def get_related_entities(self, entity: str, max_entities: int = 5) -> List[Tuple[str, int]]:
        """Get entities related to a given entity."""
        if entity not in self.entity_relationships:
            return []
        
        # Sort by co-occurrence count
        related = [(e, count) for e, count in self.entity_relationships[entity].items()]
        related.sort(key=lambda x: x[1], reverse=True)
        
        return related[:max_entities]
    
    def generate_context_for_prompt(self, query: str, user_id: str, max_items: int = 5) -> str:
        """
        Generate context string for inclusion in LLM prompt.
        
        This formats relevant memories in a way that can be included
        in the prompt to the LLM.
        """
        relevant_context = self.get_relevant_context(query, user_id, max_items)
        
        if not relevant_context:
            return ""
        
        context_str = "Relevant information from memory:\n\n"
        
        for i, item in enumerate(relevant_context):
            memory_type = item["metadata"].get("memory_type", "unknown")
            source = "User" if item["metadata"].get("is_user", False) else "Grace"
            
            context_str += f"{i+1}. "
            
            # Add entity if available
            if "entity" in item["metadata"]:
                context_str += f"[{item['metadata']['entity']}] "
            
            # Add the memory text
            context_str += f"{item['text']}"
            
            # Add source and type
            context_str += f" (Source: {source}, Type: {memory_type})\n"
        
        return context_str

# Example usage
if __name__ == "__main__":
    # Create memory system
    memory_system = MemorySystem("./chroma_db", None)
    
    # Create memory bridge
    memory_bridge = MemoryBridgeSystem(memory_system)
    
    # Process some messages
    memory_bridge.process_message("Hello, I'm interested in learning about Bitcoin.", "user_1", True)
    memory_bridge.process_message("Bitcoin is a decentralized cryptocurrency created by Satoshi Nakamoto.", "user_1", False)
    
    # Get relevant context
    context = memory_bridge.get_relevant_context("Tell me about Bitcoin", "user_1")
    print("Relevant context:", context)
    
    # Generate context for prompt
    prompt_context = memory_bridge.generate_context_for_prompt("Tell me about Bitcoin", "user_1")
    print("\nPrompt context:\n", prompt_context)
