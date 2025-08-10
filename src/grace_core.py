import os
import time
import sys
import json
import logging
import asyncio
import importlib.util
from typing import Dict, List, Any, Optional, Union
import re
import threading
import queue
import traceback
from concurrent.futures import ThreadPoolExecutor

# Assuming these imports are correct based on the provided files
from src.memory_system import MemorySystem
from src.config import get_config
from src.system_prompts import get_system_prompt
from src.agent_framework import SystemAgentManager, AgentPriority
from src.user_profile import SecureDataManager, UserProfileSystem
from src.gmgn_service import GMGNService
from src.solana_wallet import SolanaWalletManager
from src.transaction_confirmation import TransactionConfirmationSystem
from src.research_service import ResearchService
from src.conversation_management_wrapper import ConversationManager, create_conversation_management_system
from src.leverage_trading_handler import LeverageTradeManager
from src.social_media_service import SocialMediaService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("GraceCore")

class GraceCore:
    """Core class for Grace - an AI assistant based on Open Interpreter
    with crypto trading capabilities."""

    def __init__(
        self,
        config_path: Optional[str] = None,
        data_dir: Optional[str] = None,
        encryption_key: Optional[str] = None,
        test_mode: bool = False
    ):
        """Initialize Grace Core.

        Args:
            config_path: Path to configuration file
            data_dir: Directory for data storage
            encryption_key: Key for data encryption
            test_mode: Whether to run in test mode
        """
        logger.info("Initializing Grace Core")

        # Load configuration
        self.config = self._load_config(config_path)

        # Set and create data directories
        self.data_dir = data_dir or self.config.get("data_dir", os.path.join(os.getcwd(), "data"))
        os.makedirs(self.data_dir, exist_ok=True)

        # Create users directory
        users_dir = os.path.join(self.data_dir, "users")
        os.makedirs(users_dir, exist_ok=True)

        # Create profiles.json if it doesn\'t exist
        profiles_path = os.path.join(self.data_dir, "profiles.json")
        if not os.path.exists(profiles_path):
            with open(profiles_path, 'w') as f:
                json.dump({}, f)

        # Set encryption key
        self.encryption_key = encryption_key or self.config.get("encryption_key", os.environ.get('FERNET_KEY', 'dGhpc19pc19hX3Byb3Blcl8zMl9ieXRlX2Zlcm5ldF9rZXk='))
        # Test mode flag
        self.test_mode = test_mode

        # Initialize components (order matters for dependencies)
        self.secure_data_manager = self._init_secure_data_manager()
        self.user_profile_system = self._init_user_profile_system()
        self.memory_system = self._init_memory_system()
        self.conversation_manager = self._init_conversation_manager()
        self.gmgn_service = self._init_gmgn_service()
        self.solana_wallet_manager = self._init_solana_wallet_manager() # Needs to be initialized before transaction_confirmation
        self.internal_wallet_manager = self._init_internal_wallet_manager() # Initialize internal wallet manager
        self.transaction_confirmation = self._init_transaction_confirmation()
        self.research_service = self._init_research_service() # Initialize Research Service
        self.leverage_trade_manager = self._init_leverage_trade_manager() # Initialize Leverage Trade Manager
        self.social_media_service = self._init_social_media_service() # Initialize Social Media Service
        self.agent_manager = self._init_agent_manager() # Initialize Agent Manager

        # Initialize Open Interpreter components if not in test mode
        self.interpreter = None
        self.interpreter_core = None
        if not test_mode:
            try:
                self.interpreter = self._init_interpreter_core()
                self.interpreter_core = self.interpreter  # For backward compatibility
                # Update the research service with the interpreter now that it's available
                if hasattr(self, 'research_service') and self.research_service and self.interpreter:
                    self.research_service.interpreter = self.interpreter
                    logger.info("Updating Research Service with interpreter")
                logger.info("Successfully initialized Open Interpreter")
            except Exception as e:
                logger.error(f"Failed to initialize Open Interpreter: {str(e)}")
                logger.error("Running without Open Interpreter integration")
        else:
            logger.info("Running in test mode, skipping Open Interpreter initialization")
            
        # Agents are already initialized and started in _init_agent_manager
        
        # Set up memory pruning
        self._setup_memory_pruning()

        # Current user context (Consider managing this per request instead of globally)
        self.current_user_id = None
        self.current_session_id = None

        # One-time disclosure shown status
        self.disclosure_shown = {}
        
        # Initialize the enhanced conversation flow if not in test mode
        if not test_mode:
            try:
                self._init_enhanced_conversation_flow()
                logger.info("Enhanced conversation flow initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize enhanced conversation flow: {str(e)}")
                logger.error("Running with standard conversation flow")

        logger.info("Grace Core initialized successfully")

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file."""
        default_config = {
            "data_dir": os.path.join(os.getcwd(), "data"),
            "encryption_key": os.environ.get('FERNET_KEY', 'dGhpc19pc19hX3Byb3Blcl8zMl9ieXRlX2Zlcm5ldF9rZXk='),
            "solana_rpc_url": "https://mainnet.helius-rpc.com/?api-key=aa07df83-e1ac-4117-b00d-173e94e4fff7",
            "solana_network": "mainnet-beta",
            "gmgn_router_endpoint": "https://gmgn.ai/defi/router/v1/sol/tx/get_swap_route",
            "gmgn_price_endpoint": "https://www.gmgn.cc/kline/{chain}/{token}",
            "authorized_admin_email": "kmanjo11@gmail.com",
            "phantom_app_url": "https://phantom.app",
            "phantom_callback_path": "/phantom/callback",
            "jwt_secret": "grace_default_jwt_secret",
            "research_api_key": os.environ.get("RESEARCH_API_KEY", None) # Example for research service config
        }

        if not config_path:
            logger.info("No config path provided, using default configuration")
            return default_config

        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                logger.info(f"Loaded configuration from {config_path}")
                merged_config = {**default_config, **config}
                return merged_config
        except Exception as e:
            logger.error(f"Error loading configuration from {config_path}: {str(e)}")
            logger.info("Using default configuration")
            return default_config

    def _init_secure_data_manager(self):
        """Initialize the secure data manager."""
        logger.info("Initializing Secure Data Manager")
        profiles_path = os.path.join(self.data_dir, "profiles.json")
        phantom_app_url = self.config.get("phantom_app_url", "https://phantom.app")
        phantom_callback_path = self.config.get("phantom_callback_path", "/phantom/callback")
        jwt_secret = self.config.get("jwt_secret", "grace_default_jwt_secret")
        return SecureDataManager(
            profiles_path=profiles_path,
            fernet_key=self.encryption_key,
            jwt_secret=jwt_secret,
            phantom_app_url=phantom_app_url,
            phantom_callback_path=phantom_callback_path
        )

    def _init_user_profile_system(self):
        """Initialize the user profile system."""
        logger.info("Initializing User Profile System")
        user_data_dir = os.path.join(self.data_dir, "users")
        os.makedirs(user_data_dir, exist_ok=True)
        profiles_path = os.path.join(self.data_dir, "profiles.json")
        if not os.path.exists(profiles_path):
            with open(profiles_path, 'w') as f:
                json.dump({}, f)
        return UserProfileSystem(
            data_dir=user_data_dir,
            secure_data_manager=self.secure_data_manager,
            profiles_path=profiles_path
        )

    def _init_memory_system(self):
        """Initialize the memory system."""
        logger.info("Initializing Memory System")
        chroma_dir = os.environ.get('GRACE_CHROMA_DIR', os.path.join(self.data_dir, "chromadb"))
        os.makedirs(chroma_dir, exist_ok=True)
        return MemorySystem(
            chroma_db_path=chroma_dir,
            user_profile_system=self.user_profile_system
        )
        
    def _init_conversation_manager(self):
        """Initialize the conversation management system with robust state persistence."""
        logger.info("Initializing Conversation Management System with enhanced state persistence")
        conversation_dir = os.path.join(self.data_dir, "conversations")
        os.makedirs(conversation_dir, exist_ok=True)
        
        # Create a state lock file to prevent race conditions
        lock_file = os.path.join(conversation_dir, "state.lock")
        
        # Ensure we're not initializing during an existing operation
        if os.path.exists(lock_file):
            try:
                # Check if lock is stale (more than 5 minutes old)
                lock_time = os.path.getmtime(lock_file)
                if time.time() - lock_time > 300:  # 5 minutes
                    logger.warning("Found stale lock file, removing it")
                    os.remove(lock_file)
                else:
                    logger.warning("Conversation system is currently being modified by another process")
            except Exception as e:
                logger.error(f"Error checking lock file: {e}")
        
        # Create the lock file to indicate we're initializing
        try:
            with open(lock_file, 'w') as f:
                f.write(str(time.time()))
        except Exception as e:
            logger.error(f"Error creating lock file: {e}")
        
        try:
            # Create conversation manager asynchronously with proper error handling
            loop = asyncio.new_event_loop()  # Always create a new loop to avoid conflicts
            asyncio.set_event_loop(loop)
            
            try:
                # Use a timeout to prevent hanging
                conversation_manager = loop.run_until_complete(
                    asyncio.wait_for(
                        create_conversation_management_system(conversation_dir),
                        timeout=30  # 30 second timeout for initialization
                    )
                )
                logger.info("Conversation management system initialized successfully")
            except asyncio.TimeoutError:
                logger.error("Conversation manager initialization timed out")
                raise RuntimeError("Conversation manager initialization timed out")
            finally:
                loop.close()
                
            # Validate the conversation manager was properly initialized
            if not hasattr(conversation_manager, 'get_or_create_context'):
                logger.error("Conversation manager was not properly initialized")
                raise ValueError("Invalid conversation manager instance")
                
            # Verify storage is working by writing and reading a test value
            test_ctx_id = str(uuid.uuid4())
            test_context = conversation_manager.create_context("test_user", test_ctx_id)
            
            # Save the test context
            if hasattr(conversation_manager, 'save_context') and callable(conversation_manager.save_context):
                if asyncio.iscoroutinefunction(conversation_manager.save_context):
                    # Handle async save_context
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        loop.run_until_complete(conversation_manager.save_context(test_context))
                    finally:
                        loop.close()
                else:
                    # Handle sync save_context
                    conversation_manager.save_context(test_context)
                    
                logger.info("Verified conversation persistence is working correctly")
            else:
                logger.warning("Conversation manager doesn't have expected save_context method")
                
            return conversation_manager
            
        except Exception as e:
            logger.error(f"Error initializing conversation manager: {str(e)}")
            # Create a basic fallback conversation manager if initialization fails
            from conversation_management import ConversationManager
            return ConversationManager(conversation_dir)
        finally:
            # Always remove the lock file when done
            try:
                if os.path.exists(lock_file):
                    os.remove(lock_file)
            except Exception as e:
                logger.error(f"Error removing lock file: {e}")

    def _init_gmgn_service(self):
        """Initialize the GMGN service with Mango V3 as primary trading service."""
        logger.info("Initializing GMGN Service with Mango V3 integration")
        
        # Initialize Mango spot market first
        from src.mango_spot_market import MangoSpotMarket
        from src.trading_service_selector import TradingServiceSelector
        
        # Ensure we have a valid mango_url, using a default if not present in config
        mango_url = self.config.get("mango_v3_endpoint")
        if not mango_url:
            mango_url = "http://localhost:8080"  # Default fallback URL on port 8080
            logger.info(f"No Mango V3 endpoint configured, using default: {mango_url}")
        
        mango_config = {
            "mango_url": mango_url,  # Guaranteed to have a value now
            "private_key_path": self.config.get("mango_private_key_path")
        }
        
        # Initialize GMGN with standard config
        gmgn_config = {
            "trade_endpoint": self.config.get("gmgn_router_endpoint"),
            # Charts must stay with GMGN for consistent display and data format
            "price_chart_endpoint": self.config.get("gmgn_price_endpoint"),  # GMGN-only chart endpoint
            "solana_rpc_url": self.config.get("solana_rpc_url"),
            "solana_network": self.config.get("solana_network")
        }
        
        # Initialize the trading service selector (sets up both services)
        logger.info("Initializing Trading Service Selector with Mango V3 as primary")
        trading_service_selector = TradingServiceSelector(
            config={
                "mango": mango_config,
                "gmgn": gmgn_config
            },
            memory_system=self.memory_system
        )
        
        # Initialize the GMGN service directly as well for backward compatibility
        gmgn_service = GMGNService(
            memory_system=self.memory_system,
            config=gmgn_config
        )
        
        # Store both services on the instance
        self.trading_service_selector = trading_service_selector
        
        # Store a direct reference to the Mango V3 extension for direct access
        # This prevents 'GraceCore' object has no attribute 'mango_v3_extension' errors
        self.mango_v3_extension = trading_service_selector.services[trading_service_selector.primary_service]
        
        # Log that we've set up the trading service selector
        logger.info("Trading Service Selector initialized with Mango V3 as primary service")
        logger.info("Direct reference to Mango V3 extension created for backward compatibility")
        
        return gmgn_service

    def _init_internal_wallet_manager(self):
        """Initialize the internal wallet manager for seamless wallet integration with Mango V3."""
        logger.info("Initializing Internal Wallet Manager for Mango V3 integration")
        
        try:
            from src.wallet_connection import InternalWalletManager
            
            # Create wallet manager with proper configuration - only pass the secure_data_manager
            internal_wallet_manager = InternalWalletManager(
                secure_data_manager=self.secure_data_manager
            )
            
            # Add the data_dir as an attribute after initialization
            internal_wallet_manager.data_dir = self.data_dir
            internal_wallet_manager.solana_rpc_url = self.config.get("solana_rpc_url", "https://api.mainnet-beta.solana.com")
            
            logger.info("Internal Wallet Manager successfully initialized")
            return internal_wallet_manager
            
        except ImportError as e:
            logger.error(f"Failed to import InternalWalletManager: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error initializing internal wallet manager: {str(e)}")
            return None
            
    def _init_solana_wallet_manager(self):
        """Initialize the Solana wallet manager."""
        logger.info("Initializing Solana Wallet Manager")
        # Initialize SolanaWalletManager with all necessary dependencies
        return SolanaWalletManager(
            config=self.config,
            user_profile_system=self.user_profile_system,
            gmgn_service=self.gmgn_service,
            secure_data_manager=self.secure_data_manager
        )

    def _init_transaction_confirmation(self):
        """Initialize the transaction confirmation system."""
        logger.info("Initializing Transaction Confirmation System")
        try:
            return TransactionConfirmationSystem(
                solana_wallet_manager=self.solana_wallet_manager,
                user_profile_system=self.user_profile_system,
                gmgn_service=self.gmgn_service,
                config=self.config.get("transaction_confirmation", {})
            )
        except Exception as e:
            logger.error(f"Failed to initialize Transaction Confirmation System: {str(e)}")
            return None
            
    def _init_research_service(self):
        """Initialize the Research Service."""
        logger.info("Initializing Research Service")
        try:
            # ResearchService only accepts memory_system and interpreter parameters
            research_service = ResearchService(
                memory_system=self.memory_system,
                interpreter=None  # Will be set later if OpenInterpreter is available
            )
            return research_service
        except Exception as e:
            logger.error(f"Failed to initialize Research Service: {str(e)}")
            return None

    def _init_leverage_trade_manager(self):
        """Initialize the Leverage Trade Manager."""
        logger.info("Initializing Leverage Trade Manager")
        try:
            # Get the GMGN service if available
            gmgn_service = getattr(self, 'gmgn_service', None)
            
            # Initialize with required services and configuration
            manager = LeverageTradeManager(
                gmgn_service=gmgn_service,
                memory_system=getattr(self, 'memory_system', None),
                logger=logger,
                **self.config.get("leverage_trading", {})
            )
            
            return manager
        except Exception as e:
            logger.error(
                f"Failed to initialize Leverage Trade Manager: {str(e)}",
                exc_info=True
            )
            return None
        
    def _init_social_media_service(self):
        """Initialize the Social Media Service."""
        logger.info("Initializing Social Media Service")
        try:
            return SocialMediaService(
                memory_system=self.memory_system,
                cache_duration=int(self.config.get("social_media_cache_duration", 3600)),
                config=self.config.get("social_media", {})
            )
        except Exception as e:
            logger.error(f"Failed to initialize Social Media Service: {str(e)}")
            return None
            
    def _setup_memory_pruning(self):
        """Set up periodic memory pruning."""
        logger.info("Setting up periodic memory pruning")
        
        # Check if memory system is available
        if not hasattr(self, 'memory_system') or not self.memory_system:
            logger.warning("Memory system not available, skipping memory pruning setup")
            return
            
        # Define pruning interval (in seconds)
        pruning_interval = self.config.get("memory_pruning_interval", 3600)  # Default: 1 hour
        
        def pruning_task():
            """Task to periodically prune expired memories."""
            while True:
                try:
                    logger.info("Running memory pruning task")
                    self.memory_system.prune_expired_memories()
                    logger.info("Memory pruning completed successfully")
                except Exception as e:
                    logger.error(f"Error during memory pruning: {str(e)}")
                finally:
                    # Sleep for the specified interval
                    time.sleep(pruning_interval)
        
        # Start pruning thread
        pruning_thread = threading.Thread(target=pruning_task, daemon=True)
        pruning_thread.start()
        logger.info(f"Memory pruning scheduled every {pruning_interval} seconds")

    def _get_grace_system_message(self):
        """Get the Grace system message from system_prompts.py."""
        # Get a comprehensive system message that includes all prompt components
        base_prompt = get_system_prompt("general")
        trading_prompt = get_system_prompt("trading")
        research_prompt = get_system_prompt("research")
        
        # Combine all prompts into a comprehensive system message
        # We need to extract just the trading and research specific parts
        trading_specific = trading_prompt.replace(base_prompt, "").strip()
        research_specific = research_prompt.replace(base_prompt, "").strip()
        
        # Combine all components
        system_message = f"{base_prompt}\n\n{trading_specific}\n\n{research_specific}"
        
        return system_message

    def _init_agent_manager(self):
        """Initialize the Agent Manager for the multi-agent framework."""
        logger.info("Initializing Agent Manager")
        # Create the agent manager with the necessary dependencies
        from src.agent_framework import SystemAgentManager, AgentType, AgentPriority
            
        agent_manager = SystemAgentManager(
            memory_system=self.memory_system,
            api_services_manager=self.gmgn_service,  # Use the existing GMGN service
            wallet_connection_system=self.solana_wallet_manager
        )
            
        # Import the conversation manager for process_message tasks
        from conversation_management import ConversationManager
        conversation_storage_dir = os.path.join(self.data_dir, "conversations")
        os.makedirs(conversation_storage_dir, exist_ok=True)
        conversation_manager = ConversationManager(storage_dir=conversation_storage_dir)
            
        # Register specialized agents for specific task types
        # Core message processing
        agent_manager.register_agent_for_task_type("process_message", conversation_manager, AgentPriority.HIGH)
            
        # Memory operations
        agent_manager.register_agent_for_task_type("query_memory", self.memory_system, AgentPriority.MEDIUM)
        agent_manager.register_agent_for_task_type("add_memory", self.memory_system, AgentPriority.MEDIUM)
        agent_manager.register_agent_for_task_type("remember", self.memory_system, AgentPriority.MEDIUM)
            
        # Trading operations
        agent_manager.register_agent_for_task_type("execute_trade", self.gmgn_service, AgentPriority.HIGH)
        agent_manager.register_agent_for_task_type("get_token_price", self.gmgn_service, AgentPriority.MEDIUM)
        agent_manager.register_agent_for_task_type("price_check", self.gmgn_service, AgentPriority.MEDIUM)
        agent_manager.register_agent_for_task_type("check_wallet_balance", self.gmgn_service, AgentPriority.MEDIUM)
        agent_manager.register_agent_for_task_type("trade_preparation", self.gmgn_service, AgentPriority.HIGH)
        agent_manager.register_agent_for_task_type("execute_swap", self.gmgn_service, AgentPriority.HIGH)
        agent_manager.register_agent_for_task_type("monitor_smart_trading", self.gmgn_service, AgentPriority.LOW)
        
        # Create and register LeverageTradeAgent
        from src.leverage_trade_agent import LeverageTradeAgent
        leverage_trade_agent = LeverageTradeAgent(
            agent_id="leverage_trade_agent",
            leverage_trade_manager=self.leverage_trade_manager,
            config=self.config
        )
        
        # Register LeverageTradeAgent for leverage trading operations
        agent_manager.register_agent(leverage_trade_agent)
        agent_manager.register_agent_for_task_type("execute_leverage_trade", leverage_trade_agent, AgentPriority.HIGH)
        agent_manager.register_agent_for_task_type("get_leverage_positions", leverage_trade_agent, AgentPriority.MEDIUM)
        agent_manager.register_agent_for_task_type("update_leverage_trade", leverage_trade_agent, AgentPriority.HIGH)
            
        # Schedule smart trading monitoring task to run every 5 minutes
        agent_manager.schedule_task(
            task_type="monitor_smart_trading",
            content={},  # No specific parameters needed
            interval_seconds=300,  # 5 minutes
            priority=AgentPriority.LOW
        )
        logger.info("Scheduled smart trading monitoring task to run every 5 minutes")
            
        # Community tracking operations
        agent_manager.register_agent_for_task_type("get_community_pulse", self.research_service, AgentPriority.MEDIUM)
            
        # Start all agents
        agent_manager.start_all_agents()
            
        # Log registered task types for debugging
        logger.info(f"Registered task types: {list(agent_manager.task_type_to_agent.keys())}")
            
        return agent_manager
            
    def _register_interpreter_functions(self, interpreter_instance):
        """Register helper functions with Open Interpreter to allow direct calls to the agent framework."""
        logger.info("Registering helper functions with Open Interpreter")
            
        try:
            # Check if the interpreter supports function registration
            if not hasattr(interpreter_instance, 'function') and not hasattr(interpreter_instance, 'register_function'):
                logger.warning("Open Interpreter does not support function registration")
                logger.warning("Memory system not available, skipping memory pruning setup")
                return
        except Exception as e:
            logger.error(f"Error checking interpreter capabilities: {str(e)}")

    def _init_agent_manager(self):
        """Initialize the Agent Manager for the multi-agent framework."""
        logger.info("Initializing Agent Manager")
        # Create the agent manager with the necessary dependencies
        from src.agent_framework import SystemAgentManager, AgentType, AgentPriority
        
        agent_manager = SystemAgentManager(
            memory_system=self.memory_system,
            api_services_manager=self.gmgn_service,  # Use the existing GMGN service
            wallet_connection_system=self.solana_wallet_manager
        )
        
        # Import the conversation manager for process_message tasks
        from conversation_management import ConversationManager
        conversation_storage_dir = os.path.join(self.data_dir, "conversations")
        os.makedirs(conversation_storage_dir, exist_ok=True)
        conversation_manager = ConversationManager(storage_dir=conversation_storage_dir)
        
        # Register specialized agents for specific task types
        # Core message processing
        agent_manager.register_agent_for_task_type("process_message", conversation_manager, AgentPriority.HIGH)
        
        # Memory operations
        agent_manager.register_agent_for_task_type("query_memory", self.memory_system, AgentPriority.MEDIUM)
        agent_manager.register_agent_for_task_type("add_memory", self.memory_system, AgentPriority.MEDIUM)
        agent_manager.register_agent_for_task_type("remember", self.memory_system, AgentPriority.MEDIUM)
        
        # Trading operations
        agent_manager.register_agent_for_task_type("execute_trade", self.gmgn_service, AgentPriority.HIGH)
        agent_manager.register_agent_for_task_type("get_token_price", self.gmgn_service, AgentPriority.MEDIUM)
        agent_manager.register_agent_for_task_type("price_check", self.gmgn_service, AgentPriority.MEDIUM)
        agent_manager.register_agent_for_task_type("check_wallet_balance", self.gmgn_service, AgentPriority.MEDIUM)
        agent_manager.register_agent_for_task_type("trade_preparation", self.gmgn_service, AgentPriority.HIGH)
        agent_manager.register_agent_for_task_type("execute_swap", self.gmgn_service, AgentPriority.HIGH)
        agent_manager.register_agent_for_task_type("monitor_smart_trading", self.gmgn_service, AgentPriority.LOW)
        
        # Schedule smart trading monitoring task to run every 5 minutes
        agent_manager.schedule_task(
            task_type="monitor_smart_trading",
            content={},  # No specific parameters needed
            interval_seconds=300,  # 5 minutes
            priority=AgentPriority.LOW
        )
        logger.info("Scheduled smart trading monitoring task to run every 5 minutes")
        
        # Community tracking operations
        agent_manager.register_agent_for_task_type("get_community_pulse", self.research_service, AgentPriority.MEDIUM)
        
        # Start all agents
        agent_manager.start_all_agents()
        
        # Log registered task types for debugging
        logger.info(f"Registered task types: {list(agent_manager.task_type_to_agent.keys())}")
        
        return agent_manager
        
    def _register_interpreter_functions(self, interpreter_instance):
        """Register helper functions with Open Interpreter to allow direct calls to the agent framework."""
        logger.info("Registering helper functions with Open Interpreter")
        
        try:
            # Check if the interpreter supports function registration
            if not hasattr(interpreter_instance, 'function') and not hasattr(interpreter_instance, 'register_function'):
                logger.warning("Open Interpreter does not support function registration")
                return
            
            # Define helper functions that will be registered with Open Interpreter
            
            # 1. Function to check token prices
            def check_token_price(token_symbol):
                """Get the current price of a cryptocurrency token.
                
                Args:
                    token_symbol (str): The symbol of the token to check (e.g., BTC, ETH, SOL)
                    
                Returns:
                    dict: Price information including current price and 24h change
                """
                logger.info(f"OI function called: check_token_price({token_symbol})")
                try:
                    # Validate input
                    if not token_symbol:
                        return {"error": "Token symbol is required", "status": "error"}
                    
                    # Normalize token symbol
                    if isinstance(token_symbol, str):
                        token_symbol = token_symbol.upper().strip()
                    else:
                        token_symbol = str(token_symbol).upper().strip()
                    
                    # Create and route a price_check task through the agent framework
                    task = self.agent_manager.create_task(
                        task_type="price_check",
                        content={"token_symbol": token_symbol, "user_id": "system"}
                    )
                    
                    # Process the task synchronously
                    result = self.agent_manager.process_task_sync(task)
                    
                    # Validate result
                    if not result or not isinstance(result, dict):
                        logger.warning(f"Invalid result from price_check task: {result}")
                        return {"error": "Invalid result from price check", "symbol": token_symbol, "status": "error"}
                    
                    # Check for errors in the result
                    if "error" in result:
                        logger.warning(f"Error in price_check result: {result['error']}")
                        return {"error": result["error"], "symbol": token_symbol, "status": "error"}
                    
                    # Add status if not present
                    if "status" not in result:
                        result["status"] = "success"
                    
                    # Add symbol if not present
                    if "symbol" not in result:
                        result["symbol"] = token_symbol
                    
                    return result
                except Exception as e:
                    logger.error(f"Error in check_token_price: {str(e)}")
                    import traceback
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    return {"error": str(e), "symbol": token_symbol, "status": "error"}
            
            # 2. Function to check wallet balance
            def check_wallet_balance(user_id=None):
                """Get the current wallet balance for a user.
                
                Args:
                    user_id (str, optional): The user ID to check balance for. Defaults to current user.
                    
                Returns:
                    dict: Wallet balance information
                """
                logger.info(f"OI function called: check_wallet_balance({user_id})")
                try:
                    # Use the current user ID if none is provided
                    if not user_id:
                        user_id = self.current_user_id or "system"
                        logger.info(f"Using current user ID: {user_id}")
                    
                    # Validate user_id
                    if not isinstance(user_id, str):
                        user_id = str(user_id)
                    
                    # Create and route a check_wallet_balance task through the agent framework
                    task = self.agent_manager.create_task(
                        task_type="check_wallet_balance",
                        content={"user_id": user_id}
                    )
                    
                    # Process the task synchronously
                    result = self.agent_manager.process_task_sync(task)
                    
                    # Validate result
                    if not result or not isinstance(result, dict):
                        logger.warning(f"Invalid result from check_wallet_balance task: {result}")
                        return {"error": "Invalid result from wallet balance check", "user_id": user_id, "status": "error"}
                    
                    # Check for errors in the result
                    if "error" in result:
                        logger.warning(f"Error in check_wallet_balance result: {result['error']}")
                        return {"error": result["error"], "user_id": user_id, "status": "error"}
                    
                    # Add status if not present
                    if "status" not in result:
                        result["status"] = "success"
                    
                    # Add user_id if not present
                    if "user_id" not in result:
                        result["user_id"] = user_id
                    
                    return result
                except Exception as e:
                    logger.error(f"Error in check_wallet_balance: {str(e)}")
                    import traceback
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    return {"error": str(e), "user_id": user_id, "status": "error"}
            
            # 3. Function to prepare a trade
            def prepare_trade(from_token, to_token, amount=None):
                """Prepare a trade between two tokens.
                
                Args:
                    from_token (str): The token to trade from
                    to_token (str): The token to trade to
                    amount (float, optional): The amount to trade. If None, will just show exchange rate.
                    
                Returns:
                    dict: Trade preparation information including exchange rate and estimated result
                """
                logger.info(f"OI function called: prepare_trade({from_token}, {to_token}, {amount})")
                try:
                    # Validate inputs
                    if not from_token or not to_token:
                        missing = []
                        if not from_token: missing.append("from_token")
                        if not to_token: missing.append("to_token")
                        return {"error": f"Missing required parameters: {', '.join(missing)}", "status": "error"}
                    
                    # Normalize token symbols
                    if isinstance(from_token, str):
                        from_token = from_token.upper().strip()
                    else:
                        from_token = str(from_token).upper().strip()
                        
                    if isinstance(to_token, str):
                        to_token = to_token.upper().strip()
                    else:
                        to_token = str(to_token).upper().strip()
                    
                    # Convert amount to float if provided
                    if amount is not None:
                        try:
                            amount = float(amount)
                        except (ValueError, TypeError):
                            logger.warning(f"Invalid amount format: {amount}, using None instead")
                            amount = None
                    
                    # Use the transaction confirmation system to prepare the trade
                    user_id = self.current_user_id or "system"
                    
                    # Prepare transaction parameters
                    parameters = {
                        "from_token": from_token,
                        "to_token": to_token
                    }
                    
                    # Add amount if provided
                    if amount is not None:
                        parameters["amount"] = amount
                    
                    # Use transaction confirmation system to prepare the transaction
                    result = self.transaction_confirmation.prepare_transaction(
                        user_id=user_id,
                        transaction_type="swap",
                        parameters=parameters,
                        wallet_type="internal"  # Default to internal wallet
                    )
                    
                    # Validate result
                    if not result or not isinstance(result, dict):
                        logger.warning(f"Invalid result from trade_initiate task: {result}")
                        return {"error": "Invalid result from trade preparation", 
                                "from_token": from_token, "to_token": to_token, "status": "error"}
                    
                    # Check for errors in the result
                    if "error" in result:
                        logger.warning(f"Error in trade_initiate result: {result['error']}")
                        return {"error": result["error"], "from_token": from_token, 
                                "to_token": to_token, "status": "error"}
                    
                    # Add status if not present
                    if "status" not in result:
                        result["status"] = "success"
                    
                    # Add tokens if not present
                    if "from_token" not in result:
                        result["from_token"] = from_token
                    if "to_token" not in result:
                        result["to_token"] = to_token
                    
                    return result
                except Exception as e:
                    logger.error(f"Error in prepare_trade: {str(e)}")
                    import traceback
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    return {"error": str(e), "from_token": from_token, "to_token": to_token, "status": "error"}
            
            # 4. Function to get market sentiment
            def get_market_sentiment(token=None):
                """Get the current market sentiment for a token or the overall market.
                
                Args:
                    token (str, optional): The token to check sentiment for. If None, checks overall market.
                    
                Returns:
                    dict: Sentiment information
                """
                logger.info(f"OI function called: get_market_sentiment({token})")
                try:
                    # Normalize token if provided
                    if token:
                        if isinstance(token, str):
                            token = token.upper().strip()
                        else:
                            token = str(token).upper().strip()
                    
                    # Create and route a get_community_pulse task through the agent framework
                    task = self.agent_manager.create_task(
                        task_type="get_community_pulse",
                        content={
                            "token": token, 
                            "user_id": self.current_user_id or "system"
                        }
                    )
                    
                    # Process the task synchronously
                    result = self.agent_manager.process_task_sync(task)
                    
                    # Validate result
                    if not result or not isinstance(result, dict):
                        logger.warning(f"Invalid result from get_community_pulse task: {result}")
                        return {"error": "Invalid result from market sentiment check", 
                                "token": token, "status": "error"}
                    
                    # Check for errors in the result
                    if "error" in result:
                        logger.warning(f"Error in get_community_pulse result: {result['error']}")
                        return {"error": result["error"], "token": token, "status": "error"}
                    
                    # Add status if not present
                    if "status" not in result:
                        result["status"] = "success"
                    
                    # Add token if not present and was provided
                    if token and "token" not in result:
                        result["token"] = token
                    
                    return result
                except Exception as e:
                    logger.error(f"Error in get_market_sentiment: {str(e)}")
                    import traceback
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    return {"error": str(e), "token": token, "status": "error"}
            
            # 5. Function to confirm a pending transaction
            def confirm_transaction(confirmation_id, user_id=None):
                """Confirm a pending transaction.
                
                Args:
                    confirmation_id (str): The ID of the transaction to confirm
                    user_id (str, optional): The user ID. Defaults to current user.
                    
                Returns:
                    dict: Transaction confirmation result
                """
                logger.info(f"OI function called: confirm_transaction({confirmation_id}, {user_id})")
                try:
                    # Validate input
                    if not confirmation_id:
                        return {"error": "Confirmation ID is required", "status": "error"}
                    
                    # Use current user if not specified
                    if not user_id:
                        user_id = self.current_user_id
                    
                    if not user_id:
                        return {"error": "User ID is required", "status": "error"}
                    
                    # Confirm the transaction
                    return self.transaction_confirmation.confirm_transaction(
                        user_id=user_id,
                        confirmation_id=confirmation_id
                    )
                except Exception as e:
                    logger.error(f"Error in confirm_transaction: {str(e)}")
                    import traceback
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    return {"error": str(e), "confirmation_id": confirmation_id, "status": "error"}
            
            # 6. Function to cancel a pending transaction
            def cancel_transaction(confirmation_id, user_id=None):
                """Cancel a pending transaction.
                
                Args:
                    confirmation_id (str): The ID of the transaction to cancel
                    user_id (str, optional): The user ID. Defaults to current user.
                    
                Returns:
                    dict: Transaction cancellation result
                """
                logger.info(f"OI function called: cancel_transaction({confirmation_id}, {user_id})")
                try:
                    # Validate input
                    if not confirmation_id:
                        return {"error": "Confirmation ID is required", "status": "error"}
                    
                    # Use current user if not specified
                    if not user_id:
                        user_id = self.current_user_id
                    
                    if not user_id:
                        return {"error": "User ID is required", "status": "error"}
                    
                    # Cancel the transaction
                    return self.transaction_confirmation.cancel_transaction(
                        user_id=user_id,
                        confirmation_id=confirmation_id
                    )
                except Exception as e:
                    logger.error(f"Error in cancel_transaction: {str(e)}")
                    import traceback
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    return {"error": str(e), "confirmation_id": confirmation_id, "status": "error"}
            
            # 7. Function to check transaction status
            def check_transaction_status(transaction_hash):
                """Check the status of a transaction on the blockchain.
                
                Args:
                    transaction_hash (str): The transaction hash to check
                    
                Returns:
                    dict: Transaction status information
                """
                logger.info(f"OI function called: check_transaction_status({transaction_hash})")
                try:
                    # Validate input
                    if not transaction_hash:
                        return {"error": "Transaction hash is required", "status": "error"}
                    
                    # Check transaction status
                    return self.transaction_confirmation.check_transaction_status(
                        transaction_hash=transaction_hash
                    )
                except Exception as e:
                    logger.error(f"Error in check_transaction_status: {str(e)}")
                    import traceback
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    return {"error": str(e), "transaction_hash": transaction_hash, "status": "error"}
            
            # 8. Function to process Phantom wallet callback
            def process_phantom_callback(transaction_id, signature):
                """Process callback from Phantom wallet after transaction approval.
                
                Args:
                    transaction_id (str): The transaction ID
                    signature (str): The transaction signature
                    
                Returns:
                    dict: Transaction result
                """
                logger.info(f"OI function called: process_phantom_callback({transaction_id}, {signature})")
                try:
                    # Validate input
                    if not transaction_id or not signature:
                        return {"error": "Transaction ID and signature are required", "status": "error"}
                    
                    # Process callback
                    return self.transaction_confirmation.process_phantom_callback(
                        transaction_id=transaction_id,
                        signature=signature
                    )
                except Exception as e:
                    logger.error(f"Error in process_phantom_callback: {str(e)}")
                    import traceback
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    return {"error": str(e), "transaction_id": transaction_id, "status": "error"}
            
            # 7. Function to get pending transactions
            def get_pending_transactions(user_id=None):
                """Get all pending transactions for a user.
                
                Args:
                    user_id (str, optional): The user ID. Defaults to current user.
                    
                Returns:
                    dict: Pending transactions
                """
                logger.info(f"OI function called: get_pending_transactions({user_id})")
                try:
                    # Use current user if not specified
                    if not user_id:
                        user_id = self.current_user_id
                    
                    if not user_id:
                        return {"error": "User ID is required", "status": "error"}
                    
                    # Get pending transactions
                    return self.transaction_confirmation.get_pending_transactions(
                        user_id=user_id
                    )
                except Exception as e:
                    logger.error(f"Error in get_pending_transactions: {str(e)}")
                    return {"error": str(e), "status": "error"}

            # Register all functions with the interpreter
            if hasattr(interpreter_instance, 'register_function'):
                interpreter_instance.register_function(prepare_trade)
                interpreter_instance.register_function(get_market_sentiment)
                interpreter_instance.register_function(confirm_transaction)
                interpreter_instance.register_function(cancel_transaction)
                interpreter_instance.register_function(get_pending_transactions)
                interpreter_instance.register_function(check_transaction_status)
                interpreter_instance.register_function(process_phantom_callback)
                logger.info("Registered functions with Open Interpreter using register_function method")
            else:
                # Try a more generic approach
                logger.warning("Using generic approach to register functions")
                try:
                    # Add functions to the interpreter's namespace
                    interpreter_instance.check_token_price = check_token_price
                    interpreter_instance.check_wallet_balance = check_wallet_balance
                    interpreter_instance.prepare_trade = prepare_trade
                    interpreter_instance.get_market_sentiment = get_market_sentiment
                    interpreter_instance.confirm_transaction = confirm_transaction
                    interpreter_instance.cancel_transaction = cancel_transaction
                    interpreter_instance.get_pending_transactions = get_pending_transactions
                    interpreter_instance.check_transaction_status = check_transaction_status
                    interpreter_instance.process_phantom_callback = process_phantom_callback
                    
                    # Update the system message to inform about available functions
                    function_info = """
                    
You have access to the following helper functions:
- check_token_price(token_symbol): Get the current price of a cryptocurrency token
- check_wallet_balance(user_id=None): Get the current wallet balance for a user
- prepare_trade(from_token, to_token, amount=None): Prepare a trade between two tokens
- get_market_sentiment(token=None): Get the current market sentiment for a token or the overall market
- confirm_transaction(confirmation_id, user_id=None): Confirm a pending transaction
- cancel_transaction(confirmation_id, user_id=None): Cancel a pending transaction
- get_pending_transactions(user_id=None): Get all pending transactions for a user
- check_transaction_status(transaction_hash): Check the status of a transaction on the blockchain
- process_phantom_callback(transaction_id, signature): Process callback from Phantom wallet after transaction approval

Use these functions when appropriate to provide accurate information to the user.
                    """
                    interpreter_instance.system_message += function_info
                    logger.info("Added functions to interpreter namespace and updated system message")
                except Exception as e:
                    logger.error(f"Failed to use generic approach for function registration: {e}")
        except Exception as e:
            logger.error(f"Error registering functions with Open Interpreter: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
    
    def _init_conversation_manager(self):
        """Initialize the conversation management system."""
        logger.info("Initializing Conversation Manager")
        conversation_data_dir = os.path.join(self.data_dir, "conversation_data")
        os.makedirs(conversation_data_dir, exist_ok=True)
        return ConversationManager(storage_dir=conversation_data_dir)
        
    def _init_interpreter_core(self):
        """Initialize Open Interpreter core with improved error handling."""
        try:
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable is not set")

            try:
                import interpreter
                from interpreter import OpenInterpreter
                logger.info("Successfully imported Open Interpreter")
            except ImportError as e:
                logger.error(f"Failed to import Open Interpreter: {e}")
                raise ImportError("Open Interpreter package is not installed") from e

            try:
                # Create a new interpreter instance with enhanced configuration
                interpreter_instance = OpenInterpreter()
                interpreter_instance.api_key = api_key
                interpreter_instance.model = "gpt-4" # Consider making this configurable
                interpreter_instance.context_window = 8192
                interpreter_instance.max_tokens = 2048
                
                # Enhanced system message with specific instructions about handling crypto queries
                base_system_message = self._get_grace_system_message()
                enhanced_system_message = base_system_message + """

When users ask about cryptocurrency prices, trading, or wallet information:
1. Respond naturally in a conversational manner
2. If they ask about prices, mention you're checking the latest data
3. If they ask about trading, explain the process clearly
4. Always maintain context from previous messages

You are designed to work with a specialized agent framework that handles crypto operations.
"""
                interpreter_instance.system_message = enhanced_system_message
                
                # Disable interactive mode to prevent waiting for user input
                interpreter_instance.auto_run = True  # Run code without asking for permission
                interpreter_instance.offline = False  # Don't use offline models
                
                # Set temperature for more natural responses
                interpreter_instance.temperature = 0.7
                
                # Register helper functions to allow OI to directly call the agent framework
                self._register_interpreter_functions(interpreter_instance)
                
                # Verify the chat method exists and is callable
                if not hasattr(interpreter_instance, 'chat') or not callable(getattr(interpreter_instance, 'chat')):
                    raise AttributeError("Interpreter instance missing required 'chat' method")

                logger.info("Successfully configured Open Interpreter with enhanced settings")
                return interpreter_instance
            except Exception as e:
                logger.error(f"Failed to configure Open Interpreter: {e}")
                raise
        except Exception as e:
            logger.error(f"Error initializing Open Interpreter core: {e}")
            raise

    def _update_research_service_interpreter(self):
        """Update the research service with the interpreter after it's initialized."""
        if hasattr(self, 'research_service') and self.research_service and hasattr(self, 'interpreter') and self.interpreter is not None:
            logger.info("Updating Research Service with interpreter")
            self.research_service.interpreter = self.interpreter
        else:
            if not hasattr(self, 'research_service') or not self.research_service:
                logger.error("Research service not initialized, cannot update with interpreter")
            if not hasattr(self, 'interpreter') or self.interpreter is None:
                logger.error("Interpreter not initialized, cannot update research service")

    def _init_enhanced_conversation_flow(self):
        """Initialize the enhanced conversation flow for improved context handling."""
        logger.info("Initializing Enhanced Conversation Flow")
        
        # Import the enhanced conversation flow
        try:
            from src.enhanced_conversation_flow import EnhancedConversationFlow
        except ImportError as e:
            logger.error(f"Failed to import EnhancedConversationFlow: {e}")
            raise ImportError("Enhanced conversation flow module is not available") from e
        
        # Check if all required components are available
        required_components = [
            ('memory_system', 'Memory System'),
            ('gmgn_service', 'GMGN Service'),
            ('conversation_manager', 'Conversation Manager'),
            ('interpreter', 'Open Interpreter')
        ]
        
        for attr, name in required_components:
            if not hasattr(self, attr) or getattr(self, attr) is None:
                logger.error(f"{name} is not available for enhanced conversation flow")
                raise ValueError(f"{name} is required for enhanced conversation flow")
        
        # Initialize the enhanced conversation flow
        self.enhanced_conversation_flow = EnhancedConversationFlow(
            grace_core=self,
            memory_system=self.memory_system,
            gmgn_service=self.gmgn_service,
            conversation_manager=self.conversation_manager,
            interpreter=self.interpreter
        )
        
        logger.info("Enhanced Conversation Flow initialized successfully")

    def _get_grace_system_message(self) -> str:
        """Get the system message for Grace."""
        # Removed Twitter reference as requested
        return (
            "You are Grace, an AI assistant based on Open Interpreter with crypto trading capabilities.\n\n"
            "Your capabilities include:\n"
            "1. Accessing and recalling information from a three-layer memory system\n"
            "2. Trading cryptocurrencies on the Solana blockchain via GMGN\n"
            "3. Performing web research on various topics\n"
            "4. Managing user wallets (both internal and Phantom)\n"
            "5. Executing code to perform various tasks\n\n"
            "When users ask about trading or wallet operations, always use the transaction confirmation "
            "system to ensure secure execution with explicit user approval.\n\n"
            "Special commands:\n"
            "- !grace.learn [information] - Add information to your long-term memory (admin only)\n"
            "- !grace.remember [query] - Search your memory for relevant information\n"
            "- !grace.wallet - Show wallet information\n"
            "- !grace.trade - Initiate a trading operation\n"
            "- !grace.research [topic] - Perform web research on the specified topic\n\n"
            "Always be helpful, accurate, and prioritize user security when dealing with financial transactions."
        )

    # Removed async _grace_message_handler as it conflicted with synchronous interpreter chat

    # The _initialize_agents method has been removed as it was causing duplicate agent initialization.
    # All agent initialization is now handled in the _init_agent_manager method.

    async def _process_with_conversation_manager(self, user_id: str, session_id: str, message: str):
        """Process a message using the conversation management system."""
        try:
            # Get or create conversation context
            context = await self.conversation_manager.get_or_create_context(user_id, session_id)
            context_id = context.context_id
            
            # Process the message
            processing_result = await self.conversation_manager.process_message(
                context_id=context_id,
                user_id=user_id,
                message=message
            )
            
            # Check if we have a method to generate context-aware prompts
            if hasattr(self.conversation_manager, 'generate_context_aware_prompt'):
                # Generate context-aware prompt
                prompt_data = await self.conversation_manager.generate_context_aware_prompt(
                    context_id=context_id,
                    user_id=user_id,
                    query=message
                )
            else:
                # If the method doesn't exist, create a basic prompt data structure
                prompt_data = {
                    'success': True,
                    'conversation_history': processing_result.get('context', {}).get('conversation_history', []),
                    'context_info': processing_result.get('context', {}),
                    'prompt_enhancement': processing_result.get('prompt_enhancement', '')
                }
            
            return context_id, processing_result, prompt_data
        except Exception as e:
            logger.error(f"Error processing with conversation manager: {str(e)}")
            return None, None, None
    
    def _handle_special_commands(self, user_id: str, session_id: str, message: str) -> Optional[str]:
        """Handle special commands like !grace.learn, !grace.remember, etc."""
        if message.startswith("!grace.learn"):
            if not self.user_profile_system.is_admin(user_id):
                return "Sorry, only administrators can use the !grace.learn command."
            _, *content_parts = message.split(maxsplit=1)
            if not content_parts:
                return "Usage: !grace.learn [information to learn]"
            content = content_parts[0]
            task_id = self.agent_manager.create_task(
                task_type="learn",
                content={"action": "learn", "content": content, "user_id": user_id},
                priority=AgentPriority.HIGH
            )
            return f"Okay, I will learn that. Task ID: {task_id}" # Return task ID, result will come later

        elif message.startswith("!grace.remember"):
            _, *query_parts = message.split(maxsplit=1)
            if not query_parts:
                return "Usage: !grace.remember [query]"
            query = query_parts[0]
            task_id = self.agent_manager.create_task(
                task_type="remember",
                content={"action": "remember", "query": query, "user_id": user_id},
                priority=AgentPriority.HIGH
            )
            return f"Searching memory... Task ID: {task_id}" # Return task ID, result will come later

        elif message.startswith("!grace.research"):
            _, *topic_parts = message.split(maxsplit=1)
            if not topic_parts:
                return "Usage: !grace.research [topic]"
            topic = topic_parts[0]
            task_id = self.agent_manager.create_task(
                task_type="research",
                content={"action": "research", "topic": topic, "user_id": user_id},
                priority=AgentPriority.MEDIUM
            )
            return f"Starting research on \'{topic}\'. Task ID: {task_id}" # Return task ID, result will come later

        elif message.startswith("!grace.trade"):
            # Example: Triggering a trade task
            # You would parse trade details from the message here
            trade_details = message.split(maxsplit=1)[1] if len(message.split(maxsplit=1)) > 1 else ""
            task_id = self.agent_manager.create_task(
                task_type="trade_initiate",
                content={"action": "trade_initiate", "details": trade_details, "user_id": user_id},
                priority=AgentPriority.HIGH
            )
            return f"Initiating trade... Task ID: {task_id}" # Return task ID, result will come later

        # Add handlers for !grace.wallet, !grace.help, etc.

        return None # Indicate no special command was handled

    def process_message(self, user_id: str, session_id: str, message: str) -> str:
        """Process an incoming user message using the enhanced conversation flow."""
        logger.info(f"Processing message from user {user_id} (session {session_id}): {message}")

        self.current_user_id = user_id
        self.current_session_id = session_id
        
        # Use the enhanced conversation flow if available
        if hasattr(self, 'enhanced_conversation_flow'):
            try:
                # Try to get the current event loop
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    # If no event loop exists in this thread, create a new one
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                # Process the message using the enhanced conversation flow
                return loop.run_until_complete(
                    self.enhanced_conversation_flow.process_message(user_id, session_id, message)
                )
            except Exception as e:
                logger.error(f"Error in enhanced conversation flow: {str(e)}")
                # Fall back to the original implementation if enhanced flow fails
        
        # Fallback to the original implementation if enhanced flow is not available
        # 1. Handle Special Commands via Agent Framework
        command_response = self._handle_special_commands(user_id, session_id, message)
        if command_response:
            # For commands that initiate tasks, we return the task ID immediately.
            # The actual result will be pushed back via a separate mechanism (e.g., WebSocket, polling)
            # or retrieved by the user later.
            # For now, we just return the initial response.
            logger.info(f"Handled special command: {command_response}")
            # Add message and response to short-term memory
            self.memory_system.add_to_short_term(
                user_id=user_id,
                text=message,
                metadata={"source": "user"}
            )
            self.memory_system.add_to_short_term(
                user_id=user_id,
                text=command_response,
                metadata={"source": "grace"}
            )
            return command_response
            
        # 2. Process with Conversation Manager
        try:
            # Use asyncio to run the async conversation manager methods
            try:
                # Try to get the current event loop
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    # If no event loop exists in this thread, create a new one
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                # Process with conversation manager
                context_id, processing_result, prompt_data = loop.run_until_complete(
                    self._process_with_conversation_manager(user_id, session_id, message)
                )
            except Exception as e:
                logger.error(f"Error running conversation manager: {str(e)}")
                # Create a new event loop as a last resort
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    context_id, processing_result, prompt_data = new_loop.run_until_complete(
                        self._process_with_conversation_manager(user_id, session_id, message)
                    )
                except Exception as inner_e:
                    logger.error(f"Failed to process with conversation manager: {str(inner_e)}")
                    context_id, processing_result, prompt_data = None, None, None
                finally:
                    new_loop.close()
                
            # Check if we have background tasks to create
            if processing_result and 'processing_result' in processing_result:
                background_tasks = processing_result['processing_result'].get('background_tasks', [])
                for task_info in background_tasks:
                    # Create background tasks in the agent framework
                    self.agent_manager.create_task(
                        task_type=task_info['type'],
                        content={
                            'task_id': task_info['task_id'],
                            'user_id': user_id,
                            'session_id': session_id
                        },
                        priority=AgentPriority.MEDIUM
                    )
        except Exception as e:
            logger.error(f"Error with conversation manager: {str(e)}")
            context_id, processing_result, prompt_data = None, None, None

        # 3. If not a special command, use Open Interpreter (if available)
        if self.interpreter:
            try:
                logger.info("Passing message to Open Interpreter")
                # Prepare context for Open Interpreter (e.g., memory)
                relevant_memory = self.memory_system.query_memory(
                    user_id=user_id,
                    query=message,
                    n_results=5
                )
                # Get conversation history - adjust method name based on your actual implementation
                conversation_history = []  # Initialize empty in case method fails
                try:
                    # Try to get conversation history using the actual method in your memory system
                    conversation_history = self.memory_system.get_conversation_context(user_id, n_messages=10)
                except Exception as e:
                    logger.warning(f"Could not retrieve conversation history: {str(e)}")

                # Construct messages for OI chat
                messages = conversation_history + [{
                    "role": "user",
                    "content": message
                }]
                
                # Call Open Interpreter with improved error handling
                try:
                    # Add context information to the message to help OI understand the conversation
                    if prompt_data and prompt_data.get('success', False):
                        context_info = prompt_data.get('context_info', {})
                        active_topics = context_info.get('active_topics', [])
                        if active_topics:
                            topic_names = [topic.get('name') for topic in active_topics if topic.get('name')]
                            if topic_names:
                                logger.info(f"Active topics detected: {topic_names}")
                    
                    # First, add the user message to memory
                    self.memory_system.add_to_short_term(
                        user_id=user_id,
                        text=message,
                        metadata={"source": "user"}
                    )
                    
                    # Call Open Interpreter with a try-except block for each potential error type
                    try:
                        # Use a timeout to prevent hanging
                        import threading
                        import concurrent.futures
                        
                        # Check if interpreter is available
                        if not self.interpreter:
                            logger.error("Open Interpreter is not available")
                            raise ValueError("Open Interpreter is not available")
                        
                        # Verify the chat method exists and is callable
                        if not hasattr(self.interpreter, 'chat') or not callable(getattr(self.interpreter, 'chat')):
                            logger.error("Open Interpreter instance missing required 'chat' method")
                            raise AttributeError("Interpreter instance missing required 'chat' method")
                        
                        # Validate messages format
                        if not isinstance(messages, list):
                            logger.error(f"Invalid messages format: {type(messages)}, expected list")
                            raise TypeError(f"Invalid messages format: {type(messages)}, expected list")
                        
                        # Ensure messages is not empty
                        if not messages:
                            logger.warning("Empty messages list provided to Open Interpreter")
                            messages = [{"role": "user", "content": message}]  # Fallback to just the current message
                        
                        def call_interpreter():
                            # Ensure all messages have the required fields
                            validated_messages = []
                            for msg in messages:
                                # Create a new message with required fields
                                validated_msg = {}
                                
                                # Ensure 'role' field exists
                                if "role" not in msg:
                                    if "type" in msg:
                                        # Map type to role if possible
                                        validated_msg["role"] = "user" if msg["type"] == "message" else "system"
                                    else:
                                        # Default to user role
                                        validated_msg["role"] = "user"
                                else:
                                    validated_msg["role"] = msg["role"]
                                
                                # Ensure 'content' field exists
                                if "content" not in msg:
                                    validated_msg["content"] = "" # Empty content as fallback
                                else:
                                    validated_msg["content"] = msg["content"]
                                
                                # Add type field for Open Interpreter
                                validated_msg["type"] = "message"
                                
                                # Copy any other fields
                                for key, value in msg.items():
                                    if key not in validated_msg:
                                        validated_msg[key] = value
                                
                                validated_messages.append(validated_msg)
                            
                            # Log the validated messages for debugging
                            logger.info(f"Sending validated messages to Open Interpreter: {validated_messages}")
                            return self.interpreter.chat(validated_messages)
                        
                        # Use a thread pool to call the interpreter with a timeout
                        with concurrent.futures.ThreadPoolExecutor() as executor:
                            future = executor.submit(call_interpreter)
                            try:
                                response = future.result(timeout=30)  # 30 second timeout
                            except concurrent.futures.TimeoutError:
                                logger.error("Open Interpreter call timed out")
                                raise TimeoutError("Open Interpreter call timed out")
                        
                        logger.info(f"Successfully received response from Open Interpreter: {type(response)}")
                        
                        # Process the response based on its type with improved error handling
                        try:
                            if response is None:
                                logger.warning("Open Interpreter returned None response")
                                response_text = "I'm sorry, I couldn't generate a response."
                            elif isinstance(response, list):
                                # Handle streaming response format
                                response_text = ""
                                for i, chunk in enumerate(response):
                                    try:
                                        if isinstance(chunk, dict) and chunk.get("role") == "assistant":
                                            content = chunk.get("content", "")
                                            if content:
                                                response_text += content
                                        elif isinstance(chunk, dict):
                                            # Try to extract content from other dict formats
                                            for key in ["content", "message", "text", "response"]:
                                                if key in chunk and chunk[key]:
                                                    response_text += str(chunk[key])
                                                    break
                                    except Exception as chunk_error:
                                        logger.error(f"Error processing chunk {i}: {str(chunk_error)}")
                                
                                if not response_text:
                                    logger.warning("Could not extract text from list response")
                                    # Try to convert the whole response to string as a fallback
                                    try:
                                        response_text = str(response)
                                    except:
                                        response_text = "I processed your request but couldn't format the response properly."
                            elif isinstance(response, dict):
                                # Handle single response format
                                for key in ["content", "message", "text", "response"]:
                                    if key in response and response[key]:
                                        response_text = str(response[key])
                                        break
                                else:
                                    # If no content found, log the keys and use a default message
                                    logger.warning(f"No content found in response dict. Keys: {list(response.keys())}")
                                    response_text = "I processed your request but couldn't find the response content."
                            elif hasattr(response, 'content') and response.content:
                                # Handle object with content attribute
                                response_text = str(response.content)
                            elif hasattr(response, 'message') and response.message:
                                # Handle object with message attribute
                                response_text = str(response.message)
                            elif hasattr(response, 'text') and response.text:
                                # Handle object with text attribute
                                response_text = str(response.text)
                            elif hasattr(response, 'response') and response.response:
                                # Handle object with response attribute
                                response_text = str(response.response)
                            else:
                                # Handle any other response format
                                logger.warning(f"Unknown response type: {type(response)}")
                                try:
                                    response_text = str(response)
                                    if not response_text or response_text == str(type(response)):
                                        response_text = "I processed your request but couldn't format the response properly."
                                except:
                                    response_text = "I processed your request but couldn't format the response properly."
                        except Exception as format_error:
                            logger.error(f"Error formatting response: {str(format_error)}")
                            response_text = "I processed your request but encountered an issue formatting the response."
                        
                        # Add response to memory
                        self.memory_system.add_to_short_term(
                            user_id=user_id,
                            text=response_text,
                            metadata={"source": "grace"}
                        )
                        
                        return response_text
                    except TypeError as type_error:
                        # Handle the specific 'type' error we've been seeing
                        logger.error(f"Type error in Open Interpreter: {str(type_error)}")
                        # Get a detailed traceback for debugging
                        import traceback
                        logger.error(f"Traceback: {traceback.format_exc()}")
                        # Fall back to a simpler approach - just get a basic response
                        try:
                            # Try a simpler approach with just the latest message
                            simple_response = self.interpreter.chat([{"role": "user", "content": message}])
                            if isinstance(simple_response, list):
                                response_text = "".join([chunk.get("content", "") for chunk in simple_response 
                                                        if isinstance(chunk, dict) and chunk.get("role") == "assistant"])
                            elif isinstance(simple_response, dict):
                                response_text = simple_response.get("content", "")
                            else:
                                response_text = str(simple_response)
                                
                            # Add response to memory
                            self.memory_system.add_to_short_term(
                                user_id=user_id,
                                text=response_text,
                                metadata={"source": "grace"}
                            )
                            
                            return response_text
                        except Exception as inner_error:
                            logger.error(f"Simple approach also failed: {str(inner_error)}")
                            raise  # Re-raise to fall back to agent framework
                except Exception as e:
                    logger.error(f"Error using Open Interpreter: {str(e)}")
                    # Get a detailed traceback for debugging
                    import traceback
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    # Log the specific error type to help with debugging
                    logger.error(f"Error type: {type(e).__name__}")
                    # Fall back to agent framework with a specific error message
                    logger.info("Falling back to agent framework due to Open Interpreter error")
            except Exception as e:
                logger.error(f"Error preparing for Open Interpreter: {str(e)}")
                # Get a detailed traceback for debugging
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                # Log the specific error type to help with debugging
                logger.error(f"Error type: {type(e).__name__}")
                # Fall back to agent framework with a specific error message
                logger.info("Falling back to agent framework due to preparation error")
        
        # 4. If Open Interpreter is not available or failed, use the agent framework
        try:
            logger.info("Using agent framework for message processing")
            
            # Prepare context from conversation manager if available
            context_info = {}
            if prompt_data and prompt_data.get('success', False):
                context_info = {
                    "conversation_history": prompt_data.get('conversation_history', []),
                    "context_info": prompt_data.get('context_info', {}),
                    "prompt_enhancement": prompt_data.get('prompt_enhancement', "")
                }
            
            # Create task for message processing
            task_id = self.agent_manager.create_task(
                task_type="process_message",
                content={
                    "message": message,
                    "user_id": user_id,
                    "session_id": session_id,
                    "context": {
                        "memories": self.memory_system.query_memory(
                            user_id=user_id,
                            query=message,
                            n_results=5
                        ),
                        "conversation_context": context_info,
                        "system_message": self._get_grace_system_message()
                    }
                },
                priority=AgentPriority.HIGH
            )
            
            # Wait for task completion (synchronous approach)
            max_wait_time = 30  # seconds
            start_time = time.time()
            response_text = None
            
            while time.time() - start_time < max_wait_time:
                task_status = self.agent_manager.get_task_status(task_id)
                
                if task_status.status == "completed":
                    # Extract response from task result
                    if isinstance(task_status.result, dict):
                        response_text = task_status.result.get("response", "")
                    else:
                        response_text = str(task_status.result)
                    break
                    
                elif task_status.status == "failed":
                    logger.error(f"Task failed: {task_status.error}")
                    response_text = "I'm sorry, I encountered an error processing your request."
                    break
                    
                # Small delay before checking again
                time.sleep(0.5)
            
            # Handle timeout
            if response_text is None:
                logger.warning(f"Task {task_id} processing timed out")
                response_text = "I'm still thinking about your request. Please check back in a moment."
            
            # Add user message and response to memory
            self.memory_system.add_to_short_term(
                user_id=user_id,
                text=message,
                metadata={"source": "user"}
            )
            self.memory_system.add_to_short_term(
                user_id=user_id,
                text=response_text,
                metadata={"source": "grace"}
            )
            
            return response_text
            
        except Exception as e:
            logger.error(f"Error in agent framework processing: {str(e)}")
            return "I apologize, but I'm having trouble processing your request right now. Please try again in a moment."

# Run the application if executed directly
if __name__ == "__main__":
    grace = GraceCore()
    
    # Start the API server
    from src.api_server import app
    
    port = int(os.environ.get("PORT", 9000))
    app.run(host='0.0.0.0', port=port, debug=True)
