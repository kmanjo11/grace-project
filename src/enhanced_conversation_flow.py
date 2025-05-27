"""
Enhanced Conversation Flow for Grace - Inspired by FinGPT's approach to context management

This module implements a unified conversation flow that:
1. Maintains consistent context throughout the conversation
2. Uses RAG (Retrieval-Augmented Generation) to enhance responses
3. Integrates seamlessly with existing memory systems
4. Reduces framework switching for more fluid conversations
"""

import os
import json
import time
import logging
import asyncio
import inspect
import traceback
from typing import Dict, List, Any, Optional, Union, Callable

# Leverage Trading Integration
from src.leverage_trading_handler import LeverageTradeManager, LeverageTradeCondition

# Leverage Trading Integration
from src.leverage_trading_handler import LeverageTradeManager, LeverageTradeCondition
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("EnhancedConversationFlow")

class EnhancedConversationFlow:
    """
    Manages the enhanced conversation flow with unified context handling and RAG.
    """
    
    def __init__(
        self,
        grace_core,
        memory_system,
        gmgn_service,
        conversation_manager,
        interpreter,
        social_media_service=None
    ):
        """
        Initialize the enhanced conversation flow.
        
        Args:
            grace_core: Reference to the main GraceCore instance
            memory_system: The memory system (ChromaDB)
            gmgn_service: The GMGN service for financial data
            conversation_manager: The existing conversation manager
            interpreter: The Open Interpreter instance
        """
        self.grace_core = grace_core
        self.memory_system = memory_system
        self.gmgn_service = gmgn_service
        self.conversation_manager = conversation_manager
        self.social_media_service = social_media_service
        self.interpreter = interpreter
        self.logger = logging.getLogger("EnhancedConversationFlow")
        
        # Initialize Leverage Trade Manager with proper error handling
        try:
            self.leverage_trade_manager = LeverageTradeManager(
                gmgn_service=gmgn_service,
                memory_system=memory_system,
                logger=self.logger
            )
        except Exception as e:
            self.logger.error(
                f"Failed to initialize Leverage Trade Manager: {str(e)}",
                exc_info=True
            )
            # Create a dummy manager that will fail gracefully
            self.leverage_trade_manager = None
    
    async def process_message(self, user_id: str, session_id: str, message: str) -> str:
        """
        Process a message with the enhanced conversation flow.
        
        Args:
            user_id: User ID
            session_id: Session ID
            message: The user's message
            
        Returns:
            str: The response to the user
        """
        self.logger.info(f"Processing message from user {user_id} (session {session_id}): {message}")
        
        # 1. Handle special commands first (direct execution without framework switching)
        command_response = self._handle_special_commands(user_id, session_id, message)
        if command_response:
            return command_response
        
        # 2. Get or create conversation context
        context = await self._get_or_create_context(user_id, session_id)
        if not context:
            return "I'm having trouble accessing our conversation history. Let's start fresh."
        
        # 3. Process the message with the conversation manager to extract topics and entities
        processing_result = await self._process_with_conversation_manager(context.context_id, user_id, message)
        if not processing_result.get("success", False):
            self.logger.error(f"Error processing message with conversation manager: {processing_result}")
            return "I encountered an issue processing your message. Could you try rephrasing it?"
        
        # 4. Build the unified context object with all relevant information
        unified_context = await self._build_unified_context(
            user_id=user_id,
            session_id=session_id,
            context=context,
            message=message,
            processing_result=processing_result
        )
        
        # 5. Generate the response with the unified context
        response = await self._generate_response_with_context(unified_context, message)
        
        # 6. Extract and execute any actions from the response
        await self._execute_actions_from_response(response, unified_context)
        
        # 7. Update the conversation context with the response
        await self._update_context_with_response(context.context_id, user_id, response)
        
        return response
    
    def _handle_special_commands(self, user_id: str, session_id: str, message: str) -> Optional[str]:
        """
        Handle special commands like !grace.learn, !grace.remember, etc.
        Simplified version that directly executes commands without framework switching.
        """
        # Delegate to the existing handler for now
        # In the future, we can optimize this to avoid framework switching
        return self.grace_core._handle_special_commands(user_id, session_id, message)
    
    async def _get_or_create_context(self, user_id: str, session_id: str):
        """Get or create a conversation context."""
        try:
            # Check if the conversation manager has the get_or_create_context method
            if not hasattr(self.conversation_manager, 'get_or_create_context'):
                self.logger.warning("Conversation manager does not have get_or_create_context method")
                return None
            
            # Use our safe_call helper to handle both sync and async methods
            context = await self._safe_call(
                self.conversation_manager.get_or_create_context,
                user_id=user_id,
                session_id=session_id
            )
            
            # Handle case where the call failed
            if context is None:
                self.logger.error("Failed to get or create conversation context")
                
                # Try fallback methods if available
                if hasattr(self.conversation_manager, 'get_context'):
                    self.logger.info("Trying fallback to get_context method")
                    context = await self._safe_call(
                        self.conversation_manager.get_context,
                        user_id=user_id,
                        session_id=session_id
                    )
                    
                if context is None and hasattr(self.conversation_manager, 'create_context'):
                    self.logger.info("Trying fallback to create_context method")
                    context = await self._safe_call(
                        self.conversation_manager.create_context,
                        user_id=user_id,
                        session_id=session_id
                    )
            
            return context
        except Exception as e:
            self.logger.error(f"Error getting or creating context: {str(e)}")
            self.logger.error(traceback.format_exc())
            return None
    
    async def _process_with_conversation_manager(self, context_id: str, user_id: str, message: str):
        """Process the message with the conversation manager to extract topics and entities."""
        try:
            # Check if the conversation manager has the process_message method
            if not hasattr(self.conversation_manager, 'process_message'):
                self.logger.warning("Conversation manager does not have process_message method")
                return {"success": False, "error": "Conversation manager does not support message processing"}
            
            # Use our safe_call helper to handle both sync and async methods
            result = await self._safe_call(
                self.conversation_manager.process_message,
                context_id=context_id,
                user_id=user_id,
                message=message
            )
            
            # Handle case where the call failed
            if result is None:
                self.logger.error("Conversation manager process_message call failed")
                return {"success": False, "error": "Failed to process message"}
                
            return result
        except Exception as e:
            self.logger.error(f"Error processing with conversation manager: {str(e)}")
            self.logger.error(traceback.format_exc())
            return {"success": False, "error": str(e)}
    
    async def _build_unified_context(self, user_id: str, session_id: str, context, message: str, processing_result: Dict):
        """
        Build a unified context object with all relevant information.
        This is the key to the enhanced conversation flow - gathering all context in one place.
        """
        # 1. Get relevant memories
        memories = await self._retrieve_relevant_memories(user_id, message)
        
        # 2. Get conversation history
        history = context.history if hasattr(context, 'history') else []
        
        # 3. Get active topics
        active_topics = context.get_active_topics() if hasattr(context, 'get_active_topics') else []
        
        # 4. Get relevant financial data for active topics
        financial_data = await self._retrieve_financial_data(user_id, message, active_topics)
        
        # 5. Get relevant social media data if available
        social_data = await self._retrieve_social_media_data(user_id, message, active_topics) if self.social_media_service else {}
        
        # 6. Get user profile
        user_profile = await self._get_user_profile(user_id)
        
        # Build the unified context
        unified_context = {
            "user_id": user_id,
            "session_id": session_id,
            "context_id": context.context_id if hasattr(context, 'context_id') else str(uuid.uuid4()),
            "message": message,
            "history": history,
            "memories": memories,
            "active_topics": active_topics,
            "financial_data": financial_data,
            "social_data": social_data,
            "user_profile": user_profile,
            "processing_result": processing_result,
            "timestamp": time.time()
        }
        
        return unified_context
    
    async def _retrieve_relevant_memories(self, user_id: str, message: str):
        """Retrieve relevant memories from ChromaDB."""
        try:
            if not self.memory_system:
                return []
                
            # Use the memory system to retrieve relevant memories
            if hasattr(self.memory_system, 'search_memories'):
                memories = self.memory_system.search_memories(
                    user_id=user_id,
                    query=message,
                    limit=5  # Limit to 5 most relevant memories
                )
                return memories
            else:
                self.logger.warning("Memory system does not have search_memories method")
                return []
                
        except Exception as e:
            self.logger.error(f"Error retrieving memories: {str(e)}")
            self.logger.error(traceback.format_exc())
            return []
    
    async def _retrieve_financial_data(self, user_id: str, message: str, active_topics):
        """Retrieve relevant financial data based on the message and active topics."""
        financial_data = {}
        
        try:
            # Extract potential token symbols from the message
            token_symbols = self._extract_token_symbols(message)
            
            # Check if any topics are related to trading or prices
            trading_related = False
            for topic in active_topics:
                if isinstance(topic, dict) and "name" in topic:
                    if topic["name"] in ["trading", "price", "token", "crypto"]:
                        trading_related = True
                        break
            
            # Check for smart trading related keywords
            smart_trading_keywords = ["smart trading", "automated trade", "stop loss", "take profit"]
            has_smart_trading_topic = any(keyword in message.lower() for keyword in smart_trading_keywords)
            
            # If trading related, get token prices
            if trading_related and token_symbols:
                price_data = {}
                for token in token_symbols:
                    try:
                        token_price = await self._safe_call(
                            self.gmgn_service.get_token_price,
                            token=token,
                            chain="sol",
                            timeframe="1d",
                            user_id=user_id
                        )
                        if token_price:
                            price_data[token] = token_price
                    except Exception as e:
                        self.logger.error(f"Error getting price for {token}: {str(e)}")
                
                if price_data:
                    financial_data["token_prices"] = price_data
            
            # Check if any topics are related to wallets or balances
            wallet_related = False
            for topic in active_topics:
                if isinstance(topic, dict) and "name" in topic:
                    if topic["name"] in ["wallet", "balance", "account"]:
                        wallet_related = True
                        break
            
            # If wallet related, get wallet balances
            if wallet_related or "wallet" in message.lower():
                try:
                    wallet_data = await self._safe_call(
                        self.gmgn_service.get_wallet_balance,
                        user_id=user_id
                    )
                    if wallet_data:
                        financial_data["wallet_data"] = wallet_data
                except Exception as e:
                    self.logger.error(f"Error getting wallet balance: {str(e)}")
            
            # Get smart trading events if smart trading is mentioned
            if has_smart_trading_topic or "smart" in message.lower():
                try:
                    # Retrieve recent smart trading events from memory
                    if self.memory_system and hasattr(self.memory_system, 'query_memory'):
                        # Query for smart trading memories
                        smart_trading_query = "smart trading stop loss take profit"
                        smart_trading_memories = await self._safe_call(
                            self.memory_system.query_memory,
                            query=smart_trading_query,
                            user_id=user_id,
                            n_results=5  # Get the 5 most recent events
                        )
                        
                        if smart_trading_memories and len(smart_trading_memories) > 0:
                            trading_events = []
                            for memory in smart_trading_memories:
                                try:
                                    # Check if this is a smart trading memory
                                    metadata = memory.get('metadata', {})
                                    if metadata.get('event_type') == 'smart_trading_event':
                                        event_data = {
                                            'event': metadata.get('event'),
                                            'token': metadata.get('token'),
                                            'price': metadata.get('price'),
                                            'action': metadata.get('action'),
                                            'amount': metadata.get('amount'),
                                            'timestamp': metadata.get('timestamp'),
                                            'text': memory.get('text', '')
                                        }
                                        trading_events.append(event_data)
                                except Exception as parse_err:
                                    self.logger.warning(f"Error parsing smart trading memory: {str(parse_err)}")
                            
                            if trading_events:
                                financial_data["smart_trading_events"] = trading_events
                except Exception as e:
                    self.logger.warning(f"Error retrieving smart trading events: {str(e)}")
            
            # Get market sentiment if relevant
            sentiment_related = False
            for topic in active_topics:
                if isinstance(topic, dict) and "name" in topic:
                    if topic["name"] in ["sentiment", "market", "news"]:
                        sentiment_related = True
                        break
            
            if sentiment_related and token_symbols:
                sentiment_data = {}
                for token in token_symbols:
                    try:
                        sentiment = await self._safe_call(
                            self.gmgn_service.get_token_sentiment,
                            token=token,
                            user_id=user_id
                        )
                        if sentiment:
                            sentiment_data[token] = sentiment
                    except Exception as e:
                        self.logger.error(f"Error getting sentiment for {token}: {str(e)}")
                
                if sentiment_data:
                    financial_data["sentiment_data"] = sentiment_data
            
        except Exception as e:
            self.logger.error(f"Error retrieving financial data: {str(e)}")
        
        return financial_data
    
    async def _retrieve_social_media_data(self, user_id: str, message: str, active_topics):
        """Retrieve relevant social media data based on the message and active topics."""
        social_data = {}
        
        try:
            # Check if any topics are related to social media
            social_media_related = False
            for topic in active_topics:
                if isinstance(topic, dict) and "name" in topic:
                    if topic["name"] in ["social", "media", "twitter", "facebook", "instagram"]:
                        social_media_related = True
                        break
            
            # If social media related, get social media data
            if social_media_related or "social" in message.lower():
                try:
                    social_media_data = await self._safe_call(
                        self.social_media_service.get_social_media_data,
                        user_id=user_id
                    )
                    if social_media_data:
                        social_data["social_media_data"] = social_media_data
                except Exception as e:
                    self.logger.error(f"Error getting social media data: {str(e)}")
            
            # Get social media sentiment if relevant
            sentiment_related = False
            for topic in active_topics:
                if isinstance(topic, dict) and "name" in topic:
                    if topic["name"] in ["sentiment", "market", "news"]:
                        sentiment_related = True
                        break
            
            if sentiment_related:
                sentiment_data = {}
                try:
                    sentiment = await self._safe_call(
                        self.social_media_service.get_social_media_sentiment,
                        user_id=user_id
                    )
                    if sentiment:
                        sentiment_data["social_media_sentiment"] = sentiment
                except Exception as e:
                    self.logger.error(f"Error getting social media sentiment: {str(e)}")
                
                if sentiment_data:
                    social_data["sentiment_data"] = sentiment_data
            
        except Exception as e:
            self.logger.error(f"Error retrieving social media data: {str(e)}")
        
        return social_data
    
    def _extract_token_symbols(self, message: str):
        """Extract potential token symbols from the message."""
        # Common crypto tokens
        common_tokens = ["BTC", "ETH", "SOL", "USDT", "USDC", "BNB", "XRP", "ADA", "DOGE"]
        
        # Extract tokens mentioned in the message
        tokens = []
        words = message.upper().split()
        
        for word in words:
            # Clean the word of punctuation
            clean_word = re.sub(r'[^\w]', '', word)
            if clean_word in common_tokens:
                tokens.append(clean_word)
        
        return tokens
    
    async def _safe_call(self, func, *args, **kwargs):
        """Safely call a function regardless of whether it's sync or async."""
        try:
            if func is None:
                return None
                
            # Check if it's an async function
            if asyncio.iscoroutinefunction(func):
                self.logger.debug(f"Calling async function {func.__name__}")
                return await func(*args, **kwargs)
            else:
                self.logger.debug(f"Calling sync function {func.__name__}")
                return func(*args, **kwargs)
        except Exception as e:
            self.logger.error(f"Error calling function {getattr(func, '__name__', 'unknown')}: {str(e)}")
            self.logger.error(traceback.format_exc())
            return None
    
    async def _get_user_profile(self, user_id: str):
        """Get the user profile information."""
        try:
            if hasattr(self.grace_core, 'user_profile_system'):
                user_profile = self.grace_core.user_profile_system.get_user_profile(user_id)
                return user_profile
        except Exception as e:
            self.logger.error(f"Error getting user profile: {str(e)}")
        
        return {}
    
    async def _generate_response_with_context(self, unified_context, message=None):
        """
        Generate a response using the unified context.
        This is where we format all the context into a prompt for the LLM.
        
        Args:
            unified_context: The unified context object containing all relevant information
            message: Optional original message text (if not included in unified_context)
        """
        # Use message from unified_context if not provided
        if message is None and "message" in unified_context:
            message = unified_context["message"]
            
        # Extract components for the prompt
        history = unified_context.get("history", [])
        memories = unified_context.get("memories", [])
        financial_data = unified_context.get("financial_data", {})
        social_data = unified_context.get("social_data", {})
        active_topics = unified_context.get("active_topics", [])
        
        # 1. Format the conversation history
        formatted_history = self._format_conversation_history(history)
        
        # 2. Format the memories
        formatted_memories = self._format_memories(memories)
        
        # 3. Format the financial data
        formatted_financial_data = self._format_financial_data(financial_data)
        
        # 4. Format social media data
        formatted_social_data = self._format_social_media_data(social_data)
        
        # 5. Format active topics
        formatted_topics = self._format_topics(active_topics)
        
        # Build the prompt with all context sections
        prompt = f"""
        [CONVERSATION HISTORY]
        {formatted_history}
        
        [USER MEMORIES]
        {formatted_memories}
        
        [FINANCIAL DATA]
        {formatted_financial_data}
        
        [SOCIAL MEDIA INSIGHTS]
        {formatted_social_data}
        
        [ACTIVE TOPICS]
        {formatted_topics}
        
        [CURRENT MESSAGE]
        User: {message}
        
        Based on the above context, generate a helpful response.
        """
        try:
            # Set the enhanced prompt
            enhanced_prompt = prompt
            
            # 6. Prepare messages for the interpreter - ensure proper format with 'type' field
            # Open Interpreter expects messages in a specific format with 'type' field
            system_message = self.grace_core._get_grace_system_message() if hasattr(self.grace_core, '_get_grace_system_message') else ""

            # 7. Generate response with the interpreter
            self.logger.info("Generating response with enhanced context")

            # Use our safe_call helper to handle both sync and async methods
            # Pass the enhanced prompt directly instead of a messages array
            response = await self._safe_call(self.interpreter.chat, enhanced_prompt)
            
            # Handle case where the call failed
            if response is None:
                self.logger.error("Interpreter chat call failed")
                return "I'm having trouble generating a response right now. Could you try again?"
            
            # Handle different response formats
            if isinstance(response, dict):
                # Extract the actual response text from the dictionary
                if 'content' in response:
                    return response['content']
                elif 'message' in response:
                    return response['message']
                elif 'response' in response:
                    return response['response']
                else:
                    # Return the whole dictionary as a string if we can't extract a specific field
                    return str(response)
            elif isinstance(response, list) and len(response) > 0:
                # If it's a list, try to get the last message
                last_msg = response[-1]
                if isinstance(last_msg, dict) and 'content' in last_msg:
                    return last_msg['content']
                else:
                    return str(last_msg)
            
            # If it's already a string or another simple type, return it directly
            return str(response)
            
        except Exception as e:
            self.logger.error(f"Error generating response: {str(e)}")
            return "I'm having trouble generating a response right now. Could you try again?"
    
    def _format_conversation_history(self, history):
        """Format the conversation history for inclusion in the prompt."""
        if not history:
            return "No previous conversation history."
        
        # Get the last few messages (most recent first)
        recent_history = list(history)[-5:]
        
        formatted_history = ""
        for msg in recent_history:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            formatted_history += f"{role.capitalize()}: {content}\n"
        
        return formatted_history
    
    def _format_memories(self, memories):
        """Format the memories for inclusion in the prompt."""
        if not memories:
            return ""
        
        # Handle different possible memory structures
        try:
            # Check if memories is a dictionary with results inside
            if isinstance(memories, dict) and "results" in memories:
                memories = memories["results"]
            
            # Check if it's a list of documents from ChromaDB
            if isinstance(memories, list) and len(memories) > 0 and isinstance(memories[0], dict):
                formatted_memories = "Relevant information from memory:\n"
                
                for i, memory in enumerate(memories):
                    # Handle ChromaDB document format
                    if "document" in memory:
                        formatted_memories += f"- {memory['document']}\n"
                    # Handle standard text field
                    elif "text" in memory:
                        formatted_memories += f"- {memory['text']}\n"
                    # Handle content field
                    elif "content" in memory:
                        formatted_memories += f"- {memory['content']}\n"
                    # Handle metadata with text
                    elif "metadata" in memory and isinstance(memory["metadata"], dict):
                        metadata = memory["metadata"]
                        if "text" in metadata:
                            formatted_memories += f"- {metadata['text']}\n"
                        elif "content" in metadata:
                            formatted_memories += f"- {metadata['content']}\n"
                        else:
                            # Use a relevant field from metadata if available
                            relevant_fields = ["summary", "description", "title", "info"]
                            for field in relevant_fields:
                                if field in metadata and metadata[field]:
                                    formatted_memories += f"- {metadata[field]}\n"
                                    break
                            else:
                                # If no relevant field found, use the whole metadata
                                formatted_memories += f"- Memory {i+1}: {str(metadata)}\n"
                    else:
                        # Generic fallback for other dictionary formats
                        formatted_memories += f"- Memory {i+1}: {str(memory)}\n"
            elif isinstance(memories, str):
                # Handle string format
                formatted_memories = f"Relevant information from memory:\n- {memories}\n"
            else:
                # Generic fallback for other formats
                formatted_memories = "Relevant information from memory:\n"
                for i, memory in enumerate(memories):
                    formatted_memories += f"- Memory {i+1}: {str(memory)}\n"
                    
            return formatted_memories
        except Exception as e:
            self.logger.error(f"Error formatting memories: {str(e)}")
            self.logger.error(traceback.format_exc())
            return ""  # Return empty string on error
    
    def _format_financial_data(self, financial_data):
        """Format the financial data for inclusion in the prompt."""
        if not financial_data:
            return ""
        
        formatted_data = "Financial information:\n"
        
        # Format token prices
        if "token_prices" in financial_data and financial_data["token_prices"]:
            formatted_data += "Token prices:\n"
            for token, price_data in financial_data["token_prices"].items():
                if isinstance(price_data, dict) and "price" in price_data:
                    price = price_data["price"]
                    change = price_data.get("price_change_24h", "unknown")
                    formatted_data += f"- {token}: ${price} (24h change: {change}%)\n"
                else:
                    formatted_data += f"- {token}: {price_data}\n"
        
        # Format wallet data
        if "wallet_data" in financial_data and financial_data["wallet_data"]:
            wallet_data = financial_data["wallet_data"]
            formatted_data += "Wallet information:\n"
            
            if "wallets" in wallet_data:
                for wallet in wallet_data["wallets"]:
                    addr = wallet.get("address", "unknown")
                    wallet_type = wallet.get("type", "unknown")
                    balance = wallet.get("balance", {})
                    
                    # Safely format the address with proper length checking
                    if isinstance(addr, str) and len(addr) > 10:
                        addr_display = f"{addr[:6]}...{addr[-4:]}"
                    else:
                        addr_display = addr
                    
                    formatted_data += f"- {wallet_type.capitalize()} wallet ({addr_display}): "
                    
                    # Safely format the balance
                    if balance and isinstance(balance, dict):
                        balance_parts = []
                        for currency, amount in balance.items():
                            if currency and amount is not None:
                                balance_parts.append(f"{amount} {str(currency).upper()}")
                        if balance_parts:
                            formatted_data += ", ".join(balance_parts)
                        else:
                            formatted_data += "No balance information"
                    else:
                        formatted_data += "No balance information"
                    
                    formatted_data += "\n"
            elif "balance" in wallet_data:
                balance = wallet_data["balance"]
                for currency, amount in balance.items():
                    formatted_data += f"- {amount} {currency.upper()}\n"
        
        # Format sentiment data
        if "sentiment_data" in financial_data and financial_data["sentiment_data"]:
            formatted_data += "Market sentiment:\n"
            for token, sentiment in financial_data["sentiment_data"].items():
                if isinstance(sentiment, dict):
                    score = sentiment.get("sentiment_score", "unknown")
                    label = sentiment.get("sentiment", "unknown")
                    formatted_data += f"- {token}: {label} (score: {score})\n"
                else:
                    formatted_data += f"- {token}: {sentiment}\n"
        
        # Format smart trading events
        if "smart_trading_events" in financial_data and financial_data["smart_trading_events"]:
            formatted_data += "\nRecent Smart Trading Activity:\n"
            for event in financial_data["smart_trading_events"]:
                if isinstance(event, dict):
                    event_type = event.get("event", "unknown")
                    token = event.get("token", "unknown")
                    price = event.get("price", "unknown")
                    action = event.get("action", "unknown")
                    amount = event.get("amount", "unknown")
                    timestamp = event.get("timestamp", "")
                    
                    # Format the timestamp if present
                    time_str = ""
                    if timestamp:
                        try:
                            from datetime import datetime
                            dt = datetime.fromisoformat(timestamp)
                            time_str = f" on {dt.strftime('%Y-%m-%d at %H:%M')}"
                        except Exception:
                            # If timestamp parsing fails, just use the raw string
                            time_str = f" on {timestamp}"
                    
                    if event_type == "stop_loss_triggered":
                        formatted_data += f"- Stop Loss triggered for {token} at ${price}{time_str}. Action: {action} {amount} {token}\n"
                    elif event_type == "take_profit_triggered":
                        formatted_data += f"- Take Profit triggered for {token} at ${price}{time_str}. Action: {action} {amount} {token}\n"
                    else:
                        formatted_data += f"- {event_type} for {token} at ${price}{time_str}. Action: {action} {amount} {token}\n"
        
        return formatted_data
    
    def _format_topics(self, topics):
        """Format the active topics for inclusion in the prompt."""
        if not topics:
            return "No active topics"
            
        return ", ".join([t.get('name', t) if isinstance(t, dict) else t for t in topics])
        
    def _format_social_media_data(self, social_data):
        """Format the social media data for inclusion in the prompt."""
        if not social_data:
            return "No relevant social media data available."
            
        formatted_data = ["Relevant social media insights:"]
        
        # Format trending topics
        if social_data.get("trending_topics"):
            topics = social_data["trending_topics"].get("topics", [])
            if topics:
                formatted_data.append("\nTrending Topics:")
                for i, topic in enumerate(topics[:5], 1):
                    if isinstance(topic, dict) and 'name' in topic:
                        formatted_data.append(f"  {i}. {topic['name']}")
                    elif isinstance(topic, str):
                        formatted_data.append(f"  {i}. {topic}")
        
        # Format sentiment analysis
        if social_data.get("sentiment_analysis"):
            formatted_data.append("\nSentiment Analysis:")
            for term, analysis in social_data["sentiment_analysis"].items():
                sentiment = analysis.get("sentiment", "neutral")
                confidence = analysis.get("confidence", 0.0)
                sample_size = analysis.get("sample_size", 0)
                formatted_data.append(f"  {term}: {sentiment.capitalize()} (confidence: {confidence:.2f}, based on {sample_size} posts)")
        
        # Format influential accounts
        if social_data.get("influential_accounts"):
            formatted_data.append("\nInfluential Accounts:")
            for entity, accounts_data in social_data["influential_accounts"].items():
                formatted_data.append(f"  For {entity}:")
                accounts = accounts_data.get("accounts", [])
                for i, account in enumerate(accounts[:3], 1):
                    if isinstance(account, dict):
                        username = account.get('username', 'Unknown')
                        followers = account.get('followers', 0)
                        formatted_data.append(f"    {i}. @{username} ({followers:,} followers)")
        
        return "\n".join(formatted_data) if len(formatted_data) > 1 else "No relevant social media data available."
    
    async def _execute_actions_from_response(self, response, unified_context):
        """
        Extract and execute any actions from the response.
        This allows for direct execution of simple tasks without framework switching.
        
        The method analyzes the response text to identify potential actions like:
        - Price checks
        - Wallet balance requests
        - Token swaps
        - Market sentiment analysis
        
        When detected, it executes these actions directly without going through the agent framework.
        Results are stored in the conversation context for future reference.
        """
        try:
            self.logger.debug("Analyzing response for potential actions")
            
            # Get the user ID and context ID
            user_id = unified_context.get("user_id")
            context_id = unified_context.get("context_id")
            
            if not user_id or not context_id:
                self.logger.warning("Missing user_id or context_id, cannot execute actions")
                return
            
            # Extract potential actions using regex patterns and considering active topics
            actions = await self._extract_actions_from_text(response, unified_context)
            
            if not actions:
                self.logger.debug("No actions detected in response")
                return
                
            self.logger.info(f"Detected {len(actions)} potential actions in response")
            
            # Execute each detected action
            for action in actions:
                await self._execute_single_action(action, user_id, context_id)
                
        except Exception as e:
            self.logger.error(f"Error executing actions from response: {str(e)}")
            self.logger.error(traceback.format_exc())
    
    async def _extract_actions_from_text(self, text, unified_context=None):
        """
        Extract potential actions from response text using regex patterns.
        
        Args:
            text: The text to analyze for potential actions
            unified_context: Optional unified context object to consider active topics
        """
        actions = []
        active_tokens = set()
        
        # Extract active tokens from the unified context if available
        if unified_context and "active_topics" in unified_context:
            active_topics = unified_context.get("active_topics", [])
            for topic in active_topics:
                if isinstance(topic, dict) and "name" in topic:
                    topic_name = topic["name"].upper()
                    # Check if it's a token
                    if topic_name in ["BTC", "ETH", "SOL", "USDT", "USDC", "BNB", "XRP", "ADA", "DOGE"]:
                        active_tokens.add(topic_name)
                elif isinstance(topic, str):
                    topic_name = topic.upper()
                    # Check if it's a token
                    if topic_name in ["BTC", "ETH", "SOL", "USDT", "USDC", "BNB", "XRP", "ADA", "DOGE"]:
                        active_tokens.add(topic_name)
        
        # Define regex patterns for different action types
        price_check_patterns = [
            r"(?:price|value|worth)\s+of\s+([A-Za-z0-9]+)",
            r"([A-Za-z0-9]+)\s+(?:price|value|worth)",
            r"how\s+much\s+is\s+([A-Za-z0-9]+)\s+worth",
            r"current\s+(?:price|value)\s+(?:of)?\s+([A-Za-z0-9]+)"
        ]
        
        wallet_check_patterns = [
            r"(?:wallet|balance)\s+(?:info|information|details|status)",
            r"check\s+(?:your|the|my)\s+(?:wallet|balance)",
            r"how\s+much\s+(?:do\s+you|do\s+I|I)\s+have",
            r"what(?:'s|\s+is)\s+(?:my|in\s+my)\s+(?:wallet|balance)"
        ]
        
        sentiment_check_patterns = [
            r"(?:sentiment|feeling|mood)\s+(?:about|for|on)\s+([A-Za-z0-9]+)",
            r"(?:market|community)\s+(?:sentiment|feeling|mood)",
            r"how\s+(?:people|investors|the\s+market)\s+(?:feel|feels)\s+about\s+([A-Za-z0-9]+)",
            r"(?:bullish|bearish)\s+(?:on|about)\s+([A-Za-z0-9]+)"
        ]
        
        # Common crypto tokens
        common_tokens = ["BTC", "ETH", "SOL", "USDT", "USDC", "BNB", "XRP", "ADA", "DOGE"]
        
        # Leverage trade patterns
        leverage_trade_patterns = [
            r"(?:open|create|start)\s+(?:a|an)?\s+(\d+)x\s+(long|short)\s+(?:position|trade)\s+(?:on|for)\s+([A-Za-z0-9]+)",
            r"(long|short)\s+([A-Za-z0-9]+)\s+(?:at|with)\s+(\d+)x\s+leverage",
            r"leverage\s+trade\s+(\d+)x\s+(long|short)\s+([A-Za-z0-9]+)",
            r"(\d+)x\s+(long|short)\s+(?:position|trade)\s+(?:on|for)\s+([A-Za-z0-9]+)"
        ]
        
        # Check for leverage trade actions
        for pattern in leverage_trade_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match.groups()) >= 2:  # At least leverage and direction
                    actions.append({
                        "type": "leverage_trade",
                        "request": match.group(0)  # Use the full matched text as the request
                    })
        
        # Check for price check actions
        for pattern in price_check_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match.groups()) > 0:
                    token = match.group(1).upper()
                    # Consider common crypto tokens
                    if token in common_tokens:
                        actions.append({
                            "type": "price_check",
                            "token": token
                        })
        
        # Check for wallet check actions
        for pattern in wallet_check_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                actions.append({
                    "type": "wallet_check"
                })
                break  # Only need one wallet check
        
        # Check for sentiment check actions
        for pattern in sentiment_check_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match.groups()) > 0:
                    token = match.group(1).upper()
                    # Consider common crypto tokens
                    if token in common_tokens:
                        actions.append({
                            "type": "sentiment_check",
                            "token": token
                        })
                else:
                    # General market sentiment
                    actions.append({
                        "type": "sentiment_check",
                        "token": None  # General market sentiment
                    })
        
        # Add price checks for active tokens in the conversation
        for token in active_tokens:
            # Check if we already have a price check for this token
            if token in common_tokens and not any(a.get("type") == "price_check" and a.get("token") == token for a in actions):
                actions.append({
                    "type": "price_check",
                    "token": token,
                    "source": "active_topic"  # Mark that this came from an active topic
                })
        
        return actions
    
    async def _execute_single_action(self, action, user_id, context_id):
        """
        Execute a single detected action.
        """
        try:
            action_type = action.get("type")
            
            if action_type == "price_check":
                token = action.get("token")
                if not token:
                    self.logger.warning("Missing token for price check action")
                    return
                
                self.logger.info(f"Executing price check for {token}")
                
                # First, try to use the GMGN service to get the token price
                price_data = None
                
                # Check if we have the GMGN service and it has the get_token_price method
                if self.gmgn_service and hasattr(self.gmgn_service, 'get_token_price'):
                    self.logger.debug(f"Using GMGN service for price check of {token}")
                    price_data = await self._safe_call(
                        self.gmgn_service.get_token_price,
                        token=token,
                        chain="sol",  # Default to Solana chain
                        timeframe="1d"
                    )
                
                # If GMGN service failed or doesn't exist, try using the financial data service
                if not price_data and hasattr(self.grace_core, 'financial_data_service'):
                    financial_service = self.grace_core.financial_data_service
                    if hasattr(financial_service, 'get_price'):
                        self.logger.debug(f"Using financial data service for price check of {token}")
                        price_data = await self._safe_call(
                            financial_service.get_price,
                            token=token
                        )
                
                # If both services failed, try using the agent framework as a fallback
                if not price_data and hasattr(self.grace_core, 'agent_manager'):
                    agent_manager = self.grace_core.agent_manager
                    if hasattr(agent_manager, 'execute_task'):
                        self.logger.debug(f"Using agent framework for price check of {token}")
                        price_data = await self._safe_call(
                            agent_manager.execute_task,
                            task_type="price_check",
                            params={"token": token},
                            user_id=user_id
                        )
                
                # If we got price data from any source, store it
                if price_data:
                    self.logger.info(f"Successfully retrieved price data for {token}")
                    await self._store_action_result(context_id, user_id, "price_check", {
                        "token": token,
                        "price_data": price_data,
                        "timestamp": time.time()
                    })
                else:
                    self.logger.warning(f"Failed to retrieve price data for {token} from any available service")
            
            elif action_type == "wallet_check":
                self.logger.info(f"Executing wallet check for user {user_id}")
                
                # Get the user's wallet address from the user profile or session
                wallet_address = None
                wallet_data = None
                
                # Try to get wallet address from user profile system
                if hasattr(self.grace_core, 'user_profile_system'):
                    user_profile = await self._safe_call(
                        self.grace_core.user_profile_system.get_user_profile,
                        user_id=user_id
                    )
                    
                    if user_profile and isinstance(user_profile, dict):
                        # Check different possible keys for wallet address
                        for key in ['wallet_address', 'address', 'wallet', 'sol_address', 'solana_address']:
                            if key in user_profile and user_profile[key]:
                                wallet_address = user_profile[key]
                                self.logger.debug(f"Found wallet address {wallet_address} in user profile")
                                break
                
                # Try to get wallet address from session manager if available
                if not wallet_address and hasattr(self.grace_core, 'session_manager'):
                    session = await self._safe_call(
                        self.grace_core.session_manager.get_session,
                        user_id=user_id
                    )
                    
                    if session and isinstance(session, dict):
                        # Check different possible keys for wallet address
                        for key in ['wallet_address', 'address', 'wallet', 'sol_address', 'solana_address']:
                            if key in session and session[key]:
                                wallet_address = session[key]
                                self.logger.debug(f"Found wallet address {wallet_address} in session")
                                break
                
                # Try different services to get wallet data
                
                # 1. First try GMGN service if available
                if self.gmgn_service:
                    if wallet_address and hasattr(self.gmgn_service, 'get_wallet_balance_by_address'):
                        self.logger.debug(f"Using GMGN service to get balance for address {wallet_address}")
                        wallet_data = await self._safe_call(
                            self.gmgn_service.get_wallet_balance_by_address,
                            address=wallet_address
                        )
                    elif hasattr(self.gmgn_service, 'get_wallet_balance'):
                        self.logger.debug(f"Using GMGN service to get balance for user {user_id}")
                        wallet_data = await self._safe_call(
                            self.gmgn_service.get_wallet_balance,
                            user_id=user_id
                        )
                
                # 2. Try wallet service if available
                if not wallet_data and hasattr(self.grace_core, 'wallet_service'):
                    wallet_service = self.grace_core.wallet_service
                    if wallet_address and hasattr(wallet_service, 'get_balance'):
                        self.logger.debug(f"Using wallet service to get balance for address {wallet_address}")
                        wallet_data = await self._safe_call(
                            wallet_service.get_balance,
                            address=wallet_address
                        )
                    elif hasattr(wallet_service, 'get_user_balance'):
                        self.logger.debug(f"Using wallet service to get balance for user {user_id}")
                        wallet_data = await self._safe_call(
                            wallet_service.get_user_balance,
                            user_id=user_id
                        )
                
                # 3. Try agent framework as a fallback
                if not wallet_data and hasattr(self.grace_core, 'agent_manager'):
                    agent_manager = self.grace_core.agent_manager
                    if hasattr(agent_manager, 'execute_task'):
                        params = {"user_id": user_id}
                        if wallet_address:
                            params["address"] = wallet_address
                            
                        self.logger.debug(f"Using agent framework to get wallet balance")
                        wallet_data = await self._safe_call(
                            agent_manager.execute_task,
                            task_type="wallet_check",
                            params=params,
                            user_id=user_id
                        )
                
                # If we got wallet data from any source, store it
                if wallet_data:
                    self.logger.info(f"Successfully retrieved wallet data for user {user_id}")
                    result_data = {
                        "wallet_data": wallet_data,
                        "timestamp": time.time()
                    }
                    
                    # Include the wallet address if we have it
                    if wallet_address:
                        result_data["wallet_address"] = wallet_address
                        
                    await self._store_action_result(context_id, user_id, "wallet_check", result_data)
                else:
                    self.logger.warning(f"Failed to retrieve wallet data for user {user_id} from any available service")
            
            elif action_type == "sentiment_check":
                token = action.get("token")
                self.logger.info(f"Executing sentiment check for {token or 'market'}")
                
                # Implement sentiment check logic
                # This could involve calling an external API or using internal sentiment analysis
                # For now, we'll just log it
                return
            
            elif action_type == "leverage_trade":
                request = action.get("request")
                self.logger.info(f"Processing leverage trade request: {request}")
                
                # Use the leverage trade manager to process the request
                trade_result = await self._handle_leverage_trade_request(
                    user_id=user_id,
                    request=request
                )
                
                # Log the result and potentially store in context
                if trade_result['success']:
                    self.logger.info(f"Leverage trade processed successfully: {trade_result['message']}")
                else:
                    self.logger.warning(f"Leverage trade processing failed: {trade_result['message']}")
                
                return
            
        except Exception as e:
            self.logger.error(f"Error executing action {action}: {str(e)}")
            self.logger.error(traceback.format_exc())
    
    async def _store_action_result(self, context_id, user_id, action_type, result):
        """
        Store an action result in the conversation context.
        """
        try:
            # Get the context
            context = await self._safe_call(
                self.conversation_manager.get_context,
                context_id=context_id,
                user_id=user_id
            )
            
            if not context:
                self.logger.warning(f"Context {context_id} not found for storing action result")
                return
            
            # Check if the context has a background_tasks attribute
            if not hasattr(context, 'background_tasks'):
                self.logger.warning(f"Context {context_id} does not have background_tasks attribute")
                return
            
            # Generate a task ID
            task_id = f"{action_type}_{int(time.time())}_{id(result)}"
            
            # Store the result in the background_tasks dictionary
            if hasattr(context, 'add_background_task'):
                # Use the add_background_task method if available
                if asyncio.iscoroutinefunction(context.add_background_task):
                    await context.add_background_task(task_id, action_type, "completed", result)
                else:
                    context.add_background_task(task_id, action_type, "completed", result)
            else:
                # Directly update the background_tasks dictionary
                context.background_tasks[task_id] = {
                    "type": action_type,
                    "status": "completed",
                    "created_at": time.time(),
                    "updated_at": time.time(),
                    "data": result
                }
            
            # Save the context
            await self._safe_call(
                self.conversation_manager.save_context,
                context=context
            )
            
            self.logger.debug(f"Stored action result for {action_type} in context {context_id}")
            
        except Exception as e:
            self.logger.error(f"Error storing action result: {str(e)}")
            self.logger.error(traceback.format_exc())
    
    async def _handle_leverage_trade_request(self, user_id: str, request: str) -> Dict[str, Any]:
        """
        Handle a leverage trade request.
        
        Args:
            user_id: User ID
            request: Natural language trade request
            
        Returns:
            Dict with success status and message
        """
        try:
            self.logger.info(f"Handling leverage trade request from user {user_id}: {request}")
            
            # Parse the trade request
            trade_condition = self.leverage_trade_manager.parse_trade_request(user_id, request)
            
            if not trade_condition:
                self.logger.warning(f"Failed to parse leverage trade request: {request}")
                return {
                    'success': False,
                    'message': 'Failed to parse leverage trade request. Please try again with a clearer format.'
                }
            
            # Add the trade condition
            result = self.leverage_trade_manager.add_trade_condition(trade_condition)
            
            # Log the result
            if result.get('success', False):
                self.logger.info(f"Successfully added leverage trade condition: {result.get('trade_condition')}")
                
                # Format a user-friendly response
                trade_info = result.get('trade_condition', {})
                market = trade_info.get('market', 'Unknown')
                side = trade_info.get('side', 'Unknown')
                leverage = trade_info.get('leverage', 0)
                
                entry_condition = trade_info.get('entry_condition', {})
                exit_condition = trade_info.get('exit_condition', {})
                
                entry_desc = ''
                if 'price_below' in entry_condition:
                    entry_desc = f"below ${entry_condition['price_below']}"
                elif 'price_above' in entry_condition:
                    entry_desc = f"above ${entry_condition['price_above']}"
                
                exit_desc = ''
                if 'take_profit' in exit_condition:
                    exit_desc = f" with take profit at ${exit_condition['take_profit']}"
                if 'stop_loss' in exit_condition:
                    exit_desc += f"{' and' if exit_desc else ''} stop loss at ${exit_condition['stop_loss']}"
                
                message = f"Leverage trade condition set: {side.capitalize()} {leverage}x {market}{' with entry condition ' + entry_desc if entry_desc else ''}{exit_desc}"
                
                return {
                    'success': True,
                    'message': message,
                    'trade_condition': result.get('trade_condition')
                }
            else:
                self.logger.warning(f"Failed to add leverage trade condition: {result.get('message')}")
                return {
                    'success': False,
                    'message': result.get('message', 'Unknown error occurred while setting up the leverage trade')
                }
                
        except Exception as e:
            self.logger.error(f"Error handling leverage trade request: {str(e)}")
            return {
                'success': False,
                'message': f'Error processing leverage trade: {str(e)}'
            }
    
    async def _update_context_with_response(self, context_id, user_id, response):
        """Update the conversation context with the response."""
        try:
            # Add the assistant's response to the conversation history
            self.logger.debug(f"Updating context {context_id} with response")
            
            # Get the context using our safe_call helper
            if not hasattr(self.conversation_manager, 'get_context'):
                self.logger.warning("Conversation manager does not have get_context method")
                return
                
            context = await self._safe_call(
                self.conversation_manager.get_context,
                context_id=context_id,
                user_id=user_id
            )
            
            if not context:
                self.logger.warning(f"Context {context_id} not found for user {user_id}")
                return
                
            # Check if the add_message method exists
            if not hasattr(context, 'add_message'):
                self.logger.warning(f"Context {context_id} does not have add_message method")
                return
                
            # Add the message using direct call (it's likely synchronous)
            try:
                # Check if add_message is async
                if asyncio.iscoroutinefunction(context.add_message):
                    await context.add_message("assistant", response)
                else:
                    context.add_message("assistant", response)
                self.logger.debug(f"Added assistant message to context {context_id}")
            except Exception as e:
                self.logger.error(f"Error adding message to context: {str(e)}")
                self.logger.error(traceback.format_exc())
                return
                
            # Save the context using our safe_call helper
            if not hasattr(self.conversation_manager, 'save_context'):
                self.logger.warning("Conversation manager does not have save_context method")
                return
                
            await self._safe_call(
                self.conversation_manager.save_context,
                context=context
            )
            self.logger.debug(f"Saved context {context_id}")
            
        except Exception as e:
            self.logger.error(f"Error updating context with response: {str(e)}")
            self.logger.error(traceback.format_exc())
