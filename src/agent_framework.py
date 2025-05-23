"""
Agent Framework for Grace - A crypto trading application based on Open Interpreter

This module implements the agent framework that powers Grace's multi-agent architecture.
It includes the BaseAgent foundation, SmartRouter for task routing, and specialized agents
for different tasks.
"""

import time
import queue
import json
import time
import logging
import asyncio
import uuid
import threading
from enum import Enum
import datetime
from typing import Dict, Any, Optional
from datetime import datetime

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("GraceAgentFramework")


class AgentType(Enum):
    """Enum for different types of agents."""

    BASE = "base"
    DATA_WHIZ = "data_whiz"
    TRADING = "trading"
    LEVERAGE_TRADING = "leverage_trading"
    COMMUNITY_TRACKER = "community_tracker"
    MEMORY_KEEPER = "memory_keeper"
    COORDINATOR = "coordinator"


class AgentPriority(Enum):
    """Enum for agent task priorities."""

    LOW = 0
    MEDIUM = 1
    HIGH = 2
    CRITICAL = 3


class AgentTask:
    """Represents a task to be processed by an agent."""

    def __init__(
        self,
        task_id: str,
        task_type: str,
        content: Dict[str, Any],
        priority: AgentPriority = AgentPriority.MEDIUM,
        source_agent: Optional[str] = None,
        target_agent: Optional[str] = None,
    ):
        """
        Initialize a new agent task.

        Args:
            task_id: Unique identifier for the task
            task_type: Type of task
            content: Task content and parameters
            priority: Task priority
            source_agent: Agent that created the task
            target_agent: Agent that should process the task
        """
        self.task_id = task_id
        self.task_type = task_type
        self.content = content
        self.priority = priority
        self.source_agent = source_agent
        self.target_agent = target_agent
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        self.status = "pending"
        self.result = None
        self.error = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary."""
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "content": self.content,
            "priority": self.priority.name,
            "source_agent": self.source_agent,
            "target_agent": self.target_agent,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
            "status": self.status,
            "result": self.result,
            "error": self.error,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentTask":
        """Create task from dictionary."""
        task = cls(
            task_id=data["task_id"],
            task_type=data["task_type"],
            content=data["content"],
            priority=AgentPriority[data["priority"]],
            source_agent=data["source_agent"],
            target_agent=data["target_agent"],
        )
        task.created_at = datetime.fromisoformat(data["created_at"])
        if data["started_at"]:
            task.started_at = datetime.fromisoformat(data["started_at"])
        if data["completed_at"]:
            task.completed_at = datetime.fromisoformat(data["completed_at"])
        task.status = data["status"]
        task.result = data["result"]
        task.error = data["error"]
        return task


class BaseAgent:
    """Base class for all agents in the system."""

    def __init__(
        self,
        agent_id: str,
        agent_type: AgentType,
        task_queue: Optional[queue.PriorityQueue] = None,
        result_queue: Optional[queue.Queue] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize a new agent.

        Args:
            agent_id: Unique identifier for the agent
            agent_type: Type of agent
            task_queue: Queue for incoming tasks
            result_queue: Queue for task results
            config: Agent configuration
        """
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.task_queue = task_queue or queue.PriorityQueue()
        self.result_queue = result_queue or queue.Queue()
        self.config = config or {}
        self.running = False
        self.thread = None
        self.logger = logging.getLogger(f"Grace{agent_type.value.capitalize()}Agent")

        # Initialize supported task types
        self.supported_task_types = ["ping", "status"]

    def start(self):
        """Start the agent processing loop."""
        if self.running:
            self.logger.warning(f"Agent {self.agent_id} is already running")
            return

        self.running = True
        self.thread = threading.Thread(target=self._process_loop)
        self.thread.daemon = True
        self.thread.start()
        self.logger.info(f"Agent {self.agent_id} started")

    def stop(self):
        """Stop the agent processing loop."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5.0)
            self.thread = None
        self.logger.info(f"Agent {self.agent_id} stopped")

    def add_task(self, task: AgentTask):
        """
        Add a task to the agent's queue.

        Args:
            task: Task to add
        """
        # Add task to queue with priority
        self.task_queue.put((task.priority.value, task))
        self.logger.debug(f"Added task {task.task_id} to queue")

    def _process_loop(self):
        """Main processing loop for the agent."""
        while self.running:
            try:
                # Get task from queue with timeout
                try:
                    _, task = self.task_queue.get(timeout=1.0)
                except queue.Empty:
                    continue

                # Process task
                self.logger.info(
                    f"Processing task {task.task_id} of type {task.task_type}"
                )
                task.status = "processing"
                task.started_at = datetime.now()

                try:
                    # Check if task type is supported
                    if task.task_type not in self.supported_task_types:
                        raise ValueError(f"Unsupported task type: {task.task_type}")

                    # Process task based on type
                    if task.task_type == "ping":
                        result = self._handle_ping(task)
                    elif task.task_type == "status":
                        result = self._handle_status(task)
                    else:
                        # This should never happen due to the check above
                        result = self._process_task(task)

                    # Update task with result
                    task.status = "completed"
                    task.completed_at = datetime.now()
                    task.result = result

                    # Add to result queue as a dictionary
                    self.result_queue.put(
                        {
                            "task_id": task.task_id,
                            "data": task.result,
                            "status": task.status,
                        }
                    )
                    self.logger.info(f"Completed task {task.task_id}")
                except Exception as e:
                    # Handle task error
                    self.logger.error(f"Error processing task {task.task_id}: {str(e)}")
                    task.status = "failed"
                    task.completed_at = datetime.now()
                    task.error = str(e)

                    # Add to result queue as a dictionary
                    self.result_queue.put(
                        {
                            "task_id": task.task_id,
                            "data": {"error": task.error},
                            "status": task.status,
                        }
                    )

                # Mark task as done in queue
                self.task_queue.task_done()
            except Exception as e:
                self.logger.error("Error in processing loop: {str(e)}")

    def _process_task(self, task: AgentTask) -> Dict[str, Any]:
        """
        Process a task. Override in subclasses.

        Args:
            task: Task to process

        Returns:
            Dict: Task result
        """
        raise NotImplementedError("Subclasses must implement _process_task")

    def _handle_ping(self, task: AgentTask) -> Dict[str, Any]:
        """
        Handle a ping task.

        Args:
            task: Ping task

        Returns:
            Dict: Ping result
        """
        return {
            "status": "ok",
            "agent_id": self.agent_id,
            "agent_type": self.agent_type.value,
            "timestamp": datetime.now().isoformat(),
        }

    def _handle_status(self, task: AgentTask) -> Dict[str, Any]:
        """
        Handle a status task.

        Args:
            task: Status task

        Returns:
            Dict: Status result
        """
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type.value,
            "running": self.running,
            "queue_size": self.task_queue.qsize(),
            "supported_task_types": self.supported_task_types,
            "timestamp": datetime.now().isoformat(),
        }


class DataWhizAgent(BaseAgent):
    """Agent for data processing and analysis."""

    def __init__(
        self,
        agent_id: str,
        api_services_manager=None,
        memory_system=None,
        task_queue: Optional[queue.PriorityQueue] = None,
        result_queue: Optional[queue.Queue] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize a new DataWhizAgent.

        Args:
            agent_id: Unique identifier for the agent
            api_services_manager: API services manager
            memory_system: Memory system
            task_queue: Queue for incoming tasks
            result_queue: Queue for task results
            config: Agent configuration
        """
        super().__init__(
            agent_id=agent_id,
            agent_type=AgentType.DATA_WHIZ,
            task_queue=task_queue,
            result_queue=result_queue,
            config=config,
        )

        self.api_services_manager = api_services_manager
        self.memory_system = memory_system

        # Set supported task types
        self.supported_task_types = set(
            [
                "process_message",  # Add support for processing messages
                "search_twitter",
                "get_community_pulse",
                "get_token_price",
                "get_token_insights",
                "analyze_sentiment",
                "search_and_associate",
            ]
        )

    def _process_task(self, task: AgentTask) -> Dict[str, Any]:
        """
        Process a task.

        Args:
            task: Task to process

        Returns:
            Dict: Task result
        """
        # Process task based on type
        if task.task_type == "process_message":
            return self._handle_process_message(task)
        elif task.task_type == "search_twitter":
            return self._handle_search_twitter(task)
        elif task.task_type == "get_community_pulse":
            return self._handle_get_community_pulse(task)
        elif task.task_type == "get_token_price":
            return self._handle_get_token_price(task)
        elif task.task_type == "get_token_insights":
            return self._handle_get_token_insights(task)
        elif task.task_type == "analyze_sentiment":
            return self._handle_analyze_sentiment(task)
        elif task.task_type == "search_and_associate":
            return self._handle_search_and_associate(task)
        else:
            raise ValueError(f"Unsupported task type: {task.task_type}")

    def _handle_process_message(self, task: AgentTask) -> Dict[str, Any]:
        """
        Handle a process_message task.

        Args:
            task: Task to process

        Returns:
            Dict: Task result with response
        """
        try:
            # Extract message and context from task content
            content = task.content
            message = content.get("message", "")
            user_id = content.get("user_id", "")
            session_id = content.get("session_id", "")
            context = content.get("context", {})

            # Get memories and system message from context
            memories = context.get("memories", [])
            system_message = context.get(
                "system_message", "You are Grace, a helpful AI assistant."
            )

            # Get conversation context if available
            conversation_context = context.get("conversation_context", {})
            conversation_history = conversation_context.get("conversation_history", [])
            context_info = conversation_context.get("context_info", {})
            prompt_enhancement = conversation_context.get("prompt_enhancement", "")

            self.logger.info(
                f"Processing message for user {user_id}: {message[:50]}..."
            )

            # Build a more informed response based on available context
            response = ""

            # Check if we have completed background tasks with information
            if context_info and "completed_tasks" in context_info:
                for task in context_info["completed_tasks"]:
                    if task["type"] == "price_check" and "result" in task:
                        result = task["result"]
                        response += f"The current price of {result['symbol']} is ${result['price']:.2f} USD. "
                    elif task["type"] == "data_search" and "result" in task:
                        result = task["result"]
                        response += (
                            f"I found some information about '{result['query']}': "
                        )
                        for item in result["results"][:2]:  # Limit to 2 results
                            response += f"{item['title']} - {item['snippet']} "

            # If we have active topics, acknowledge them
            if (
                context_info
                and "active_topics" in context_info
                and context_info["active_topics"]
            ):
                topics = [topic["name"] for topic in context_info["active_topics"][:2]]
                if (
                    topics and not response
                ):  # Only add if we don't already have a response
                    response += f"Regarding {', '.join(topics)}, "

            # If we don't have any context-specific response yet, generate a more intelligent response
            if not response:
                # Check for specific crypto tokens or coins in the message
                common_tokens = [
                    "bitcoin",
                    "btc",
                    "ethereum",
                    "eth",
                    "solana",
                    "sol",
                    "dogecoin",
                    "doge",
                    "cardano",
                    "ada",
                    "ripple",
                    "xrp",
                    "bnb",
                    "usdt",
                    "tether",
                    "usdc",
                    "wif",
                ]

                # Check if message contains any token names
                found_tokens = [
                    token for token in common_tokens if token in message.lower()
                ]

                # Process specific types of queries with better responses
                if "hello" in message.lower() or "hi" in message.lower():
                    response = "Hello! I'm Grace, your crypto assistant. How can I help you today with cryptocurrency information or trading?"

                elif "help" in message.lower():
                    response = "I'm here to help with crypto trading, price information, market analysis, and wallet management. What specific aspect of crypto would you like assistance with?"

                elif (
                    "trade" in message.lower() or "trading" in message.lower()
                ) and found_tokens:
                    token = found_tokens[0].upper()
                    response = f"I see you're interested in trading {token}. I can help you check its current price, analyze market conditions, or execute a trade. What would you like to do with {token}?"

                elif "trade" in message.lower() or "trading" in message.lower():
                    response = "I can assist with trading cryptocurrencies. Would you like to check current prices, execute a specific trade, or learn about trading strategies? I can also help connect to your wallet if needed."

                elif (
                    "price" in message.lower()
                    or "prices" in message.lower()
                    or "worth" in message.lower()
                ) and found_tokens:
                    # Create a price check task for this token
                    token = found_tokens[0].upper()
                    try:
                        # Try to create a price check task
                        if self.api_services_manager:
                            price_info = self.api_services_manager.get_token_price(
                                token
                            )
                            if price_info and "price" in price_info:
                                response = f"The current price of {token} is ${price_info['price']:.2f} USD. "
                                if "change_24h" in price_info:
                                    change = price_info["change_24h"]
                                    if change > 0:
                                        response += f"It's up {change:.2f}% in the last 24 hours."
                                    else:
                                        response += f"It's down {abs(change):.2f}% in the last 24 hours."
                            else:
                                response = f"I'm checking the latest price for {token}. This information should be available through the trading interface. Would you like me to help you navigate to the price charts?"
                        else:
                            response = f"I'd be happy to check the current price of {token} for you. This information should be available through our trading interface. Would you like me to help you access that?"
                    except Exception as e:
                        self.logger.error(f"Error getting price for {token}: {str(e)}")
                        response = f"I'd be happy to provide the current price of {token}. Would you like me to check that for you?"

                elif "price" in message.lower() or "prices" in message.lower():
                    response = "I can check cryptocurrency prices for you. Which specific token or coin are you interested in? For example, Bitcoin (BTC), Ethereum (ETH), or Solana (SOL)?"

                elif "wallet" in message.lower() or "balance" in message.lower():
                    response = "I can help you check your wallet balance or connect to your wallet. Would you like me to show your current balance or help with wallet connection?"

                elif "memory" in message.lower() or "remember" in message.lower():
                    response = "I can help you store and retrieve important information. What specific details would you like me to remember for you?"

                elif found_tokens:
                    token = found_tokens[0].upper()
                    response = f"I see you're interested in {token}. I can provide price information, trading options, or market analysis for {token}. What specific information would you like?"

                else:
                    # Use the prompt enhancement if available
                    if prompt_enhancement:
                        response = f"Based on our conversation, I understand you're asking about {message}. "
                        response += "I can provide information on cryptocurrency prices, trading options, wallet management, or market analysis. How can I assist you specifically?"
                    else:
                        response = "I understand you're interested in cryptocurrency. I can help with price information, trading, wallet management, or market analysis. What specific aspect would you like to explore?"

                # Add a closing statement if the response doesn't already have one
                if not response.endswith("?") and not "What would you like" in response:
                    response += " How else can I assist you with crypto trading today?"

            # Return a response format compatible with the rest of the system
            # This will be placed in the 'data' field by BaseAgent._process_loop
            return {"response": response}
        except Exception as e:
            self.logger.error(f"Error processing message: {str(e)}")
            # Return a response format compatible with the rest of the system
            return {
                "response": "I'm sorry, I couldn't process your message.",
                "error": str(e),
            }

    def _handle_search_twitter(self, task: AgentTask) -> Dict[str, Any]:
        """
        Handle a search_twitter task.

        Args:
            task: Task to process

        Returns:
            Dict: Task result
        """
        if not self.api_services_manager:
            raise ValueError("API services manager not available")

        query = task.content.get("query")
        count = task.content.get("count", 20)
        search_type = task.content.get("search_type", "Top")

        if not query:
            raise ValueError("Query is required")

        # Search Twitter
        result = self.api_services_manager.twitter_service.search_twitter(
            query=query, count=count, search_type=search_type
        )

        return {
            "query": query,
            "count": count,
            "search_type": search_type,
            "result": result,
        }

    def _handle_get_community_pulse(self, task: AgentTask) -> Dict[str, Any]:
        """
        Handle a get_community_pulse task.

        Args:
            task: Task to process

        Returns:
            Dict: Task result
        """
        if not self.api_services_manager:
            raise ValueError("API services manager not available")

        community = task.content.get("community")

        if not community:
            raise ValueError("Community is required")

        # Get community pulse
        result = self.api_services_manager.twitter_service.get_community_pulse(
            community
        )

        return {"community": community, "result": result}

    def _handle_get_token_price(self, task: AgentTask) -> Dict[str, Any]:
        """
        Handle a get_token_price task.

        Args:
            task: Task to process

        Returns:
            Dict: Task result
        """
        if not self.api_services_manager:
            raise ValueError("API services manager not available")

        token = task.content.get("token")

        if not token:
            raise ValueError("Token is required")

        # Get token price
        result = self.api_services_manager.trading_service.get_token_price(token)

        return {"token": token, "result": result}

    def _handle_get_token_insights(self, task: AgentTask) -> Dict[str, Any]:
        """
        Handle a get_token_insights task.

        Args:
            task: Task to process

        Returns:
            Dict: Task result
        """
        if not self.api_services_manager:
            raise ValueError("API services manager not available")

        token = task.content.get("token")

        if not token:
            raise ValueError("Token is required")

        # Get token insights
        result = self.api_services_manager.financial_service.get_token_insights(token)

        return {"token": token, "result": result}

    def _handle_analyze_sentiment(self, task: AgentTask) -> Dict[str, Any]:
        """
        Handle an analyze_sentiment task.

        Args:
            task: Task to process

        Returns:
            Dict: Task result
        """
        text = task.content.get("text")

        if not text:
            raise ValueError("Text is required")

        # In a real implementation, this would use NLP for sentiment analysis
        # For now, use a simple approach
        positive_words = [
            "great",
            "good",
            "amazing",
            "excellent",
            "bullish",
            "up",
            "gain",
        ]
        negative_words = ["bad", "terrible", "bearish", "down", "loss", "crash", "fail"]

        positive_count = 0
        negative_count = 0

        text_lower = text.lower()

        for word in positive_words:
            if word in text_lower:
                positive_count += 1

        for word in negative_words:
            if word in text_lower:
                negative_count += 1

        if positive_count > negative_count * 1.5:
            sentiment = "positive"
        elif negative_count > positive_count * 1.5:
            sentiment = "negative"
        else:
            sentiment = "neutral"

        return {
            "text": text,
            "sentiment": sentiment,
            "positive_count": positive_count,
            "negative_count": negative_count,
        }

    def _handle_search_and_associate(self, task: AgentTask) -> Dict[str, Any]:
        """
        Handle a search_and_associate task.

        Args:
            task: Task to process

        Returns:
            Dict: Task result
        """
        if not self.api_services_manager:
            raise ValueError("API services manager not available")

        query = task.content.get("query")
        entity = task.content.get("entity")
        search_twitter = task.content.get("search_twitter", True)
        search_financial = task.content.get("search_financial", True)

        if not query or not entity:
            raise ValueError("Query and entity are required")

        # Search and associate
        result = self.api_services_manager.search_and_associate(
            query=query,
            entity=entity,
            search_twitter=search_twitter,
            search_financial=search_financial,
        )

        return {"query": query, "entity": entity, "result": result}


class TradingAgent(BaseAgent):
    """Agent for trading operations."""

    def __init__(
        self,
        agent_id: str,
        api_services_manager=None,
        memory_system=None,
        task_queue: Optional[queue.PriorityQueue] = None,
        result_queue: Optional[queue.Queue] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize a new TradingAgent.

        Args:
            agent_id: Unique identifier for the agent
            api_services_manager: API services manager
            memory_system: Memory system
            task_queue: Queue for incoming tasks
            result_queue: Queue for task results
            config: Agent configuration
        """
        super().__init__(
            agent_id=agent_id,
            agent_type=AgentType.TRADING,
            task_queue=task_queue,
            result_queue=result_queue,
            config=config,
        )

        self.api_services_manager = api_services_manager
        self.memory_system = memory_system

        # Add supported task types
        self.supported_task_types.extend(
            [
                "execute_trade",
                "get_user_trades",
                "create_liquidity_pool",
                "get_user_liquidity_pools",
                "remove_liquidity",
                "setup_auto_trading",
                "price_check",
                "get_token_price",
                "check_wallet_balance",
                "trade_initiate",
            ]
        )

    def _process_task(self, task: AgentTask) -> Dict[str, Any]:
        """
        Process a task.

        Args:
            task: Task to process

        Returns:
            Dict: Task result
        """
        try:
            if task.task_type == "execute_trade":
                return self._handle_execute_trade(task)
            elif task.task_type == "get_user_trades":
                return self._handle_get_user_trades(task)
            elif task.task_type == "create_liquidity_pool":
                return self._handle_create_liquidity_pool(task)
            elif task.task_type == "get_user_liquidity_pools":
                return self._handle_get_user_liquidity_pools(task)
            elif task.task_type == "remove_liquidity":
                return self._handle_remove_liquidity(task)
            elif task.task_type == "setup_auto_trading":
                return self._handle_setup_auto_trading(task)
            elif task.task_type == "price_check" or task.task_type == "get_token_price":
                return self._handle_price_check(task)
            elif task.task_type == "check_wallet_balance":
                return self._handle_check_wallet_balance(task)
            elif task.task_type == "trade_initiate":
                return self._handle_trade_initiate(task)
            else:
                self.logger.warning(f"Unsupported task type: {task.task_type}")
                return {
                    "error": f"Unsupported task type: {task.task_type}",
                    "status": "error",
                }
        except Exception as e:
            self.logger.error(
                f"Error processing task {task.task_id} of type {task.task_type}: {str(e)}"
            )
            import traceback

            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return {"error": str(e), "status": "error"}

    def _handle_execute_trade(self, task: AgentTask) -> Dict[str, Any]:
        """
        Handle an execute_trade task.

        Args:
            task: Task to process

        Returns:
            Dict: Task result
        """
        if not self.api_services_manager or not hasattr(
            self.api_services_manager, "mango_spot_market"
        ):
            raise ValueError("Mango spot market not available")

        # Extract trade parameters
        user_id = task.content.get("user_id")
        market = task.content.get("market")  # e.g. "BTC/USDC"
        side = task.content.get("side")  # "buy" or "sell"
        order_type = task.content.get("type", "market")  # "limit" or "market"
        size = task.content.get("size")
        price = task.content.get("price")  # Optional for market orders
        client_id = task.content.get("client_id")  # Optional

        # Validate required fields
        if not all([user_id, market, side, size]):
            raise ValueError("user_id, market, side, and size are required")
        if order_type == "limit" and not price:
            raise ValueError("price is required for limit orders")

        # Prepare trade request
        trade_request = {
            "market": market,
            "side": side,
            "type": order_type,
            "size": float(size),
        }
        if price:
            trade_request["price"] = float(price)
        if client_id:
            trade_request["client_id"] = client_id

        # Execute trade through MangoSpotMarket
        try:
            result = self.api_services_manager.mango_spot_market.process_trade_request(
                entities=trade_request, client_id=user_id
            )

            # Store trade in memory system
            if (
                hasattr(self.api_services_manager, "memory_system")
                and self.api_services_manager.memory_system
            ):
                trade_memory = {
                    "type": "trade_execution",
                    "source": "mango_v3",
                    "user_id": user_id,
                    "trade_details": trade_request,
                    "result": result,
                    "timestamp": datetime.datetime.now().isoformat(),
                }
                self.api_services_manager.memory_system.add_to_short_term(
                    user_id=user_id,
                    text=f"Executed {trade_request['side']} trade of {trade_request['size']} {trade_request['market']} via Mango V3",
                    metadata=trade_memory,
                )

            return {
                "status": "success",
                "user_id": user_id,
                "trade_details": trade_request,
                "result": result,
            }

        except Exception as e:
            self.logger.error(f"Trade execution failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "user_id": user_id,
                "trade_details": trade_request,
            }

    def _handle_get_user_trades(self, task: AgentTask) -> Dict[str, Any]:
        """
        Handle a get_user_trades task.

        Args:
            task: Task to process

        Returns:
            Dict: Task result
        """
        if not self.api_services_manager:
            raise ValueError("API services manager not available")

        user_id = task.content.get("user_id")

        if not user_id:
            raise ValueError("user_id is required")

        # Get user trades
        result = self.api_services_manager.trading_service.get_user_trades(user_id)

        return {"user_id": user_id, "trades": result}

    def _handle_create_liquidity_pool(self, task: AgentTask) -> Dict[str, Any]:
        """
        Handle a create_liquidity_pool task.

        Args:
            task: Task to process

        Returns:
            Dict: Task result
        """
        if not self.api_services_manager:
            raise ValueError("API services manager not available")

        user_id = task.content.get("user_id")
        token_a = task.content.get("token_a")
        token_b = task.content.get("token_b")
        amount_a = task.content.get("amount_a")
        amount_b = task.content.get("amount_b")
        wallet_address = task.content.get("wallet_address")

        # This is a placeholder implementation
        return {
            "status": "simulated",
            "user_id": user_id,
            "token_a": token_a,
            "token_b": token_b,
            "amount_a": amount_a,
            "amount_b": amount_b,
            "wallet_address": wallet_address,
            "pool_id": "simulated_pool_" + str(uuid.uuid4())[:8],
        }

    def _handle_price_check(self, task: AgentTask) -> Dict[str, Any]:
        """
        Handle a price_check or get_token_price task.

        Args:
            task: Task to process

        Returns:
            Dict: Task result with token price information
        """
        self.logger.info(f"Handling price check task: {task.task_id}")

        # Extract token symbol from task content
        content = task.content
        token_symbol = content.get("token_symbol") or content.get("symbol")
        user_id = content.get("user_id")

        if not token_symbol:
            self.logger.error("Token symbol not provided for price check")
            return {"status": "error", "error": "Token symbol not provided"}

        try:
            # Try Mango V3 first
            if hasattr(self.api_services_manager, "mango_spot_market"):
                try:
                    market_data = (
                        self.api_services_manager.mango_spot_market.get_market_data(
                            token_symbol
                        )
                    )
                    if market_data and "price" in market_data:
                        return {
                            "status": "success",
                            "source": "mango_v3",
                            "price": market_data["price"],
                            "market_data": market_data,
                        }
                except Exception as e:
                    self.logger.warning(
                        f"Mango V3 price check failed: {str(e)}, falling back to GMGN"
                    )

            # Fallback to GMGN
            try:
                price = self._get_token_price(token_symbol)
                return {
                    "status": "success",
                    "source": "gmgn",
                    "token_symbol": token_symbol,
                    "price": price,
                }
            except Exception as e:
                self.logger.error(
                    f"Both Mango V3 and GMGN price checks failed for {token_symbol}: {str(e)}"
                )
                return {"status": "error", "error": str(e)}

        except Exception as e:
            self.logger.error(f"Error in price check handler: {str(e)}")
            import traceback

            self.logger.error(f"Traceback: {traceback.format_exc()}")

            return {
                "status": "error",
                "symbol": token_symbol,
                "error": str(e),
                "user_id": user_id,
            }

    def _handle_check_wallet_balance(self, task: AgentTask) -> Dict[str, Any]:
        """
        Handle a check_wallet_balance task.

        Args:
            task: Task to process

        Returns:
            Dict: Task result with wallet balance information
        """
        if not self.api_services_manager:
            raise ValueError("API services manager not available")

        user_id = task.content.get("user_id")
        wallet_address = task.content.get("wallet_address")

        if not user_id:
            raise ValueError("user_id is required")

        try:
            # Try Mango V3 first
            if hasattr(self.api_services_manager, "mango_spot_market"):
                try:
                    balances = (
                        self.api_services_manager.mango_spot_market.get_wallet_balances(
                            user_id
                        )
                    )
                    return {
                        "status": "success",
                        "source": "mango_v3",
                        "user_id": user_id,
                        "wallet_address": wallet_address,
                        "balances": balances,
                    }
                except Exception as e:
                    self.logger.warning(
                        f"Mango V3 balance check failed: {str(e)}, falling back to GMGN"
                    )

            # Fallback to GMGN
            result = self.api_services_manager.get_wallet_balance(
                user_id=user_id, wallet_address=wallet_address
            )

            # Store GMGN balance check in memory system
            if (
                hasattr(self.api_services_manager, "memory_system")
                and self.api_services_manager.memory_system
            ):
                balance_memory = {
                    "type": "balance_check",
                    "source": "gmgn",
                    "user_id": user_id,
                    "wallet_address": wallet_address,
                    "result": result,
                    "timestamp": datetime.datetime.now().isoformat(),
                }
                self.api_services_manager.memory_system.add_to_short_term(
                    user_id=user_id,
                    text=f"Retrieved wallet balance via GMGN for wallet {wallet_address}",
                    metadata=balance_memory,
                )

            return {
                "status": "success",
                "source": "gmgn",
                "user_id": user_id,
                "wallet_address": wallet_address,
                "balances": result,
            }

        except Exception as e:
            self.logger.error(f"Both Mango V3 and GMGN balance checks failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "user_id": user_id,
                "wallet_address": wallet_address,
            }

    def _handle_setup_auto_trading(self, task: AgentTask) -> Dict[str, Any]:
        """
        Handle a setup_auto_trading task.

        Args:
            task: Task to process

        Returns:
            Dict: Task result
        """
        if not self.api_services_manager:
            raise ValueError("API services manager not available")

        user_id = task.content.get("user_id")
        risk_level = task.content.get("risk_level")
        max_trade_size = task.content.get("max_trade_size")
        stop_loss = task.content.get("stop_loss")
        take_profit = task.content.get("take_profit")
        wallet_address = task.content.get("wallet_address")

        if (
            not user_id
            or risk_level is None
            or max_trade_size is None
            or stop_loss is None
            or take_profit is None
        ):
            raise ValueError(
                "user_id, risk_level, max_trade_size, stop_loss, and take_profit are required"
            )

        # Setup auto-trading
        result = self.api_services_manager.setup_auto_trading(
            user_id=user_id,
            risk_level=risk_level,
            max_trade_size=max_trade_size,
            stop_loss=stop_loss,
            take_profit=take_profit,
            wallet_address=wallet_address,
        )

        return {
            "user_id": user_id,
            "risk_level": risk_level,
            "max_trade_size": max_trade_size,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "wallet_address": wallet_address,
            "result": result,
        }


class CommunityTrackerAgent(BaseAgent):
    """Agent for tracking community trends and social signals."""

    def __init__(
        self,
        agent_id: str,
        api_services_manager=None,
        memory_system=None,
        task_queue: Optional[queue.PriorityQueue] = None,
        result_queue: Optional[queue.Queue] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize a new CommunityTrackerAgent.

        Args:
            agent_id: Unique identifier for the agent
            api_services_manager: API services manager
            memory_system: Memory system
            task_queue: Queue for incoming tasks
            result_queue: Queue for task results
            config: Agent configuration
        """
        super().__init__(
            agent_id=agent_id,
            agent_type=AgentType.COMMUNITY_TRACKER,
            task_queue=task_queue,
            result_queue=result_queue,
            config=config,
        )

        self.api_services_manager = api_services_manager
        self.memory_system = memory_system

        # Add supported task types
        self.supported_task_types.extend(
            [
                "get_community_insights",
                "discover_community_changes",
                "update_community_seeds",
                "track_entity_mentions",
            ]
        )

    def _process_task(self, task: AgentTask) -> Dict[str, Any]:
        """
        Process a task.

        Args:
            task: Task to process

        Returns:
            Dict: Task result
        """
        if task.task_type == "get_community_insights":
            return self._handle_get_community_insights(task)
        elif task.task_type == "discover_community_changes":
            return self._handle_discover_community_changes(task)
        elif task.task_type == "update_community_seeds":
            return self._handle_update_community_seeds(task)
        elif task.task_type == "track_entity_mentions":
            return self._handle_track_entity_mentions(task)
        else:
            raise ValueError(f"Unsupported task type: {task.task_type}")

    def _handle_get_community_insights(self, task: AgentTask) -> Dict[str, Any]:
        """
        Handle a get_community_insights task.

        Args:
            task: Task to process

        Returns:
            Dict: Task result
        """
        if not self.api_services_manager:
            raise ValueError("API services manager not available")

        community = task.content.get("community")

        if not community:
            raise ValueError("Community is required")

        # Get community insights
        result = self.api_services_manager.get_community_insights(community)

        return {"community": community, "result": result}

    def _handle_discover_community_changes(self, task: AgentTask) -> Dict[str, Any]:
        """
        Handle a discover_community_changes task.

        Args:
            task: Task to process

        Returns:
            Dict: Task result
        """
        if not self.api_services_manager:
            raise ValueError("API services manager not available")

        community = task.content.get("community")

        if not community:
            raise ValueError("Community is required")

        # Discover community changes
        result = self.api_services_manager.twitter_service.discover_community_changes(
            community
        )

        return {"community": community, "result": result}

    def _handle_update_community_seeds(self, task: AgentTask) -> Dict[str, Any]:
        """
        Handle an update_community_seeds task.

        Args:
            task: Task to process

        Returns:
            Dict: Task result
        """
        if not self.api_services_manager:
            raise ValueError("API services manager not available")

        community = task.content.get("community")
        add_handles = task.content.get("add_handles", [])
        remove_handles = task.content.get("remove_handles", [])

        if not community:
            raise ValueError("Community is required")

        # Update community seeds
        result = self.api_services_manager.twitter_service.update_community_seeds(
            community=community, add_handles=add_handles, remove_handles=remove_handles
        )

        return {
            "community": community,
            "add_handles": add_handles,
            "remove_handles": remove_handles,
            "result": result,
        }

    def _handle_track_entity_mentions(self, task: AgentTask) -> Dict[str, Any]:
        """
        Handle a track_entity_mentions task.

        Args:
            task: Task to process

        Returns:
            Dict: Task result
        """
        if not self.api_services_manager:
            raise ValueError("API services manager not available")

        entity = task.content.get("entity")

        if not entity:
            raise ValueError("Entity is required")

        # Track entity mentions
        # In a real implementation, this would set up continuous tracking
        # For now, just do a one-time search
        result = self.api_services_manager.twitter_service.search_twitter(entity)

        # Associate with entity in memory if available
        if self.memory_system:
            try:
                self.api_services_manager.twitter_service.associate_with_entity(
                    query=entity, entity=entity, memory_system=self.memory_system
                )
            except Exception as e:
                self.logger.error("Error associating with entity: {str(e)}")

        return {
            "entity": entity,
            "mentions_count": len(result.get("tweets", [])),
            "result": result,
        }


class MemoryKeeperAgent(BaseAgent):
    """Agent for managing context and memory."""

    def __init__(
        self,
        agent_id: str,
        memory_system=None,
        task_queue: Optional[queue.PriorityQueue] = None,
        result_queue: Optional[queue.Queue] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize a new MemoryKeeperAgent.

        Args:
            agent_id: Unique identifier for the agent
            memory_system: Memory system
            task_queue: Queue for incoming tasks
            result_queue: Queue for task results
            config: Agent configuration
        """
        super().__init__(
            agent_id=agent_id,
            agent_type=AgentType.MEMORY_KEEPER,
            task_queue=task_queue,
            result_queue=result_queue,
            config=config,
        )

        self.memory_system = memory_system

        # Add supported task types
        self.supported_task_types.extend(
            [
                "add_memory",
                "query_memory",
                "prune_memory",
                "merge_memories",
                "get_entity_memories",
            ]
        )

    def _process_task(self, task: AgentTask) -> Dict[str, Any]:
        """
        Process a task.

        Args:
            task: Task to process

        Returns:
            Dict: Task result
        """
        if task.task_type == "add_memory":
            return self._handle_add_memory(task)
        elif task.task_type == "query_memory":
            return self._handle_query_memory(task)
        elif task.task_type == "prune_memory":
            return self._handle_prune_memory(task)
        elif task.task_type == "merge_memories":
            return self._handle_merge_memories(task)
        elif task.task_type == "get_entity_memories":
            return self._handle_get_entity_memories(task)
        else:
            raise ValueError(f"Unsupported task type: {task.task_type}")

    def _handle_add_memory(self, task: AgentTask) -> Dict[str, Any]:
        """
        Handle an add_memory task.

        Args:
            task: Task to process

        Returns:
            Dict: Task result
        """
        if not self.memory_system:
            raise ValueError("Memory system not available")

        content = task.content.get("content")
        source = task.content.get("source")
        entity = task.content.get("entity")
        priority = task.content.get("priority", 0.5)

        if not content:
            raise ValueError("Content is required")

        # Add memory
        memory_id = self.memory_system.add_memory(
            content=content, source=source, entity=entity, priority=priority
        )

        return {
            "memory_id": memory_id,
            "content": content,
            "source": source,
            "entity": entity,
            "priority": priority,
        }

    def _handle_query_memory(self, task: AgentTask) -> Dict[str, Any]:
        """
        Handle a query_memory task.

        Args:
            task: Task to process

        Returns:
            Dict: Task result
        """
        if not self.memory_system:
            raise ValueError("Memory system not available")

        query = task.content.get("query")
        limit = task.content.get("limit", 10)

        if not query:
            raise ValueError("Query is required")

        # Query memory
        results = self.memory_system.query_memory(query, n_results=limit)

        return {"query": query, "limit": limit, "results": results}

    def _handle_prune_memory(self, task: AgentTask) -> Dict[str, Any]:
        """
        Handle a prune_memory task.

        Args:
            task: Task to process

        Returns:
            Dict: Task result
        """
        if not self.memory_system:
            raise ValueError("Memory system not available")

        max_age_days = task.content.get("max_age_days", 30)
        min_priority = task.content.get("min_priority", 0.3)

        # Prune memory
        pruned_count = self.memory_system.prune_memories(
            max_age_days=max_age_days, min_priority=min_priority
        )

        return {
            "max_age_days": max_age_days,
            "min_priority": min_priority,
            "pruned_count": pruned_count,
        }

    def _handle_merge_memories(self, task: AgentTask) -> Dict[str, Any]:
        """
        Handle a merge_memories task.

        Args:
            task: Task to process

        Returns:
            Dict: Task result
        """
        if not self.memory_system:
            raise ValueError("Memory system not available")

        entity = task.content.get("entity")

        if not entity:
            raise ValueError("Entity is required")

        # Merge memories
        merged_count = self.memory_system.merge_memories(entity)

        return {"entity": entity, "merged_count": merged_count}

    def _handle_get_entity_memories(self, task: AgentTask) -> Dict[str, Any]:
        """
        Handle a get_entity_memories task.

        Args:
            task: Task to process

        Returns:
            Dict: Task result
        """
        if not self.memory_system:
            raise ValueError("Memory system not available")

        entity = task.content.get("entity")

        if not entity:
            raise ValueError("Entity is required")

        # Get entity memories
        memories = self.memory_system.get_entity_memories(entity)

        return {"entity": entity, "memories": memories}


class SmartRouter:
    """Routes tasks to appropriate agents based on task type and content."""

    def __init__(
        self, agents: Dict[str, BaseAgent], task_type_to_agent: Dict[str, Dict] = None
    ):
        """
        Initialize a new SmartRouter.

        Args:
            agents: Dictionary of agents by ID
            task_type_to_agent: Optional mapping from task types to agent services
        """
        self.agents = agents
        self.agent_types = {
            agent.agent_type: agent_id for agent_id, agent in agents.items()
        }
        self.logger = logging.getLogger("GraceSmartRouter")
        self.task_type_to_agent = task_type_to_agent or {}

        # Default task type to agent type mapping if no external mapping provided
        self.task_type_mapping = {
            # Core message processing
            "process_message": AgentType.DATA_WHIZ,  # Assign to DataWhiz as the primary message processor
            # DataWhizAgent tasks
            "search_twitter": AgentType.DATA_WHIZ,
            "get_community_pulse": AgentType.DATA_WHIZ,
            "get_token_price": AgentType.DATA_WHIZ,
            "get_token_insights": AgentType.DATA_WHIZ,
            "analyze_sentiment": AgentType.DATA_WHIZ,
            "search_and_associate": AgentType.DATA_WHIZ,
            # TradingAgent tasks
            "execute_trade": AgentType.TRADING,
            "get_user_trades": AgentType.TRADING,
            "create_liquidity_pool": AgentType.TRADING,
            "get_user_liquidity_pools": AgentType.TRADING,
            "remove_liquidity": AgentType.TRADING,
            "setup_auto_trading": AgentType.TRADING,
            # LeverageTradeAgent tasks
            "execute_leverage_trade": AgentType.LEVERAGE_TRADING,
            "get_leverage_positions": AgentType.LEVERAGE_TRADING,
            "update_leverage_trade": AgentType.LEVERAGE_TRADING,
            # CommunityTrackerAgent tasks
            "get_community_insights": AgentType.COMMUNITY_TRACKER,
            "discover_community_changes": AgentType.COMMUNITY_TRACKER,
            "update_community_seeds": AgentType.COMMUNITY_TRACKER,
            "track_entity_mentions": AgentType.COMMUNITY_TRACKER,
            # MemoryKeeperAgent tasks
            "add_memory": AgentType.MEMORY_KEEPER,
            "query_memory": AgentType.MEMORY_KEEPER,
            "prune_memory": AgentType.MEMORY_KEEPER,
            "merge_memories": AgentType.MEMORY_KEEPER,
            "get_entity_memories": AgentType.MEMORY_KEEPER,
        }

    def route_task(self, task: AgentTask) -> bool:
        """
        Route a task to the appropriate agent.

        Args:
            task: Task to route

        Returns:
            bool: True if task was routed successfully
        """
        # If target agent is specified, route to that agent
        if task.target_agent and task.target_agent in self.agents:
            self.agents[task.target_agent].add_task(task)
            self.logger.info(
                f"Routed task {task.task_id} to specified agent {task.target_agent}"
            )
            return True

        # First, check if we have a service registered for this task type
        if task.task_type in self.task_type_to_agent:
            # If we have a service, we need to find an agent that can handle it
            # For now, we'll use the DATA_WHIZ agent as a proxy for service-based tasks
            if AgentType.DATA_WHIZ in self.agent_types:
                agent_id = self.agent_types[AgentType.DATA_WHIZ]
                self.agents[agent_id].add_task(task)
                self.logger.info(
                    f"Routed task {task.task_id} of type {task.task_type} to agent {agent_id} (service proxy)"
                )
                return True

        # Otherwise, route based on task type using the traditional mapping
        if task.task_type in self.task_type_mapping:
            agent_type = self.task_type_mapping[task.task_type]

            if agent_type in self.agent_types:
                agent_id = self.agent_types[agent_type]
                self.agents[agent_id].add_task(task)
                self.logger.info(
                    f"Routed task {task.task_id} of type {task.task_type} to agent {agent_id}"
                )
                return True
            else:
                self.logger.error(
                    f"No agent of type {agent_type.value} available for task {task.task_id}"
                )
                return False
        else:
            # For unknown task types, try to find an agent that supports it
            for agent_id, agent in self.agents.items():
                if task.task_type in agent.supported_task_types:
                    agent.add_task(task)
                    self.logger.info(
                        f"Routed task {task.task_id} to agent {agent_id} based on supported task types"
                    )
                    return True

            self.logger.error(f"No agent found for task type {task.task_type}")
            return False


class SystemAgentManager:
    """Manages multiple agents and coordinates their activities."""

    def __init__(
        self,
        api_services_manager=None,
        memory_system=None,
        wallet_connection_system=None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize a new EnhancedAgentManager.

        Args:
            api_services_manager: API services manager
            memory_system: Memory system
            wallet_connection_system: Wallet connection system
            config: Manager configuration
        """
        self.api_services_manager = api_services_manager
        self.memory_system = memory_system
        self.wallet_connection_system = wallet_connection_system
        self.config = config or {}
        self.logger = logging.getLogger("GraceAgentManager")

        # Initialize result queue
        self.result_queue = queue.Queue()

        # Initialize agents
        self.agents = {}
        # Dictionary to map task types to agents
        self.task_type_to_agent = {}
        # Dictionary to store task status and results
        self.tasks = {}
        self._initialize_agents()

        # Task cleanup configuration
        self.max_tasks = self.config.get(
            "max_tasks", 1000
        )  # Maximum number of tasks to keep
        self.task_retention_hours = self.config.get(
            "task_retention_hours", 24
        )  # How long to keep completed tasks
        self.cleanup_interval = self.config.get(
            "cleanup_interval", 100
        )  # Run cleanup every N tasks
        self.last_cleanup_count = 0  # Counter for tracking when to run cleanup

        # Initialize task ID counter
        self.task_id_counter = 0

        # Initialize router with task type mapping
        self.router = SmartRouter(self.agents, self.task_type_to_agent)

        # Start result processing thread
        self.running = True
        self.result_thread = threading.Thread(target=self._process_results)
        self.result_thread.daemon = True
        self.result_thread.start()

        # Initialize scheduled tasks
        self.scheduled_tasks = {}
        self.scheduler_thread = None
        self.last_schedule_run = time.time()

    def _initialize_agents(self):
        """Initialize all agents."""
        # Create DataWhizAgent
        data_whiz = DataWhizAgent(
            agent_id="data_whiz_1",
            api_services_manager=self.api_services_manager,
            memory_system=self.memory_system,
            result_queue=self.result_queue,
        )
        self.agents[data_whiz.agent_id] = data_whiz

        # Create TradingAgent
        trading_agent = TradingAgent(
            agent_id="trading_1",
            api_services_manager=self.api_services_manager,
            memory_system=self.memory_system,
            result_queue=self.result_queue,
        )
        self.agents[trading_agent.agent_id] = trading_agent

        # Create CommunityTrackerAgent
        community_tracker = CommunityTrackerAgent(
            agent_id="community_tracker_1",
            api_services_manager=self.api_services_manager,
            memory_system=self.memory_system,
            result_queue=self.result_queue,
        )
        self.agents[community_tracker.agent_id] = community_tracker

        # Create MemoryKeeperAgent
        memory_keeper = MemoryKeeperAgent(
            agent_id="memory_keeper_1",
            memory_system=self.memory_system,
            result_queue=self.result_queue,
        )
        self.agents[memory_keeper.agent_id] = memory_keeper

    def start_all_agents(self):
        """Start all agents."""
        for agent_id, agent in self.agents.items():
            agent.start()
            self.logger.info(f"Started agent {agent_id}")

        # Start scheduler thread
        self._start_scheduler()

    def stop_all_agents(self):
        """Stop all agents."""
        for agent_id, agent in self.agents.items():
            agent.stop()
            self.logger.info(f"Stopped agent {agent_id}")

        # Stop result processing
        self.running = False
        if self.result_thread:
            self.result_thread.join(timeout=5.0)
            self.result_thread = None

        # Stop scheduler thread
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5.0)
            self.scheduler_thread = None

    def register_agent_for_task_type(
        self,
        task_type: str,
        target_service: Any,
        priority: AgentPriority = AgentPriority.MEDIUM,
    ):
        """
        Register an agent for a specific task type.

        This method maps a task type to a service that can process it.
        The service must have a process_task method that takes a task_data parameter.

        Args:
            task_type: Type of task this agent can handle
            target_service: Service that will process the task
            priority: Default priority for tasks of this type
        """
        if not hasattr(target_service, "process_task"):
            self.logger.warning(
                f"Service for task type {task_type} does not have a process_task method"
            )
            return

        self.task_type_to_agent[task_type] = {
            "service": target_service,
            "priority": priority,
        }
        self.logger.info(f"Registered agent for task type: {task_type}")

    def get_task_status(self, task_id: str):
        """
        Get the status of a task.

        Args:
            task_id: ID of the task to check

        Returns:
            A SimpleNamespace object with status, result, and error fields
        """
        from types import SimpleNamespace

        if task_id not in self.tasks:
            return SimpleNamespace(
                status="unknown", result=None, error="Task not found"
            )

        return SimpleNamespace(
            status=self.tasks[task_id].get("status", "pending"),
            result=self.tasks[task_id].get("result", None),
            error=self.tasks[task_id].get("error", None),
        )

    def create_task(
        self,
        task_type: str,
        content: Dict[str, Any],
        priority: AgentPriority = AgentPriority.MEDIUM,
        source_agent: Optional[str] = None,
        target_agent: Optional[str] = None,
    ) -> str:
        """
        Create and route a new task.

        Args:
            task_type: Type of task
            content: Task content and parameters
            priority: Task priority
            source_agent: Agent that created the task
            target_agent: Agent that should process the task

        Returns:
            Task ID
        """
        # Run task cleanup if needed
        self.cleanup_tasks()

        # Increment task ID counter
        self.task_id_counter += 1
        task_id = str(self.task_id_counter)

        # Create task
        task = AgentTask(
            task_id=task_id,
            task_type=task_type,
            content=content,
            priority=priority,
            source_agent=source_agent,
            target_agent=target_agent,
        )

        # Store task in tasks dictionary
        self.tasks[task_id] = {
            "status": "pending",
            "task": task,
            "created_at": datetime.now(),
        }

        # Check if we have a registered service for this task type
        if task_type in self.task_type_to_agent:
            service = self.task_type_to_agent[task_type]["service"]
            try:
                # Process the task with the registered service
                result = service.process_task(content)
                self.tasks[task_id]["status"] = "completed"
                self.tasks[task_id]["result"] = result
                self.logger.info(
                    f"Processed task {task_id} with registered service for {task_type}"
                )
                return task_id
            except Exception as e:
                self.tasks[task_id]["status"] = "error"
                self.tasks[task_id]["error"] = str(e)
                self.logger.error(
                    f"Error processing task {task_id} with registered service: {str(e)}"
                )

        # If no registered service or processing failed, use the router
        target_agent_id = self.router.route_task(task)
        if target_agent_id and target_agent_id in self.agents:
            self.agents[target_agent_id].add_task(task)
            self.logger.info(f"Routed task {task_id} to agent {target_agent_id}")
        else:
            self.tasks[task_id]["status"] = "error"
            self.tasks[task_id]["error"] = "Could not route task to any agent"
            self.logger.warning(f"Could not route task {task_id} to any agent")

        return task_id

    def _process_results(self):
        """Process task results from the result queue."""
        cleanup_counter = 0
        while self.running:
            try:
                # Get result from queue with timeout
                result = self.result_queue.get(timeout=1)

                # Update task status if task_id is provided
                task_id = result.get("task_id")
                if task_id and task_id in self.tasks:
                    self.tasks[task_id]["status"] = "completed"
                    self.tasks[task_id]["result"] = result.get("data", {})
                    self.tasks[task_id]["completed_at"] = datetime.now()

                # Process result
                if result.get("event") == "memory_added":
                    self._handle_memory_added(result)
                elif result.get("event") == "trade_executed":
                    self._handle_trade_executed(result)
                # Add more event handlers as needed

                # Mark task as done
                self.result_queue.task_done()

                # Periodically run cleanup in the result processing thread
                # This ensures we clean up even if no new tasks are being created
                cleanup_counter += 1
                if cleanup_counter >= 20:  # Run cleanup every 20 results
                    self.cleanup_tasks()
                    cleanup_counter = 0

            except queue.Empty:
                # Queue is empty, continue
                pass
            except Exception as e:
                self.logger.error(f"Error processing result: {str(e)}")
                import traceback

                self.logger.error(f"Traceback: {traceback.format_exc()}")
                # Continue processing other results

    def _handle_memory_added(self, task_result: Dict[str, Any]):
        """
        Handle memory added event.

        Args:
            task_result: Task result data
        """
        # In a real implementation, this would trigger additional actions
        # For now, just log the event
        self.logger.info(f"Memory added: {task_result.get('memory_id')}")

    def _handle_trade_executed(self, task_result: Dict[str, Any]):
        """
        Handle trade executed event.

        Args:
            task_result: Task result data
        """
        # In a real implementation, this would trigger additional actions
        # For now, just log the event
        self.logger.info(
            f"Trade executed: {task_result.get('result', {}).get('trade_id')}"
        )

    def cleanup_tasks(self, force: bool = False):
        """
        Clean up old and completed tasks to prevent memory leaks.

        This method removes tasks from the tasks dictionary based on several criteria:
        1. Tasks that have been completed/failed/errored and are older than task_retention_hours
        2. If the total number of tasks exceeds max_tasks, remove the oldest ones

        Args:
            force: If True, run cleanup regardless of the cleanup interval

        Returns:
            int: Number of tasks removed
        """
        # Check if we need to run cleanup based on the interval
        if (
            not force
            and self.task_id_counter - self.last_cleanup_count < self.cleanup_interval
        ):
            return 0

        self.last_cleanup_count = self.task_id_counter
        self.logger.debug(
            f"Running task cleanup. Current task count: {len(self.tasks)}"
        )

        # Get current time for age-based cleanup
        current_time = datetime.now()
        tasks_to_remove = []

        # First pass: identify tasks that can be removed based on age and status
        for task_id, task_info in self.tasks.items():
            # Check if task is in a terminal state (completed, failed, error)
            status = task_info.get("status")
            if status in ["completed", "failed", "error"]:
                # Check if it's older than our retention period
                created_at = task_info.get("created_at")
                if created_at:
                    age_hours = (current_time - created_at).total_seconds() / 3600
                    if age_hours > self.task_retention_hours:
                        tasks_to_remove.append((task_id, created_at))

        # If we're still over the limit, sort remaining tasks by age and remove oldest
        remaining_count = len(self.tasks) - len(tasks_to_remove)
        if remaining_count > self.max_tasks:
            # Get all tasks not already marked for removal
            remaining_tasks = [
                (tid, tinfo.get("created_at"))
                for tid, tinfo in self.tasks.items()
                if tid not in [t[0] for t in tasks_to_remove]
            ]
            # Sort by creation time (oldest first)
            remaining_tasks.sort(key=lambda x: x[1] if x[1] else datetime.max)
            # Mark additional tasks for removal to get under the limit
            tasks_to_remove.extend(remaining_tasks[: remaining_count - self.max_tasks])

        # Remove the identified tasks
        for task_id, _ in tasks_to_remove:
            if task_id in self.tasks:
                del self.tasks[task_id]

        removed_count = len(tasks_to_remove)
        if removed_count > 0:
            self.logger.info(
                f"Cleaned up {removed_count} tasks. Remaining: {len(self.tasks)}"
            )

        return removed_count

    def schedule_task(
        self,
        task_type: str,
        content: Dict[str, Any],
        interval_seconds: int,
        priority: AgentPriority = AgentPriority.LOW,
    ):
        """
        Schedule a task to run periodically.

        Args:
            task_type: Type of task to schedule
            content: Task content and parameters
            interval_seconds: How often to run the task (in seconds)
            priority: Task priority
        """
        task_id = f"scheduled_{task_type}_{uuid.uuid4().hex[:8]}"
        self.scheduled_tasks[task_id] = {
            "task_type": task_type,
            "content": content,
            "interval": interval_seconds,
            "priority": priority,
            "last_run": 0,  # Never run yet
        }
        self.logger.info(
            f"Scheduled task {task_id} of type {task_type} to run every {interval_seconds} seconds"
        )

        # Make sure scheduler is running
        self._start_scheduler()

        return task_id

    def _start_scheduler(self):
        """
        Start the scheduler thread if it's not already running.
        """
        if self.scheduler_thread is None or not self.scheduler_thread.is_alive():
            self.scheduler_thread = threading.Thread(target=self._scheduler_loop)
            self.scheduler_thread.daemon = True
            self.scheduler_thread.start()
            self.logger.info("Started scheduler thread")

    def _scheduler_loop(self):
        """
        Main loop for the scheduler thread.
        """
        self.logger.info("Scheduler thread started")

        while self.running:
            try:
                current_time = time.time()

                # Check if any scheduled tasks need to run
                for task_id, task_info in list(self.scheduled_tasks.items()):
                    if current_time - task_info["last_run"] >= task_info["interval"]:
                        # Time to run this task
                        self.logger.info(
                            f"Running scheduled task {task_id} of type {task_info['task_type']}"
                        )

                        # Create and submit the task
                        task = AgentTask(
                            task_id=f"{task_id}_{int(current_time)}",
                            task_type=task_info["task_type"],
                            content=task_info["content"],
                            priority=task_info["priority"],
                        )

                        # Route the task
                        if task_info["task_type"] in self.task_type_to_agent:
                            service = self.task_type_to_agent[task_info["task_type"]][
                                "service"
                            ]
                            try:
                                # Process the task with the registered service
                                result = service.process_task(task.content)
                                self.logger.info(
                                    f"Processed scheduled task {task_id} with result: {result}"
                                )
                            except Exception as e:
                                self.logger.error(
                                    f"Error processing scheduled task {task_id}: {str(e)}"
                                )
                        else:
                            # Use the router if no direct service is available
                            if not self.router.route_task(task):
                                self.logger.error(
                                    f"Could not route scheduled task {task_id}"
                                )

                        # Update last run time
                        self.scheduled_tasks[task_id]["last_run"] = current_time

                # Sleep for a bit to avoid high CPU usage
                time.sleep(1.0)

            except Exception as e:
                self.logger.error(f"Error in scheduler loop: {str(e)}")
                import traceback

                self.logger.error(f"Traceback: {traceback.format_exc()}")
                time.sleep(5.0)  # Sleep longer after an error

        self.logger.info("Scheduler thread stopped")

    def process_task_sync(self, task: AgentTask, timeout: int = 30) -> Dict[str, Any]:
        """
        Process a task synchronously and return the result.

        This method creates a task and waits for its completion, then returns the result.
        It's useful for helper functions that need to get results immediately.

        Args:
            task: The task to process
            timeout: Maximum time to wait for task completion in seconds

        Returns:
            Dict: Task result
        """
        self.logger.info(
            f"Processing task {task.task_id} of type {task.task_type} synchronously"
        )

        try:
            # Run task cleanup if needed
            self.cleanup_tasks()

            # First, check if we have a registered service for this task type
            if task.task_type in self.task_type_to_agent:
                service = self.task_type_to_agent[task.task_type]["service"]
                try:
                    # Process the task with the registered service
                    result = service.process_task(task.content)
                    self.logger.info(
                        f"Processed task {task.task_id} with registered service for {task.task_type}"
                    )
                    return result
                except Exception as e:
                    self.logger.error(
                        f"Error processing task {task.task_id} with registered service: {str(e)}"
                    )
                    # Continue to try routing the task

            # If no registered service or processing failed, use the router
            if not self.router.route_task(task):
                self.logger.error(f"Could not route task {task.task_id} to any agent")
                return {"error": "Could not route task to any agent", "status": "error"}

            # Store task in tasks dictionary
            self.tasks[task.task_id] = {
                "status": "pending",
                "task": task,
                "created_at": datetime.now(),
            }

            # Wait for task completion
            start_time = time.time()
            while time.time() - start_time < timeout:
                task_status = self.get_task_status(task.task_id)

                if task_status.status == "completed":
                    # Return the result
                    return task_status.result
                elif task_status.status == "failed" or task_status.status == "error":
                    # Return error information
                    return {"error": task_status.error, "status": "error"}

                # Small delay before checking again
                time.sleep(0.5)

            # Handle timeout
            self.logger.warning(f"Task {task.task_id} processing timed out")
            return {"error": "Task processing timed out", "status": "timeout"}

        except Exception as e:
            self.logger.error(f"Error in process_task_sync: {str(e)}")
            import traceback

            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return {"error": str(e), "status": "error"}


# Example usage
if __name__ == "__main__":
    # Initialize agent manager
    agent_manager = SystemAgentManager()

    # Start all agents
    agent_manager.start_all_agents()

    try:
        # Create a task
        task_id = agent_manager.create_task(
            task_type="ping", content={}, priority=AgentPriority.MEDIUM
        )
        print(f"Created task: {task_id}")

        # Wait for a while
        time.sleep(5)
    finally:
        # Stop all agents
        agent_manager.stop_all_agents()
