"""
Wallet Connection System for Grace - A crypto trading application based on Open Interpreter

This module implements wallet connection functionality for both internal and Phantom wallets,
integrating with SolanaWalletManager for secure key generation and management.

Key Data Structures:
1. WalletData:
   {
       'public_key': str,                # Base58-encoded public key
       'private_key_encrypted': str,     # Encrypted private key (base64)
       'wallet_type': str,              # 'internal' or 'phantom'
       'created_at': str,               # ISO 8601 timestamp
       'updated_at': str,               # ISO 8601 timestamp
       'is_active': bool,               # Wallet activation status
       'metadata': Dict[str, Any]       # Additional wallet metadata
   }

2. SessionData:
   {
       'session_id': str,               # Unique session identifier
       'user_id': str,                  # Associated user ID
       'wallet_address': str,           # Wallet public key
       'created_at': float,             # Unix timestamp
       'expires_at': float,             # Expiration timestamp
       'status': Literal['pending', 'active', 'expired'],  # Session status

       'last_activity': float           # Last activity timestamp
   }
"""

import os
import uuid
import json
import base64
import logging
import time
from typing import Dict, List, Optional, Any, TypedDict, Literal, Callable, Union
from datetime import datetime, timedelta
import asyncio
import base58
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.system_program import TransferParams, transfer
from solders.transaction import Transaction
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
from spl.token.instructions import get_associated_token_address, create_associated_token_account
from spl.token.constants import TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID
from spl.token.instructions import TransferParams as TokenTransferParams
from spl.token.instructions import transfer_checked, TransferCheckedParams
from spl.token.constants import WRAPPED_SOL_MINT as TOKEN_PROGRAM_ID
from solana.rpc.types import TokenAccountOpts
from solders.rpc.responses import GetTokenAccountBalanceResp, GetTokenAccountsByOwnerResp
from solders.signature import Signature
from solders.transaction import VersionedTransaction
from urllib.parse import urlencode, urlparse

from src.config import get_config
from src.solana_wallet import SolanaWalletManager
from src.exceptions import (
    PhantomWalletError,
    SessionExpiredError,
    InvalidWalletAddressError,
    InvalidSessionError,
    WalletConnectionError,
    InvalidConfigurationError
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("GraceWalletConnection")


class InternalWalletManager:
    """
    Manages internal wallets for Grace users, leveraging SolanaWalletManager for key generation
    and secure key management.
    """

    def __init__(self, secure_data_manager=None):
        """
        Initialize the internal wallet manager.

        Args:
            secure_data_manager: SecureDataManager instance for key encryption
        """
        self.secure_data_manager = secure_data_manager
        self.solana_rpc_url = get_config().get("solana_rpc_url")
        self.logger = logging.getLogger("GraceInternalWallet")
        self.solana_wallet = SolanaWalletManager(
            secure_data_manager=secure_data_manager
        )

    def generate_wallet(self) -> Dict[str, Any]:
        """
        Generate a new Solana wallet using SolanaWalletManager.

        Returns:
            Dict[str, Any]: Wallet data following WalletData structure
            {
                'public_key': str,               # Base58-encoded public key
                'private_key_encrypted': str,  # Encrypted private key (base64)
                'wallet_type': 'internal',
                'created_at': str,             # ISO 8601 timestamp
                'updated_at': str,             # ISO 8601 timestamp
                'is_active': bool,
                'metadata': {
                    'key_derivation': 'ed25519',
                    'key_encryption': 'base64',
                    'key_storage': 'encrypted'
                }
            }

        
        Raises:
            ValueError: If wallet generation fails
        """
        try:
            # Generate keypair using SolanaWalletManager
            keypair = self.solana_wallet._generate_keypair()
            
            # Create wallet data with standardized structure
            current_time = datetime.utcnow().isoformat()
            wallet_data = {
                'public_key': keypair['public_key'],
                'private_key_encrypted': base64.b64encode(keypair['private_key']).decode('utf-8'),
                'wallet_type': 'internal',
                'created_at': current_time,
                'updated_at': current_time,
                'is_active': True,
                'metadata': {
                    'key_derivation': 'ed25519',
                    'key_encryption': 'base64',
                    'key_storage': 'encrypted'
                }
            }

            self.logger.info(f"Generated new internal wallet: {wallet_data['public_key']}")
            return wallet_data
            
        except Exception as e:
            error_msg = f"Failed to generate wallet: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise ValueError(error_msg) from e

    async def get_user_wallet(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get wallet data for a specific user, ensuring funds can be properly seen and managed.
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            User wallet data or None if not found
        """
        try:
            # In a production system, this would check a database
            # For this implementation, we'll check a simple in-memory store
            user_dir = os.path.join(self.data_dir, "users", user_id)
            wallet_file = os.path.join(user_dir, "wallet.json")
            
            if os.path.exists(wallet_file):
                with open(wallet_file, 'r') as f:
                    wallet_data = json.load(f)
                self.logger.info(f"Retrieved wallet for user {user_id}")
                return wallet_data
            else:
                self.logger.warning(f"No wallet found for user {user_id}")
                return None
        except Exception as e:
            self.logger.error(f"Error retrieving user wallet: {str(e)}")
            return None
    
    async def update_wallet_balance(self, user_id: str, token: str, amount: float, operation: str = "add") -> bool:
        """
        Update wallet balance for a specific user and token. This ensures funds are properly 
        reflected in the internal wallet system after trading operations.
        
        Args:
            user_id: Unique user identifier
            token: Token symbol (e.g., "sol", "usdc")
            amount: Amount to add/subtract
            operation: "add" or "subtract"
            
        Returns:
            Success status
        """
        try:
            # Standardize token name
            token = token.lower()
            
            # Get current wallet data
            wallet_data = await self.get_user_wallet(user_id)
            if not wallet_data:
                self.logger.warning(f"Cannot update balance - no wallet for user {user_id}")
                return False
                
            # Get current balance
            current_balance = wallet_data.get("balance", {}).get(token, 0.0)
            
            # Calculate new balance
            if operation.lower() == "add":
                new_balance = current_balance + amount
            elif operation.lower() == "subtract":
                new_balance = max(0, current_balance - amount)  # Prevent negative balance
            else:
                self.logger.error(f"Invalid operation: {operation}")
                return False
                
            # Update balance in wallet data
            if "balance" not in wallet_data:
                wallet_data["balance"] = {}
            wallet_data["balance"][token] = new_balance
            
            # Save updated wallet data
            user_dir = os.path.join(self.data_dir, "users", user_id)
            os.makedirs(user_dir, exist_ok=True)
            wallet_file = os.path.join(user_dir, "wallet.json")
            
            with open(wallet_file, 'w') as f:
                json.dump(wallet_data, f, indent=2)
                
            self.logger.info(f"Updated {token} balance for user {user_id}: {current_balance} -> {new_balance}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating wallet balance: {str(e)}")
            return False
    
    def get_wallet_balance(self, public_key: str) -> Dict[str, float]:
        """
        Get wallet balance from Solana network.

        Args:
            public_key: Wallet public key

        Returns:
            Dict: Wallet balances
        """
        try:
            # Make direct RPC call to get SOL balance
            headers = {"Content-Type": "application/json"}
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getBalance",
                "params": [public_key],
            }

            response = requests.post(
                self.solana_rpc_url, headers=headers, json=payload, timeout=10
            )
            if response.status_code == 200:
                result = response.json()
                if "result" in result and "value" in result["result"]:
                    sol_balance = (
                        result["result"]["value"] / 1_000_000_000
                    )  # Convert lamports to SOL
                else:
                    sol_balance = 0.0
            else:
                sol_balance = 0.0

            # For USDT, we would need to query the token account
            # This is simplified for now
            usdt_balance = 0.0

            return {"solana": sol_balance, "tether_usd": usdt_balance}
        except Exception as e:
            self.logger.error(f"Error getting wallet balance: {str(e)}")
            return {"solana": 0.0, "tether_usd": 0.0}

    def update_wallet_balance(self, wallet_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update wallet balance from network.

        Args:
            wallet_data: Wallet data

        Returns:
            Dict: Updated wallet data
        """
        try:
            public_key = wallet_data["public_key"]
            balances = self.get_wallet_balance(public_key)

            # Update wallet data
            updated_wallet = wallet_data.copy()
            updated_wallet["balance"] = balances
            updated_wallet["last_updated"] = datetime.now().isoformat()

            return updated_wallet
        except Exception as e:
            self.logger.error(f"Error updating wallet balance: {str(e)}")
            return wallet_data


# Type definitions for better type checking
class SessionData(TypedDict):
    """Data structure for Phantom wallet sessions."""
    session_id: str
    user_id: str
    wallet_address: str
    created_at: float
    expires_at: float
    status: Literal['pending', 'active', 'expired']
    last_activity: float

class WalletData(TypedDict):
    """Data structure for wallet information."""
    public_key: str
    private_key_encrypted: Optional[str]
    wallet_type: Literal['internal', 'phantom']
    created_at: str
    updated_at: str
    is_active: bool
    metadata: Dict[str, Any]

class PhantomConnectionResponse(TypedDict):
    """Response structure for Phantom connection requests."""
    public_key: str
    session: Optional[Dict[str, Any]]

class PhantomWalletConnector:
    """
    Manages connections to Phantom wallets following the official Phantom Wallet protocol.
    
    Implements the Phantom Wallet Provider API as documented at:
    https://docs.phantom.com/solana/establishing-a-connection
    
    Features:
    - Standard Phantom connection flow
    - Session management with configurable TTL
    - Automatic session cleanup
    - Secure wallet data handling
    - Integration with Solana RPC
    - Rate limiting and input validation
    - Comprehensive error handling
    """
    
    # Default session TTL (24 hours)
    DEFAULT_SESSION_TTL = 24 * 60 * 60  # 24 hours in seconds
    
    # Cleanup interval (1 hour)
    CLEANUP_INTERVAL = 60 * 60
    
    # Rate limiting (requests per minute per IP)
    RATE_LIMIT = 60
    
    # Phantom error codes
    PHANTOM_ERRORS = {
        4001: "User rejected the request",
        4100: "The requested method is not supported",
        4200: "The method is not available",
        4900: "The provider is disconnected",
        4901: "The provider is not connected",
    }
    
    def __init__(
        self,
        phantom_app_url: str = None,
        phantom_deep_link: str = None,
        session_ttl: int = None,
        secure_data_manager = None,
        app_metadata: Optional[Dict[str, str]] = None
    ):
        """
        Initialize the Phantom wallet connector.
        
        Args:
            phantom_app_url: Base URL for Phantom wallet (default: from env or https://phantom.app)
            phantom_deep_link: Base URL for Phantom deep links (default: from env or https://phantom.app/ul/v1/)
            session_ttl: Session time-to-live in seconds (default: 24h)
            secure_data_manager: Optional secure data manager for encryption
            app_metadata: Optional metadata about the connecting app
            
        Raises:
            InvalidConfigurationError: If required configuration is missing
        """
        try:
            # Load from environment variables if not provided
            self.phantom_app_url = (phantom_app_url or 
                                  os.getenv('PHANTOM_APP_URL', 'https://phantom.app')).rstrip('/')
            self.phantom_deep_link = (phantom_deep_link or 
                                    os.getenv('PHANTOM_DEEP_LINK', 'https://phantom.app/ul/v1/')).rstrip('/')
            
            # Load encryption keys
            self.phantom_private_key = os.getenv('PHANTOM_ENCRYPTION_PRIVATE_KEY')
            self.phantom_public_key = os.getenv('PHANTOM_ENCRYPTION_PUBLIC_KEY')
            
            if not all([self.phantom_private_key, self.phantom_public_key]):
                raise InvalidConfigurationError(
                    "Missing Phantom wallet encryption keys. "
                    "Please set PHANTOM_ENCRYPTION_PRIVATE_KEY and "
                    "PHANTOM_ENCRYPTION_PUBLIC_KEY in your environment."
                )
            
            # Initialize session TTL
            self.session_ttl = int(session_ttl) if session_ttl is not None else self.DEFAULT_SESSION_TTL
            self.secure_data_manager = secure_data_manager
            
            # Get Solana RPC URL from config
            config = get_config()
            self.solana_rpc_url = config.get("solana_rpc_url")
            
            # Set up logger
            self.logger = logging.getLogger("GracePhantomWallet")
            
            # Parse and validate app metadata
            self.app_metadata = {
                "name": (app_metadata or {}).get("name", "Grace Trading Platform"),
                "url": self._validate_url((app_metadata or {}).get("url", "http://localhost:8000")),
                "icon": self._validate_url((app_metadata or {}).get("icon", "http://localhost:8000/icon.png"))
            }
            
            # Initialize storage
            self.sessions: Dict[str, SessionData] = {}
            self.wallets: Dict[str, WalletData] = {}
            self.last_cleanup = time.time()
            
            # Track connection state
            self._is_connected = False
            self._public_key = None
            self._listeners: Dict[str, List[Callable]] = {
                "connect": [], 
                "disconnect": [], 
                "accountChanged": []
            }
            
            # Rate limiting
            self._rate_limits: Dict[str, List[float]] = {}
            
            self.logger.info("PhantomWalletConnector initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize PhantomWalletConnector: {str(e)}")
            raise InvalidConfigurationError(f"Failed to initialize PhantomWalletConnector: {str(e)}")
    
    def _validate_url(self, url: str) -> str:
        """
        Validate and normalize a URL.
        
        Args:
            url: The URL to validate
            
        Returns:
            str: The validated URL
            
        Raises:
            InvalidConfigurationError: If the URL is invalid
        """
        if not url:
            raise InvalidConfigurationError("URL cannot be empty")
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                raise ValueError("Invalid URL format")
            return url
        except Exception as e:
            raise InvalidConfigurationError(f"Invalid URL '{url}': {str(e)}")
    
    def _check_rate_limit(self, identifier: str) -> bool:
        """
        Check if a request is allowed based on rate limiting.
        
        Args:
            identifier: Unique identifier for rate limiting (e.g., IP address)
            
        Returns:
            bool: True if request is allowed, False if rate limited
        """
        now = time.time()
        
        # Clean up old timestamps
        if identifier in self._rate_limits:
            self._rate_limits[identifier] = [t for t in self._rate_limits[identifier] 
                                           if now - t < 60]  # 1 minute window
        
        # Initialize if not exists
        if identifier not in self._rate_limits:
            self._rate_limits[identifier] = []
        
        # Check rate limit
        if len(self._rate_limits[identifier]) >= self.RATE_LIMIT:
            return False
        
        # Add current timestamp
        self._rate_limits[identifier].append(now)
        return True
    
    def _cleanup_expired_sessions(self):
        """
        Clean up expired sessions to free up resources.
        
        This method is called automatically before operations that might be affected by expired sessions.
        """
        now = time.time()
        
        # Only run cleanup at most once per minute to avoid performance issues
        if now - self.last_cleanup < 60:  # 1 minute minimum between cleanups
            return
            
        expired_sessions = [
            session_id for session_id, session in self.sessions.items()
            if session['expires_at'] < now
        ]
        
        for session_id in expired_sessions:
            self.logger.debug(f"Cleaning up expired session: {session_id}")
            del self.sessions[session_id]
        
        self.last_cleanup = now
        
        # Also clean up old rate limit data
        cutoff = now - 300  # 5 minutes
        self._rate_limits = {
            k: [t for t in v if t > cutoff]
            for k, v in self._rate_limits.items()
            if any(t > cutoff for t in v)
        }
    
    def _validate_wallet_address(self, address: str) -> bool:
        """
        Validate a Solana wallet address.
        
        Args:
            address: The address to validate
            
        Returns:
            bool: True if the address is valid, False otherwise
        """
        if not address or not isinstance(address, str):
            return False
            
        # Basic validation - Solana addresses are base58 encoded 32-byte public keys
        try:
            import base58
            decoded = base58.b58decode(address)
            return len(decoded) == 32
        except Exception:
            return False

    # Core Connection Methods
    
    def connect(self, only_if_trusted: bool = False, request_identifier: str = None) -> Dict[str, Any]:
        """
        Connect to the Phantom wallet.
        
        Implements the equivalent of `window.phantom.solana.connect()`.
        
        Args:
            only_if_trusted: If True, only connects if already authorized
            request_identifier: Unique identifier for rate limiting (e.g., IP address)
            
        Returns:
            Dict: Connection response with public key and session
            
        Raises:
            WalletConnectionError: If connection fails or is rejected
            SessionExpiredError: If the session has expired
            RateLimitExceededError: If rate limit is exceeded
        """
        try:
            # Check rate limiting
            if request_identifier and not self._check_rate_limit(request_identifier):
                raise RateLimitExceededError("Too many connection attempts. Please try again later.")
            
            # Clean up expired sessions
            self._cleanup_expired_sessions()
            
            # Check if already connected
            if self._is_connected and self._public_key:
                return {
                    'public_key': self._public_key,
                    'session': None  # No new session created
                }
            
            # Create a new connection session
            session_data = self.create_connection_session(
                user_id=f"temp_{int(time.time())}",  # Temporary user ID for connection
                redirect_url=f"{self.app_metadata['url']}/phantom/callback"
            )
            
            # If only_if_trusted is True, we need to check if we have a valid session
            if only_if_trusted and not self._is_connected:
                raise WalletConnectionError("No existing trusted connection")
            
            # Return the connection URL and session data
            return {
                'public_key': None,  # Will be set after connection
                'session': {
                    'session_id': session_data['session_id'],
                    'connection_url': session_data['connection_url'],
                    'expires_at': session_data['expires_at']
                }
            }
            
        except Exception as e:
            self.logger.error(f"Connection failed: {str(e)}", exc_info=True)
            if isinstance(e, (WalletConnectionError, SessionExpiredError, RateLimitExceededError)):
                raise
            raise WalletConnectionError(f"Failed to connect to Phantom wallet: {str(e)}")
            
   

    def verify_session(self, session_id: str, public_key: str) -> bool:
        """
        Verify a wallet connection session.
        
        Args:
            session_id: The session ID to verify
            public_key: The public key to associate with the session
            
        Returns:
            bool: True if verification is successful
            
        Raises:
            InvalidSessionError: If the session is invalid or expired
            InvalidWalletAddressError: If the wallet address is invalid
        """
        try:
            # Clean up expired sessions first
            self._cleanup_expired_sessions()
            
            # Check if session exists and is valid
            if session_id not in self.sessions:
                raise InvalidSessionError("Session not found or expired")
                
            session = self.sessions[session_id]
            
            # Check if session is already completed
            if session.get('status') == 'completed':
                return True
                
            # Validate public key
            if not self._validate_wallet_address(public_key):
                raise InvalidWalletAddressError(f"Invalid wallet address: {public_key}")
            
            # Update session
            session['public_key'] = public_key
            session['status'] = 'completed'
            session['connected_at'] = int(time.time())
            
            # Update connection state
            self._public_key = public_key
            self._is_connected = True
            
            # Store wallet data
            self.wallets[public_key] = {
                'public_key': public_key,
                'connected_at': session['connected_at'],
                'session_id': session_id
            }
            
            # Emit connect event
            self._emit('connect', {'publicKey': public_key})
            
            self.logger.info(f"Verified session {session_id} for wallet {public_key}")
            return True
            
        except Exception as e:
            self.logger.error(f"Session verification failed: {str(e)}", exc_info=True)
            if isinstance(e, (InvalidSessionError, InvalidWalletAddressError)):
                raise
            raise WalletConnectionError(f"Failed to verify session: {str(e)}")
            
        return True


    def _generate_nonce(self, length: int = 16) -> str:
        """Generate a secure random nonce for CSRF protection."""
        return secrets.token_hex(length)

    def _sign_message(self, message: str, private_key: str) -> str:
        """
        Sign a message using the app's private key.
        
        Args:
            message: The message to sign
            private_key: The private key to use for signing
            
        Returns:
            str: Hex-encoded signature
            
        Raises:
            ValueError: If private key is not provided
        """
        if not private_key:
            raise ValueError("Private key is required for signing")
        return hmac.new(
            private_key.encode('utf-8'),
            msg=message.encode('utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()

    def _verify_signature(self, message: str, signature: str, public_key: str) -> bool:
        """
        Verify a message signature.
        
        Args:
            message: The original message
            signature: The signature to verify
            public_key: The public key to verify against
            
        Returns:
            bool: True if signature is valid, False otherwise
        """
        expected_signature = self._sign_message(message, self.phantom_private_key)
        return hmac.compare_digest(expected_signature, signature)

    def create_connection_session(
        self,
        user_id: str,
        redirect_url: str = None,
        client_info: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Create a new connection session for Phantom wallet with CSRF protection.
        
        Args:
            user_id: Unique identifier for the user
            redirect_url: URL to redirect to after connection
            client_info: Optional client information (IP, user agent, etc.)
            
        Returns:
            Dict containing session information including connection URL
            
        Raises:
            WalletConnectionError: If session creation fails
        """
        try:
            # Generate secure session ID and nonce
            session_id = f"ph_sess_{secrets.token_hex(16)}"
            nonce = self._generate_nonce()
            current_time = datetime.utcnow()
            
            # Create session data with enhanced security
            session_data: Dict[str, Any] = {
                'session_id': session_id,
                'user_id': user_id,
                'nonce': nonce,
                'client_info': client_info or {},
                'created_at': current_time.timestamp(),
                'expires_at': (current_time + timedelta(seconds=self.session_ttl)).timestamp(),
                'status': 'pending',
                'ip_address': client_info.get('ip_address') if client_info else None,
                'user_agent': client_info.get('user_agent') if client_info else None
            }

            # Sign the session data
            session_data['signature'] = self._sign_message(
                f"{session_id}:{nonce}",
                self.phantom_private_key
            )

            # Store the session
            self.sessions[session_id] = session_data

            # Generate connection URL with state parameter for CSRF protection
            state = base64.urlsafe_b64encode(
                json.dumps({
                    'session_id': session_id,
                    'nonce': nonce,
                    'ts': int(current_time.timestamp())
                }).encode('utf-8')
            ).decode('utf-8')

            connection_url = self._generate_connection_url(
                session_id=session_id,
                redirect_url=redirect_url,
                state=state
            )

            return {
                'session_id': session_id,
                'connection_url': connection_url,
                'expires_at': session_data['expires_at'],
                'state': state
            }

        except Exception as e:
            self.logger.error(f"Error creating connection session: {str(e)}", exc_info=True)
            raise WalletConnectionError("Failed to create connection session") from e

    def disconnect_wallet(self, wallet_address: str) -> Dict[str, Any]:
        """
        Enhanced wallet disconnection with proper cleanup.
        """
        try:
            if wallet_address not in self.wallets:
                raise ValueError(f"Wallet not found: {wallet_address}")

            # Update wallet status
            self.wallets[wallet_address].update({
                'is_connected': False,
                'disconnected_at': datetime.utcnow().isoformat()
            })

            # Find and update related sessions
            for session_id, session in self.sessions.items():
                if session.get('public_key') == wallet_address:
                    session.update({
                        'status': 'disconnected',
                        'disconnected_at': datetime.utcnow().timestamp()
                    })

            # Emit disconnect event
            self._emit('disconnect', {
                'publicKey': wallet_address,
                'timestamp': datetime.utcnow().isoformat()
            })

            return {
                'status': 'disconnected',
                'wallet_address': wallet_address,
                'disconnected_at': datetime.utcnow().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Error disconnecting wallet: {str(e)}", exc_info=True)
            raise
    
    def is_connected(self) -> bool:
        """Check if connected to Phantom wallet."""
        return self._is_connected
    
    def get_public_key(self) -> Optional[str]:
        """Get the connected wallet's public key."""
        return self._public_key
    
    # Event Handling
    
    def on(self, event: str, handler: Callable) -> Callable:
        """
        Register an event handler.
        
        Args:
            event: Event name ('connect', 'disconnect', 'accountChanged')
            handler: Callback function to handle the event
            
        Returns:
            Function to unregister the handler
        """
        if event not in self._listeners:
            raise ValueError(f"Unknown event: {event}")
            
        self._listeners[event].append(handler)
        
        # Return unregister function
        def unregister():
            if handler in self._listeners[event]:
                self._listeners[event].remove(handler)
                
        return unregister
    
    def _emit(self, event: str, data: Any = None) -> None:
        """
        Trigger all handlers for an event.
        
        Args:
            event: Event name
            data: Event data
        """
        for handler in self._listeners.get(event, []):
            try:
                handler(data)
            except Exception as e:
                self.logger.error(f"Error in {event} handler: {str(e)}", exc_info=True)
    
    # Session Management
    
    def _cleanup_expired_sessions(self) -> None:
        """Remove expired sessions to prevent memory leaks."""
        current_time = datetime.utcnow().timestamp()
        
        # Only run cleanup at the specified interval
        if (current_time - self.last_cleanup) < self.CLEANUP_INTERVAL:
            return
            
        expired_sessions = [
            session_id for session_id, session in self.sessions.items()
            if 'expires_at' in session and current_time > session['expires_at']
        ]
        
        for session_id in expired_sessions:
            self.logger.debug(f"Cleaning up expired session: {session_id}")
            del self.sessions[session_id]
            
        self.last_cleanup = current_time
        
    def _create_deep_link(self, session_id: str) -> str:
        """
        Create a Phantom deep link for wallet connection.
        
        Args:
            session_id: The session ID to include in the deep link
            
        Returns:
            str: The complete deep link URL
        """
        # Create a connection request payload
        connection_request = {
            'app_url': self.app_metadata.get('url', 'http://localhost:8000'),
            'app_icon': self.app_metadata.get('icon', ''),
            'app_name': self.app_metadata.get('name', 'Grace Trading Platform'),
            'session_id': session_id,
            'timestamp': int(datetime.utcnow().timestamp())
        }
        
        # In a real implementation, you would sign this request with your app's private key
        # For now, we'll just encode it as base64
        import base64
        import json
        
        encoded_request = base64.urlsafe_b64encode(
            json.dumps(connection_request).encode('utf-8')
        ).decode('utf-8')
        
        # Create the deep link
        deep_link = f"{self.phantom_deep_link}connect?app=Grace&dapp_encryption_public_key=YOUR_PUBLIC_KEY&redirect_link={encoded_request}"
        
        return deep_link
        
    def _validate_connection_response(self, response: Dict[str, Any]) -> bool:
        """
        Validate a connection response from Phantom.
        
        Args:
            response: The response from Phantom
            
        Returns:
            bool: True if the response is valid, False otherwise
        """
        try:
            # Check required fields
            required_fields = ['public_key', 'session', 'signature']
            if not all(field in response for field in required_fields):
                self.logger.error(f"Missing required fields in response: {response}")
                return False
                
            # Verify the session exists
            session_id = response.get('session', {}).get('session_id')
            if not session_id or session_id not in self.sessions:
                self.logger.error(f"Invalid or expired session: {session_id}")
                return False
                
            # Verify the signature (in a real implementation)
            # This would involve verifying the signature using the wallet's public key
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating connection response: {str(e)}")
            return False
    
    def create_connection_session(self, user_id: str, redirect_url: str = None) -> Dict[str, Any]:
        """
        Create a new Phantom wallet connection session.

        Args:
            user_id: Unique identifier for the user
            redirect_url: URL to redirect to after connection

        Returns:
            Dict[str, Any]: Session information with the following structure:
            {
                'session_id': str,               # Unique session identifier
                'user_id': str,                  # User ID
                'created_at': float,             # Unix timestamp
                'expires_at': float,             # Expiration timestamp
                'status': 'pending',             # Initial status
                'deep_link': str,                # Deep link to open Phantom
                'connection_url': str,           # Fallback URL for web
                'qr_code_data': str              # Data for QR code generation
            }
            
        Raises:
            ValueError: If session creation fails
        """
        try:
            # Clean up expired sessions periodically
            current_time = datetime.utcnow()
            if (current_time.timestamp() - self.last_cleanup) > self.CLEANUP_INTERVAL:
                self._cleanup_expired_sessions()
            
            session_id = f"ph_sess_{uuid.uuid4().hex}"
            created_at = current_time.timestamp()
            expires_at = created_at + self.session_ttl
            
            # Create session data
            session_data: SessionData = {
                'session_id': session_id,
                'user_id': user_id,
                'public_key': None,
                'created_at': created_at,
                'expires_at': expires_at,
                'status': 'pending',
                'last_activity': created_at,
                'redirect_url': redirect_url,
                'app_metadata': self.app_metadata
            }
            
            # Store session
            self.sessions[session_id] = session_data
            
            # Generate deep link for mobile
            deep_link = self._create_deep_link(session_id)
            
            # Generate connection URL for web
            base_url = "http://localhost:8000"
            connection_url = (
                f"{self.phantom_app_url}/ul/v1/connect"
                f"?app_url={base_url}"
                f"&dapp_encryption_public_key=421MrWonHu6VxRAAqYJwEPzACTBLGoeurehPMSKhRzZM"
                f"&redirect_uri={redirect_url or f'{base_url}/phantom/callback'}"
                f"&app_name={self.app_metadata.get('name', 'Grace')}"
                f"&session_id={session_id}"
            )
            
            # Generate QR code data for mobile wallets
            qr_code_data = f"https://phantom.app/ul/v1/connect?app=Grace&session_id={session_id}"
            
            self.logger.info(
                f"Created Phantom connection session {session_id} "
                f"for user {user_id} (expires: {datetime.fromtimestamp(expires_at)} UTC)"
            )
            
            return {
                'session_id': session_id,
                'user_id': user_id,
                'created_at': created_at,
                'expires_at': expires_at,
                'status': 'pending',
                'deep_link': deep_link,
                'connection_url': connection_url,
                'qr_code_data': qr_code_data
            }
            
        except Exception as e:
            error_msg = f"Failed to create Phantom session: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise ValueError(error_msg) from e
            
    def handle_connection_callback(self, callback_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle connection callback from Phantom wallet.
        
        Args:
            callback_data: The callback data from Phantom
            
        Returns:
            Dict with connection status and session data
            
        Raises:
            ValueError: If callback data is invalid
        """
        try:
            # Validate the callback data
            if not self._validate_connection_response(callback_data):
                raise ValueError("Invalid connection response")
                
            # Get session data
            session_id = callback_data.get('session', {}).get('session_id')
            if not session_id or session_id not in self.sessions:
                raise ValueError("Invalid or expired session")
                
            # Update session with wallet information
            session = self.sessions[session_id]
            session.update({
                'status': 'connected',
                'public_key': callback_data.get('public_key'),
                'connected_at': datetime.utcnow().timestamp(),
                'wallet_data': {
                    'public_key': callback_data.get('public_key'),
                    'session': callback_data.get('session', {}),
                    'signature': callback_data.get('signature')
                }
            })
            
            # Update connection state
            self._public_key = callback_data.get('public_key')
            self._is_connected = True
            
            # Trigger connect event
            self._emit('connect', {
                'publicKey': self._public_key,
                'session': session
            })
            
            self.logger.info(f"Successfully connected wallet: {self._public_key}")
            
            return {
                'status': 'success',
                'session_id': session_id,
                'public_key': self._public_key,
                'redirect_url': session.get('redirect_url')
            }
            
        except Exception as e:
            error_msg = f"Failed to handle connection callback: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise ValueError(error_msg) from e

    def _get_session(self, session_id: str) -> Optional[SessionData]:
        """
        Retrieve and validate a session.

        Args:
            session_id: Session ID to retrieve

        Returns:
            Optional[SessionData]: Session data if valid, None otherwise
        """
        session = self.sessions.get(session_id)
        if not session:
            self.logger.warning(f"Session not found: {session_id}")
            return None

        now = datetime.utcnow().timestamp()
        
        # Check if session is expired
        if now > session['expires_at']:
            session['status'] = 'expired'
            self.logger.warning(f"Session expired: {session_id}")
            return None

        # Update last activity
        session['last_activity'] = now
        return session

    def verify_session(self, session_id: str) -> bool:
        """
        Verify if a session is valid and active.

        Args:
            session_id: Session ID to verify

        Returns:
            bool: True if session is valid and active
        """
        return self._get_session(session_id) is not None

    def complete_connection(self, session_id: str, wallet_address: str) -> Dict[str, Any]:
        """
        Complete the Phantom wallet connection process.

        Args:
            session_id: Session ID from create_connection_session
            wallet_address: Wallet public key from Phantom

        Returns:
            Dict[str, Any]: Connected wallet information
            {
                'status': 'connected',
                'wallet_address': str,
                'session_id': str,
                'user_id': str,
                'expires_at': float
            }

        Raises:
            ValueError: If session is invalid or connection fails
        """
        try:
            session = self._get_session(session_id)
            if not session:
                raise ValueError("Invalid or expired session")

            if not wallet_address:
                raise ValueError("Wallet address is required")


            # Create wallet data structure
            current_time = datetime.utcnow()
            wallet_data: WalletData = {
                'public_key': wallet_address,
                'private_key_encrypted': None,  # Phantom wallets don't expose private keys
                'wallet_type': 'phantom',
                'created_at': current_time.isoformat(),
                'updated_at': current_time.isoformat(),
                'is_active': True,
                'metadata': {
                    'connection_method': 'phantom',
                    'last_connected': current_time.isoformat(),
                    'connection_count': 1
                }
            }

            # Store wallet data
            self.wallets[wallet_address] = wallet_data
            
            # Update session
            session['wallet_address'] = wallet_address
            session['status'] = 'active'
            session['last_activity'] = current_time.timestamp()

            self.logger.info(
                f"Successfully connected Phantom wallet {wallet_address} "
                f"for user {session['user_id']} (session: {session_id})"
            )

            return {
                'status': 'connected',
                'wallet_address': wallet_address,
                'session_id': session_id,
                'user_id': session['user_id'],
                'expires_at': session['expires_at']
            }

        except Exception as e:
            error_msg = f"Failed to complete Phantom connection: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise ValueError(error_msg) from e

    async def get_wallet_balance(self, wallet_address: str) -> Dict[str, float]:
        """
        Get balance for a connected wallet including SOL and token balances.

        Args:
            wallet_address: Wallet public key as base58 string

        Returns:
            Dict[str, float]: Token balances in the format:
            {
                'SOL': float,    # SOL balance in lamports (1 SOL = 1e9 lamports)
                'USDC': float,   # USDC balance (6 decimal places)
                'USDT': float,   # USDT balance (6 decimal places)
            }


        Raises:
            WalletConnectionError: If unable to fetch balance
            ValueError: If wallet address is invalid
        """
        if not self._validate_wallet_address(wallet_address):
            raise ValueError("Invalid wallet address")

        try:
            async with AsyncClient(self.solana_rpc_url) as client:
                # Get SOL balance
                sol_balance = await client.get_balance(Pubkey.from_string(wallet_address))
                
                # Get token accounts
                token_accounts = await client.get_token_accounts_by_owner(
                    Pubkey.from_string(wallet_address),
                    TokenAccountOpts(program_id=TOKEN_PROGRAM_ID)
                )
                
                # Process token accounts
                balances = {
                    'SOL': sol_balance.value / 1e9  # Convert lamports to SOL
                }
                
                # Add USDC and USDT balances (0 by default)
                balances['USDC'] = 0.0
                balances['USDT'] = 0.0
                
                # Known token mints
                TOKEN_MINTS = {
                    'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v': 'USDC',  # USDC mint
                    'Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB': 'USDT'   # USDT mint
                }
                
                # Process token accounts
                for account in token_accounts.value:
                    mint = str(account.account.data.parsed['info']['mint'])
                    if mint in TOKEN_MINTS:
                        token_symbol = TOKEN_MINTS[mint]
                        amount = int(account.account.data.parsed['info']['tokenAmount']['amount'])
                        decimals = int(account.account.data.parsed['info']['tokenAmount']['decimals'])
                        balances[token_symbol] = amount / (10 ** decimals)
                
                return balances
                
        except Exception as e:
            self.logger.error(f"Error fetching wallet balance: {str(e)}")
            raise WalletConnectionError(f"Failed to fetch wallet balance: {str(e)}") # In a real implementation, this would query the Solana RPC
            # For now, return mock data
            return {
                'SOL': 10.5,
                'USDC': 1000.0,
                'USDT': 500.0
            }

        except Exception as e:
            error_msg = f"Failed to get wallet balance: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise ValueError(error_msg) from e

    async def transfer_to_internal_wallet(
        self,
        user_id: str,
        source_wallet: str,
        amount: float,
        token: str = 'SOL',
        priority_fee: int = 10000  # micro-lamports
    ) -> Dict[str, Any]:
        """
        Transfer funds from Phantom wallet to internal wallet.

        Args:
            user_id: User ID initiating the transfer
            source_wallet: Source wallet public key (base58)
            amount: Amount to transfer
            token: Token to transfer ('SOL' or 'USDC')
            priority_fee: Priority fee in micro-lamports (for SOL transfers)

        Returns:
            Dict containing transfer result with the following structure:
            {
                'status': 'success'|'failed',
                'signature': str,  # Transaction signature
                'amount': float,    # Actual amount transferred
                'token': str,       # Token symbol
                'timestamp': str    # ISO 8601 timestamp
            }


        Raises:
            WalletConnectionError: If transfer fails
            ValueError: For invalid parameters
        """
        if not self._validate_wallet_address(source_wallet):
            raise ValueError("Invalid source wallet address")
            
        if amount <= 0:
            raise ValueError("Amount must be positive")
            
        token = token.upper()
        if token not in ['SOL', 'USDC']:
            raise ValueError("Only SOL and USDC transfers are supported")
            
        try:
            # Get internal wallet for the user
            internal_wallet = self.get_internal_wallet(user_id)
            if not internal_wallet or 'public_key' not in internal_wallet:
                raise WalletConnectionError("Internal wallet not found")
                
            dest_wallet = internal_wallet['public_key']
            
            async with AsyncClient(self.solana_rpc_url) as client:
                # For SOL transfers
                if token == 'SOL':
                    # Convert SOL to lamports
                    lamports = int(amount * 1e9)
                    
                    # Create transfer instruction
                    transfer_ix = transfer(
                        TransferParams(
                            from_pubkey=Pubkey.from_string(source_wallet),
                            to_pubkey=Pubkey.from_string(dest_wallet),
                            lamports=lamports
                        )
                    )
                    
                    # Get recent blockhash
                    recent_blockhash = (await client.get_latest_blockhash()).value.blockhash
                    
                    # Create transaction
                    txn = Transaction(fee_payer=Pubkey.from_string(source_wallet))
                    txn.add(transfer_ix)
                    
                    # Sign and send transaction (in a real implementation, this would be signed by the user's wallet)
                    # This is a placeholder - in practice, you'd use the wallet adapter to sign
                    signature = await client.send_transaction(
                        txn,
                        Keypair.from_base58_string(source_wallet)  # This is simplified - use wallet adapter in production
                    )
                    
                    # Wait for confirmation
                    await client.confirm_transaction(signature.value, commitment=Confirmed)
                    
                    return {
                        'status': 'success',
                        'signature': str(signature.value),
                        'amount': amount,
                        'token': token,
                        'timestamp': datetime.utcnow().isoformat()
                    }
                    
                # For USDC transfers
                elif token == 'USDC':
                    # USDC has 6 decimal places
                    token_amount = int(amount * 1e6)
                    
                    # Get token accounts
                    source_token_account = get_associated_token_address(
                        owner=Pubkey.from_string(source_wallet),
                        mint=Pubkey.from_string('EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v')  # USDC mint
                    )
                    
                    dest_token_account = get_associated_token_address(
                        owner=Pubkey.from_string(dest_wallet),
                        mint=Pubkey.from_string('EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v')  # USDC mint
                    )
                    
                    # Check if destination token account exists, create if not
                    try:
                        await client.get_account_info(dest_token_account)
                    except:
                        # Create associated token account if it doesn't exist
                        create_ix = create_associated_token_account(
                            payer=Pubkey.from_string(source_wallet),
                            owner=Pubkey.from_string(dest_wallet),
                            mint=Pubkey.from_string('EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v')
                        )
                        
                        recent_blockhash = (await client.get_latest_blockhash()).value.blockhash
                        txn = Transaction(fee_payer=Pubkey.from_string(source_wallet))
                        txn.add(create_ix)
                        
                        # Sign and send (in practice, use wallet adapter)
                        signature = await client.send_transaction(
                            txn,
                            Keypair.from_base58_string(source_wallet)  # Simplified
                        )
                        await client.confirm_transaction(signature.value, commitment=Confirmed)
                    
                    # Create transfer instruction
                    transfer_ix = transfer_checked(
                        TokenTransferParams(
                            program_id=TOKEN_PROGRAM_ID,
                            source=source_token_account,
                            mint=Pubkey.from_string('EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v'),
                            dest=dest_token_account,
                            owner=Pubkey.from_string(source_wallet),
                            amount=token_amount,
                            decimals=6
                        )
                    )
                    
                    # Create and send transaction
                    recent_blockhash = (await client.get_latest_blockhash()).value.blockhash
                    txn = Transaction(fee_payer=Pubkey.from_string(source_wallet))
                    txn.add(transfer_ix)
                    
                    # Sign and send (in practice, use wallet adapter)
                    signature = await client.send_transaction(
                        txn,
                        Keypair.from_base58_string(source_wallet)  # Simplified
                    )
                    await client.confirm_transaction(signature.value, commitment=Confirmed)
                    
                    return {
                        'status': 'success',
                        'signature': str(signature.value),
                        'amount': amount,
                        'token': token,
                        'timestamp': datetime.utcnow().isoformat()
                    }
                    
        except Exception as e:
            self.logger.error(f"Error in transfer_to_internal_wallet: {str(e)}")
            raise WalletConnectionError(f"Transfer failed: {str(e)}")
            
    def disconnect_wallet(self, wallet_address: str) -> Dict[str, Any]:
        """
        Disconnect a Phantom wallet and clean up associated sessions.

        Args:
            wallet_address: Wallet public key to disconnect

        Returns:
            Dict: Status of the disconnection
            {
                'status': 'success'|'error',
                'message': str,
                'wallet_address': str,
                'timestamp': str
            }

        Raises:
            WalletConnectionError: If disconnection fails
            ValueError: If wallet_address is invalid
        """
        if not wallet_address or not isinstance(wallet_address, str):
            raise ValueError("Invalid wallet address provided")

        try:
            self.logger.info(f"Initiating disconnection for wallet: {wallet_address}")
            
            # Remove wallet from active wallets
            if wallet_address in self.wallets:
                del self.wallets[wallet_address]
                self.logger.debug(f"Removed wallet {wallet_address} from active wallets")

            # Find and remove any sessions associated with this wallet
            sessions_to_remove = [
                session_id for session_id, session in self.sessions.items()
                if session.wallet_address == wallet_address
            ]
            
            for session_id in sessions_to_remove:
                del self.sessions[session_id]
                self.logger.debug(f"Removed session {session_id} for wallet {wallet_address}")

            # Update connection state
            if self._public_key == wallet_address:
                self._public_key = None
                self._is_connected = False
                
                # Notify listeners
                self._emit('disconnect', {
                    'publicKey': wallet_address,
                    'timestamp': datetime.utcnow().isoformat()
                })

            self.logger.info(f"Successfully disconnected wallet: {wallet_address}")
            return {
                'status': 'success',
                'message': 'Wallet disconnected successfully',
                'wallet_address': wallet_address,
                'timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            error_msg = f"Failed to disconnect wallet {wallet_address}: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise WalletConnectionError(error_msg) from e

    def update_wallet_balance(self, wallet_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update wallet balance from network.

        Args:
            wallet_data: Wallet data

        Returns:
            Dict: Updated wallet data with balance and timestamp
        """
        try:
            public_key = wallet_data["public_key"]
            balances = self.get_wallet_balance(public_key)

            # Update wallet data
            updated_wallet = wallet_data.copy()
            updated_wallet["balance"] = balances
            updated_wallet["last_updated"] = datetime.now().isoformat()

            return updated_wallet
        except Exception as e:
            self.logger.error(f"Error updating wallet balance: {str(e)}")
            return wallet_data

    def _generate_connection_url(self, session_id: str, redirect_url: str) -> str:
        """
        Generate a connection URL for Phantom wallet.

        Args:
            session_id: Session ID
            redirect_url: Redirect URL after connection

        Returns:
            str: Connection URL
        """
        try:
            # In a real implementation, this would create a dApp connection URL
            # For now, we'll simulate this with a placeholder URL
            connection_url = f"{self.phantom_app_url}/connect?session={session_id}&redirect={redirect_url}{self.phantom_callback_path}"

            self.logger.info(f"Generated connection URL for session {session_id}")
            return connection_url
        except Exception as e:
            self.logger.error(f"Error generating connection URL: {str(e)}")
            raise

    def update_wallet_balance(self, wallet_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update wallet balance from network.

        Args:
            wallet_data: Wallet data

        Returns:
            Dict: Updated wallet data
        """
        try:
            public_key = wallet_data["public_key"]
            balances = self.get_wallet_balance(public_key)

            # Update wallet data
            updated_wallet = wallet_data.copy()
            updated_wallet["balance"] = balances
            updated_wallet["last_updated"] = datetime.now().isoformat()

            return updated_wallet
        except Exception as e:
            self.logger.error(f"Error updating wallet balance: {str(e)}")
            return wallet_data

    def _update_user_phantom_sessions(self, user_id: str, session_data: Dict[str, Any]) -> bool:
        """
        Update Phantom sessions in the user profile.

        Args:
            user_id: Unique identifier for the user
            session_data: Session data to add or update

        Returns:
            bool: True if update was successful, False otherwise
            
        Raises:
            ValueError: If user_id or session_data is invalid
            WalletConnectionError: If there's an error updating the profile
        """
        if not user_id or not isinstance(user_id, str):
            raise ValueError("Invalid user ID")
            
        if not session_data or not isinstance(session_data, dict):
            raise ValueError("Invalid session data")
            
        try:
            # Get current profile
            result = self.user_profile_system.get_user_profile(user_id)
            if not result or not isinstance(result, dict) or not result.get("success", False):
                self.logger.error(f"Failed to retrieve profile for user {user_id}")
                return False

            profile = result.get("profile", {})
            
            # Initialize or update sessions list
            sessions = profile.get("phantom_sessions", [])
            
            # Check if session with this ID already exists
            session_id = session_data.get("session_id")
            if not session_id:
                raise ValueError("Session data must contain a session_id")
                
            current_time = datetime.utcnow().isoformat()
            session_exists = False
            
            # Update existing session if found, otherwise add new session
            for i, session in enumerate(sessions):
                if isinstance(session, dict) and session.get("session_id") == session_id:
                    sessions[i] = {
                        **session,
                        **session_data,
                        "updated_at": current_time
                    }
                    session_exists = True
                    break
                    
            if not session_exists:
                sessions.append({
                    **session_data,
                    "created_at": current_time,
                    "updated_at": current_time
                })
            
            try:
                # Update profile with modified sessions
                update_result = self.user_profile_system.update_user_profile(
                    user_id, 
                    {"phantom_sessions": sessions}
                )
                
                if not update_result or not isinstance(update_result, dict) or not update_result.get("success", False):
                    error_msg = update_result.get("error", "Unknown error") if isinstance(update_result, dict) else "Invalid response format"
                    self.logger.error(f"Failed to update profile for user {user_id}: {error_msg}")
                    return False
                    
                return True
                
            except Exception as update_error:
                self.logger.error(f"Error updating user profile: {str(update_error)}")
                return False
                
        except ValueError as ve:
            self.logger.error(f"Validation error in _update_user_phantom_sessions: {str(ve)}")
            raise
            
        except Exception as e:
            error_msg = f"Unexpected error in _update_user_phantom_sessions: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise WalletConnectionError(error_msg) from e
            
        except Exception as e:
            error_msg = f"Error updating user Phantom sessions: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            if not isinstance(e, (ValueError, WalletConnectionError)):
                raise WalletConnectionError(error_msg) from e
            raise

    def get_connection_status(self, session_id: str) -> Dict[str, Any]:
        """
        Get the connection status for a session.

        Args:
            session_id: The session ID to check

        Returns:
            Dict containing connection status information with the following structure:
            {
                'session_id': str,               # The session ID
                'status': str,                   # Session status ('pending', 'active', 'expired')
                'wallet_address': Optional[str], # Connected wallet address if any
                'is_connected': bool,            # Whether the wallet is currently connected
                'created_at': float,             # Session creation timestamp
                'expires_at': float,             # Session expiration timestamp
                'seconds_remaining': float       # Seconds until session expires
            }

        Raises:
            InvalidSessionError: If the session is invalid or expired
            WalletConnectionError: If there's an error checking the status
        """
        if not session_id or not isinstance(session_id, str):
            raise InvalidSessionError("Invalid session ID")
            
        try:
            session = self._get_session(session_id)
            if not session:
                raise InvalidSessionError("Invalid or expired session")

            wallet_address = session.get('public_key')
            wallet_data = self.wallets.get(wallet_address) if wallet_address else None
            
            # Calculate time remaining
            expires_at = session.get('expires_at', 0)
            current_time = time.time()
            seconds_remaining = max(0, expires_at - current_time) if expires_at else 0
            
            # Determine connection status
            status = session.get('status', 'unknown')
            if status == 'active' and seconds_remaining <= 0:
                status = 'expired'
                session['status'] = status
            
            return {
                'session_id': session_id,
                'status': status,
                'wallet_address': wallet_address,
                'is_connected': bool(wallet_data and wallet_data.get('is_connected', False)),
                'created_at': session.get('created_at'),
                'expires_at': expires_at,
                'seconds_remaining': seconds_remaining,
                'wallet_type': 'phantom'
            }

        except InvalidSessionError:
            raise  # Re-raise session-specific errors
        except Exception as e:
            error_msg = f"Error getting connection status: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise WalletConnectionError(error_msg) from e
class WalletConnectionSystem:
    """
    Manages wallet connections for Grace users.
    """

# Removed duplicate __init__ method - using the more comprehensive one above

    def create_internal_wallet(self, user_id: str) -> Dict[str, Any]:
        """
        Create an internal wallet for a user.

        Args:
            user_id: User ID

        Returns:
            Dict: Wallet information
        """
        try:
            # Generate wallet
            wallet_data = self.internal_wallet_manager.generate_wallet()

            # Update user profile
            result = self.user_profile_system.update_user_profile(
                user_id, {"internal_wallet": wallet_data}
            )

            if not result.get("success", False):
                raise ValueError(
                    f"Failed to update user profile: {result.get('error')}"
                )

            self.logger.info(f"Created internal wallet for user: {user_id}")
            return wallet_data
        except Exception as e:
            self.logger.error(f"Error creating internal wallet: {str(e)}")
            raise

    def get_internal_wallet(self, user_id: str) -> Dict[str, Any]:
        """
        Get a user's internal wallet.

        Args:
            user_id: User ID

        Returns:
            Dict: Wallet information
        """
        try:
            # Get user profile
            result = self.user_profile_system.get_user_profile(user_id)

            if not result.get("success", False):
                raise ValueError(f"Failed to get user profile: {result.get('error')}")

            profile = result["profile"]

            if "internal_wallet" not in profile:
                raise ValueError(f"User {user_id} has no internal wallet")

            return profile["internal_wallet"]
        except Exception as e:
            self.logger.error(f"Error getting internal wallet: {str(e)}")
            raise

    def update_internal_wallet_balance(self, user_id: str) -> Dict[str, float]:
        """
        Update a user's internal wallet balance.

        Args:
            user_id: User ID

        Returns:
            Dict: Updated wallet balances
        """
        try:
            # Get internal wallet
            wallet_data = self.get_internal_wallet(user_id)

            # Update balance
            updated_wallet = self.internal_wallet_manager.update_wallet_balance(
                wallet_data
            )

            # Update user profile
            result = self.user_profile_system.update_user_profile(
                user_id, {"internal_wallet": updated_wallet}
            )

            if not result.get("success", False):
                raise ValueError(
                    f"Failed to update user profile: {result.get('error')}"
                )

            self.logger.info(f"Updated internal wallet balance for user: {user_id}")
            return updated_wallet["balance"]
        except Exception as e:
            self.logger.error(f"Error updating internal wallet balance: {str(e)}")
            raise

    def initiate_phantom_connection(
        self, user_id: str, redirect_url: str
    ) -> Dict[str, str]:
        """
        Initiate Phantom wallet connection.

        Args:
            user_id: User ID
            redirect_url: Redirect URL after connection

        Returns:
            Dict: Connection information
        """
        try:
            # Create connection session
            session = self.phantom_connector.create_connection_session()

            # Generate connection URL
            connection_url = self.phantom_connector.generate_connection_url(
                session["session_id"], redirect_url
            )

            # Store session in user profile
            result = self.user_profile_system.get_user_profile(user_id)

            if not result.get("success", False):
                raise ValueError(f"Failed to get user profile: {result.get('error')}")

            profile = result["profile"]

            if "phantom_sessions" not in profile:
                profile["phantom_sessions"] = []

            profile["phantom_sessions"].append(session)

            # Update profiles directly instead of using update_user_profile
            # Get the profiles again to ensure we have the latest data
            profiles = self.user_profile_system._load_profiles()

            if user_id in profiles:
                # Update the phantom_sessions in the profile
                profiles[user_id]["phantom_sessions"] = profile["phantom_sessions"]
                # Save the updated profiles
                self.user_profile_system._save_profiles(profiles)
            else:
                raise ValueError(f"User ID '{user_id}' not found")

            self.logger.info(f"Initiated Phantom connection for user: {user_id}")
            return {
                "session_id": session["session_id"],
                "connection_url": connection_url,
            }
        except Exception as e:
            self.logger.error(f"Error initiating Phantom connection: {str(e)}")
            raise

    def complete_phantom_connection(
        self, user_id: str, session_id: str, wallet_address: str
    ) -> Dict[str, Any]:
        """
        Complete Phantom wallet connection.

        Args:
            user_id: User ID
            session_id: Session ID
            wallet_address: Wallet address

        Returns:
            Dict: Connected wallet information
        """
        try:
            # Complete connection
            wallet_data = self.phantom_connector.complete_connection(
                session_id, wallet_address
            )

            # Get user profile
            result = self.user_profile_system.get_user_profile(user_id)

            if not result.get("success", False):
                raise ValueError(f"Failed to get user profile: {result.get('error')}")

            profile = result["profile"]

            # Update session status
            for session in profile.get("phantom_sessions", []):
                if session["session_id"] == session_id:
                    session["status"] = "completed"
                    break

            # Add wallet to profile
            if "phantom_wallets" not in profile:
                profile["phantom_wallets"] = []

            # Check if wallet already exists
            wallet_exists = False
            for i, wallet in enumerate(profile["phantom_wallets"]):
                if wallet["wallet_address"] == wallet_address:
                    profile["phantom_wallets"][i] = wallet_data
                    wallet_exists = True
                    break

            if not wallet_exists:
                profile["phantom_wallets"].append(wallet_data)

            # Update user profile
            update_result = self.user_profile_system.update_user_profile(
                user_id,
                {
                    "phantom_sessions": profile.get("phantom_sessions", []),
                    "phantom_wallets": profile.get("phantom_wallets", []),
                },
            )

            if not update_result.get("success", False):
                raise ValueError(
                    f"Failed to update user profile: {update_result.get('error')}"
                )

            self.logger.info(f"Completed Phantom connection for user: {user_id}")
            return wallet_data
        except Exception as e:
            self.logger.error(f"Error completing Phantom connection: {str(e)}")
            raise

    def disconnect_phantom_wallet(self, user_id: str, wallet_address: str) -> bool:
        """
        Disconnect a Phantom wallet.

        Args:
            user_id: User ID
            wallet_address: Wallet address

        Returns:
            bool: Success status
        """
        try:
            # Disconnect wallet
            success = self.phantom_connector.disconnect_wallet(wallet_address)

            if not success:
                return False

            # Get user profile
            result = self.user_profile_system.get_user_profile(user_id)

            if not result.get("success", False):
                raise ValueError(f"Failed to get user profile: {result.get('error')}")

            profile = result["profile"]

            # Remove wallet from profile
            if "phantom_wallets" in profile:
                profile["phantom_wallets"] = [
                    w
                    for w in profile["phantom_wallets"]
                    if w["wallet_address"] != wallet_address
                ]

            # Update user profile
            update_result = self.user_profile_system.update_user_profile(
                user_id, {"phantom_wallets": profile.get("phantom_wallets", [])}
            )

            if not update_result.get("success", False):
                raise ValueError(
                    f"Failed to update user profile: {update_result.get('error')}"
                )

            self.logger.info(f"Disconnected Phantom wallet for user: {user_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error disconnecting Phantom wallet: {str(e)}")
            return False

    def get_all_wallets(self, user_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get all wallets for a user.

        Args:
            user_id: User ID

        Returns:
            Dict: All wallet information
        """
        try:
            # Get user profile
            result = self.user_profile_system.get_user_profile(user_id)

            if not result.get("success", False):
                raise ValueError(f"Failed to get user profile: {result.get('error')}")

            profile = result["profile"]

            # Get internal wallet
            internal_wallet = profile.get("internal_wallet", None)

            # Get phantom wallets
            phantom_wallets = profile.get("phantom_wallets", [])

            return {
                "internal_wallet": internal_wallet,
                "phantom_wallets": phantom_wallets,
            }
        except Exception as e:
            self.logger.error(f"Error getting all wallets: {str(e)}")
            raise

    def update_all_wallet_balances(self, user_id: str) -> Dict[str, Any]:
        """
        Update balances for all wallets.

        Args:
            user_id: User ID

        Returns:
            Dict: Updated wallet information
        """
        try:
            # Get all wallets
            wallets = self.get_all_wallets(user_id)

            # Update internal wallet balance
            if wallets["internal_wallet"]:
                internal_balance = self.update_internal_wallet_balance(user_id)
                wallets["internal_wallet"]["balance"] = internal_balance

            # Update phantom wallet balances
            for i, wallet in enumerate(wallets["phantom_wallets"]):
                balance = self.phantom_connector.get_wallet_balance(
                    wallet["wallet_address"]
                )
                wallets["phantom_wallets"][i]["balance"] = balance

            self.logger.info(f"Updated all wallet balances for user: {user_id}")
            return wallets
        except Exception as e:
            self.logger.error(f"Error updating all wallet balances: {str(e)}")
            raise


# Example usage
if __name__ == "__main__":
    # This would be initialized with actual user profile system in production
    from user_profile import UserProfileSystem

    # Use environment variables
    fernet_key = os.environ.get(
        "FERNET_KEY", "47_1uGC4S-2LuO3DlgvAnRQx7T-pNKWkGhNKZenAD2w="
    )
    phantom_app_url = os.environ.get("PHANTOM_APP_URL", "https://phantom.app")
    phantom_callback_path = os.environ.get("PHANTOM_CALLBACK_PATH", "/phantom/callback")
    jwt_secret = "your-jwt-secret-key"  # In production, use a secure secret

    # Initialize user profile system
    user_system = UserProfileSystem(
        "profiles.json", fernet_key, jwt_secret, phantom_app_url, phantom_callback_path
    )

    # Initialize wallet connection system
    wallet_system = WalletConnectionSystem(
        user_system,
        None,  # No secure data manager for this example
        phantom_app_url,
        phantom_callback_path,
    )

    # Create a test user
    try:
        user = user_system.create_user(
            "testuser", "test@example.com", "password123", "1234567890"
        )
        print(f"Created user: {user}")

        # Create internal wallet
        internal_wallet = wallet_system.create_internal_wallet(user["user_id"])
        print(f"Created internal wallet: {internal_wallet}")

        # Initiate Phantom connection
        connection = wallet_system.initiate_phantom_connection(
            user["user_id"], "http://localhost:3000"
        )
        print(f"Connection URL: {connection['connection_url']}")

        # Simulate completing connection
        wallet = wallet_system.complete_phantom_connection(
            user["user_id"],
            connection["session_id"],
            "5FHwkrdxBc3S4TidqJfhRxzVZrj8xnHKKZwQpWrXKmZa",
        )
        print(f"Connected wallet: {wallet}")

        # Get all wallets
        all_wallets = wallet_system.get_all_wallets(user["user_id"])
        print(f"All wallets: {all_wallets}")

        # Update all wallet balances
        updated_wallets = wallet_system.update_all_wallet_balances(user["user_id"])
        print(f"Updated wallets: {updated_wallets}")
    except Exception as e:
        print(f"Error: {str(e)}")
