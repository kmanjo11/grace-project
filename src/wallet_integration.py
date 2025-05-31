"""
Wallet Integration for Grace Project

This module provides integration points for the wallet system with the rest of the application.
It initializes the wallet components and provides access to wallet functionality.
"""

import logging
from typing import Dict, Any, Optional

from src.wallet_provider_factory import WalletProviderFactory
from src.wallet_adapter import WalletAdapter
from src.config import get_config

logger = logging.getLogger("WalletIntegration")

class WalletIntegration:
    """
    Integration class for wallet functionality.
    Provides a single entry point for wallet operations.
    """
    
    _instance = None
    
    @classmethod
    def get_instance(cls, user_profile_system=None, secure_data_manager=None):
        """
        Get singleton instance of WalletIntegration.
        
        Args:
            user_profile_system: User profile system for user data
            secure_data_manager: Secure data manager for encryption
            
        Returns:
            WalletIntegration instance
        """
        if cls._instance is None:
            cls._instance = cls(
                user_profile_system=user_profile_system,
                secure_data_manager=secure_data_manager,
            )
        return cls._instance
    
    def __init__(self, user_profile_system=None, secure_data_manager=None):
        """
        Initialize wallet integration.
        
        Args:
            user_profile_system: User profile system for user data
            secure_data_manager: Secure data manager for encryption
        """
        # If singleton instance already exists, don't reinitialize
        if WalletIntegration._instance is not None:
            return
            
        self.user_profile_system = user_profile_system
        self.secure_data_manager = secure_data_manager
        self.config = get_config()
        
        # Initialize wallet provider factory
        self.wallet_provider_factory = WalletProviderFactory(
            user_profile_system=user_profile_system,
            secure_data_manager=secure_data_manager,
            config=self.config,
        )
        
        # Initialize wallet adapter
        self.wallet_adapter = WalletAdapter(
            wallet_provider_factory=self.wallet_provider_factory,
            user_profile_system=user_profile_system,
        )
        
        # Set this instance as the singleton
        WalletIntegration._instance = self
        
        logger.info("WalletIntegration initialized")
    
    def create_wallet(self, user_id: str) -> Dict[str, Any]:
        """
        Create wallet for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Dict[str, Any]: Wallet information
        """
        return self.wallet_adapter.create_internal_wallet(user_id)
    
    def get_balance(self, user_id: str, wallet_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Get wallet balance for a user.
        
        Args:
            user_id: User ID
            wallet_type: Wallet type (internal, phantom, or None for both)
            
        Returns:
            Dict[str, Any]: Wallet balance
        """
        return self.wallet_adapter.get_wallet_balance(user_id, wallet_type)
    
    def connect_phantom(self, user_id: str, phantom_address: str) -> Dict[str, Any]:
        """
        Connect a Phantom wallet to a user account.
        
        Args:
            user_id: User ID
            phantom_address: Phantom wallet address
            
        Returns:
            Dict[str, Any]: Connection result
        """
        return self.wallet_adapter.connect_phantom_wallet(user_id, phantom_address)
    
    def disconnect_phantom(self, user_id: str) -> Dict[str, Any]:
        """
        Disconnect a Phantom wallet from a user account.
        
        Args:
            user_id: User ID
            
        Returns:
            Dict[str, Any]: Disconnection result
        """
        return self.wallet_adapter.disconnect_phantom_wallet(user_id)
    
    def register_public_key(self, user_id: str, public_key: str) -> Dict[str, Any]:
        """
        Register a client-generated public key.
        Only applicable for non-custodial wallets.
        
        Args:
            user_id: User ID
            public_key: Public key generated client-side
            
        Returns:
            Dict[str, Any]: Registration result
        """
        return self.wallet_adapter.register_public_key(user_id, public_key)
    
    def update_all_balances(self, user_id: str) -> Dict[str, Any]:
        """
        Update balances for all wallets.
        
        Args:
            user_id: User ID
            
        Returns:
            Dict[str, Any]: Updated wallet information
        """
        return self.wallet_adapter.update_all_wallet_balances(user_id)
