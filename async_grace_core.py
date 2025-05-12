"""
Asynchronous Grace Core - A crypto trading application based on Open Interpreter

This module extends the OpenInterpreter class to create AsyncGraceInterpreter,
which includes asynchronous memory system integration and crypto trading capabilities.
"""

import os
import sys
import json
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union

# Add Open Interpreter to path
sys.path.append('/home/ubuntu/open-interpreter')

# Import Open Interpreter
from interpreter import OpenInterpreter

# Import async memory system
from async_memory_system import create_memory_system

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("GraceCore")

class AsyncGraceInterpreter:
    """
    AsyncGraceInterpreter wraps OpenInterpreter with asynchronous memory system 
    integration and crypto trading capabilities.
    """
    
    def __init__(
        self,
        memory_persist_directory: str = "./chroma_db",
        **kwargs
    ):
        """
        Initialize AsyncGraceInterpreter with memory system and other capabilities.
        
        Args:
            memory_persist_directory: Directory to store memory database
            **kwargs: Additional arguments to pass to OpenInterpreter
        """
        # Initialize base OpenInterpreter
        self.interpreter = OpenInterpreter(**kwargs)
        
        # Memory system components (will be initialized in setup)
        self.memory_manager = None
        self.entity_linker = None
        self.memory_router = None
        self.memory_persist_directory = memory_persist_directory
        
        # Current user context
        self.current_user = None
        
        # Disclosure shown status
        self.disclosure_shown = {}  # Track by username
        
        # Lock for thread safety
        self._lock = asyncio.Lock()
        
        # Customize system message to include Grace-specific capabilities
        self._extend_system_message()
    
    def _extend_system_message(self):
        """
        Extend the default system message with Grace-specific capabilities.
        """
        grace_extension = """
You are Grace, an advanced AI assistant built on Open Interpreter with crypto trading capabilities.

You can:
1. Execute code and perform computer tasks with full system access
2. Connect to and trade through Phantom wallet
3. Manage internal crypto wallets
4. Access and utilize your sophisticated memory system
5. Learn and remember information specific to each user

When using your memory system:
- You can bridge new information to existing knowledge
- You maintain separate memory spaces for each user
- You can recall information naturally in conversations
- Authorized users can update your global memory with the !grace.learn command

For crypto trading:
- You can connect to Phantom wallet when requested
- You can create and manage internal wallets
- You can execute trades on Solana-based tokens
- You can provide liquidity pool trading through Raydium DEX
- You can implement auto-trading with risk-based settings

Always prioritize user security and provide helpful, accurate information.
"""
        
        # Append Grace-specific extension to system message
        self.interpreter.system_message = self.interpreter.system_message + "\n\n" + grace_extension
    
    async def setup(self):
        """
        Asynchronously set up the memory system.
        Must be called before using any memory-related features.
        """
        try:
            # Initialize memory system
            self.memory_manager, self.entity_linker, self.memory_router = await create_memory_system(
                persist_directory=self.memory_persist_directory
            )
            logger.info("Memory system initialized successfully")
        except Exception as e:
            logger.error(f"Error setting up memory system: {str(e)}")
            raise
    
    async def set_user(self, username: str):
        """
        Set the current user context for memory operations.
        
        Args:
            username: Username to set as current user
        """
        async with self._lock:
            self.current_user = username
            logger.info(f"User context set to: {username}")
    
    async def show_disclosure(self):
        """
        Show the one-time disclosure about system capabilities.
        
        Returns:
            str or False: Disclosure text if shown, False if already shown
        """
        if not self.current_user:
            return False
        
        async with self._lock:
            if self.current_user not in self.disclosure_shown:
                disclosure_text = """
IMPORTANT DISCLOSURE:

Grace has full access to execute code and perform tasks on your computer system.
This includes the ability to:
- Run any code or command
- Access files and system resources
- Connect to the internet and external services
- Interact with your Phantom wallet when authorized

By continuing to use Grace, you acknowledge and accept these capabilities.
Your security and privacy remain a priority, and all operations are performed
only with your explicit permission.

This notice will only be shown once.
"""
                self.disclosure_shown[self.current_user] = True
                return disclosure_text
        
        return False
    
    async def chat(self, message=None, display=True, stream=False):
        """
        Asynchronous chat method that integrates memory system.
        
        Args:
            message: User message
            display: Whether to display the response
            stream: Whether to stream the response
            
        Returns:
            Response from the model
        """
        # Check if memory system is initialized
        if not self.memory_manager:
            logger.warning("Memory system not initialized. Call setup() first.")
            return await self._call_interpreter_chat(message, display, stream)
        
        # Process message through memory system if it's a string
        if isinstance(message, str) and self.current_user:
            # Check if it's a command
            is_command = message.startswith("!grace.learn")
            
            try:
                # Process through memory router
                memory_result = await self.memory_router.process_input(
                    text=message,
                    username=self.current_user,
                    is_command=is_command
                )
                
                # If it's a command that was processed successfully, handle it
                if is_command and memory_result.get("command_processed", False):
                    return [{"role": "assistant", "content": "Global memory updated successfully."}]
                
                # Enhance message with related memories if available
                if memory_result.get("related_memories"):
                    # Get the most relevant memories
                    relevant_memories = []
                    
                    # Add core memories
                    for memory in memory_result["related_memories"].get("core", [])[:2]:
                        relevant_memories.append(f"Core memory: {memory['text']}")
                    
                    # Add global memories (prioritize these)
                    for memory in memory_result["related_memories"].get("global", [])[:3]:
                        relevant_memories.append(f"Global memory: {memory['text']}")
                    
                    # Add user memories
                    for memory in memory_result["related_memories"].get("user", [])[:2]:
                        relevant_memories.append(f"Your memory: {memory['text']}")
                    
                    # If we have relevant memories, add them to the system message
                    if relevant_memories:
                        context_message = "\n\nRelevant context from memory:\n" + "\n".join(relevant_memories)
                        
                        # Temporarily extend system message with context
                        original_system_message = self.interpreter.system_message
                        self.interpreter.system_message = original_system_message + context_message
                        
                        # Call interpreter chat method
                        result = await self._call_interpreter_chat(message, display, stream)
                        
                        # Restore original system message
                        self.interpreter.system_message = original_system_message
                        
                        # Process response to update memory
                        await self.process_response(result)
                        
                        return result
            except Exception as e:
                logger.error(f"Error processing memory: {str(e)}")
                # Continue with normal chat if memory processing fails
        
        # If no memory processing or no relevant memories, just call interpreter method
        result = await self._call_interpreter_chat(message, display, stream)
        
        # Process response to update memory
        await self.process_response(result)
        
        return result
    
    async def _call_interpreter_chat(self, message, display, stream):
        """
        Call the OpenInterpreter chat method and wrap it in a coroutine.
        
        Args:
            message: User message
            display: Whether to display the response
            stream: Whether to stream the response
            
        Returns:
            Response from the model
        """
        # Create a future to store the result
        loop = asyncio.get_event_loop()
        
        # Run the blocking chat method in a thread pool
        return await loop.run_in_executor(
            None, 
            lambda: self.interpreter.chat(message=message, display=display, stream=stream, blocking=True)
        )
    
    async def process_response(self, response):
        """
        Process a response from the model to update memory.
        
        Args:
            response: Response from the model
            
        Returns:
            Processed response
        """
        # Extract text content from response
        if isinstance(response, list):
            content = ""
            for msg in response:
                if msg.get("role") == "assistant" and isinstance(msg.get("content"), str):
                    content += msg["content"] + "\n"
        elif isinstance(response, dict):
            content = response.get("content", "")
        elif isinstance(response, str):
            content = response
        else:
            return response
        
        # Only process if we have content and a current user
        if content and self.current_user and self.entity_linker:
            try:
                # Connect new information to memory
                await self.entity_linker.connect_new_information(content, self.current_user)
                logger.info(f"Response processed and added to memory for user: {self.current_user}")
            except Exception as e:
                logger.error(f"Error processing response for memory: {str(e)}")
        
        return response
    
    async def process_command(self, command_text, username):
        """
        Process a command directly.
        
        Args:
            command_text: Command text (e.g., "!grace.learn entity:update")
            username: Username issuing the command
            
        Returns:
            Dict: Command processing result
        """
        if not self.memory_router:
            return {"success": False, "error": "Memory system not initialized"}
        
        try:
            result = await self.memory_router.process_input(
                text=command_text,
                username=username,
                is_command=True
            )
            return result
        except Exception as e:
            logger.error(f"Error processing command: {str(e)}")
            return {"success": False, "error": str(e)}
