"""
Wallet Adapter for Grace Project

This module implements an adapter pattern to provide a consistent interface
for both custodial and non-custodial wallet implementations.
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("WalletAdapter")

class WalletAdapter:
    """
    Adapter that provides a consistent interface for both custodial and non-custodial wallets.
    Ensures compatibility with existing code.
    """
    
    def __init__(self, wallet_provider_factory, user_profile_system=None):
        """
        Initialize with wallet provider factory.
        
        Args:
            wallet_provider_factory: Factory to get appropriate wallet implementation
            user_profile_system: User profile system for user data
        """
        self.wallet_provider_factory = wallet_provider_factory
        self.user_profile_system = user_profile_system
        logger.info("WalletAdapter initialized")
    
    def create_internal_wallet(self, user_id: str) -> Dict[str, Any]:
        """
        Create internal wallet for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Dict[str, Any]: Wallet information
        """
        # Get appropriate wallet manager
        wallet_manager = self.wallet_provider_factory.get_wallet_manager(user_id)
        
        # Delegate to implementation
        return wallet_manager.generate_internal_wallet(user_id)
    
    def get_wallet_balance(self, user_id: str, wallet_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Get wallet balance for a user.
        
        Args:
            user_id: User ID
            wallet_type: Wallet type (internal, phantom, or None for both)
            
        Returns:
            Dict[str, Any]: Wallet balance
        """
        # Get appropriate wallet manager
        wallet_manager = self.wallet_provider_factory.get_wallet_manager(user_id)
        
        # Delegate to implementation
        return wallet_manager.get_wallet_balance(user_id, wallet_type)
    
    def connect_phantom_wallet(self, user_id: str, phantom_address: str) -> Dict[str, Any]:
        """
        Connect a Phantom wallet to a user account.
        
        Args:
            user_id: User ID
            phantom_address: Phantom wallet address
            
        Returns:
            Dict[str, Any]: Connection result
        """
        # Get appropriate wallet manager
        wallet_manager = self.wallet_provider_factory.get_wallet_manager(user_id)
        
        # Delegate to implementation
        return wallet_manager.connect_phantom_wallet(user_id, phantom_address)
    
    def disconnect_phantom_wallet(self, user_id: str) -> Dict[str, Any]:
        """
        Disconnect a Phantom wallet from a user account.
        
        Args:
            user_id: User ID
            
        Returns:
            Dict[str, Any]: Disconnection result
        """
        # Get appropriate wallet manager
        wallet_manager = self.wallet_provider_factory.get_wallet_manager(user_id)
        
        # Delegate to implementation if available
        if hasattr(wallet_manager, 'disconnect_phantom_wallet'):
            return wallet_manager.disconnect_phantom_wallet(user_id)
        else:
            logger.error(f"Wallet manager does not support disconnect_phantom_wallet")
            return {"status": "error", "message": "Operation not supported"}
    
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
        # Get appropriate wallet manager
        wallet_manager = self.wallet_provider_factory.get_wallet_manager(user_id)
        
        # Delegate to implementation if available
        if hasattr(wallet_manager, 'register_public_key'):
            return wallet_manager.register_public_key(user_id, public_key)
        else:
            logger.error(f"Wallet manager does not support register_public_key")
            return {"status": "error", "message": "Operation not supported"}
    
    def update_all_wallet_balances(self, user_id: str) -> Dict[str, Any]:
        """
        Update balances for all wallets.
        
        Args:
            user_id: User ID
            
        Returns:
            Dict[str, Any]: Updated wallet information
        """
        # Get appropriate wallet manager
        wallet_manager = self.wallet_provider_factory.get_wallet_manager(user_id)
        
        # Delegate to implementation if available
        if hasattr(wallet_manager, 'update_all_wallet_balances'):
            return wallet_manager.update_all_wallet_balances(user_id)
        else:
            # Fallback implementation
            try:
                # Get all wallets
                wallets = {}
                
                # Get internal wallet balance
                internal_result = self.get_wallet_balance(user_id, "internal")
                if internal_result.get("status") == "success":
                    wallets["internal_wallet"] = {
                        "public_key": internal_result.get("wallet_address"),
                        "balance": internal_result.get("balance", 0)
                    }
                
                # Get phantom wallet balance
                phantom_result = self.get_wallet_balance(user_id, "phantom")
                if phantom_result.get("status") == "success":
                    wallets["phantom_wallets"] = [{
                        "wallet_address": phantom_result.get("wallet_address"),
                        "balance": phantom_result.get("balance", 0)
                    }]
                
                logger.info(f"Updated all wallet balances for user: {user_id}")
                return wallets
            except Exception as e:
                logger.error(f"Error updating all wallet balances: {str(e)}")
                return {"status": "error", "message": str(e)}
