"""
Wallet Provider Factory for Grace Project

This module implements a factory pattern to determine whether to use custodial or 
non-custodial wallet implementation based on user attributes.
"""

from typing import Dict, Any, Optional
import logging
from datetime import datetime

from src.solana_wallet import SolanaWalletManager

logger = logging.getLogger("WalletProviderFactory")

class WalletProviderFactory:
    """Factory that provides appropriate wallet implementation based on user attributes."""
    
    def __init__(
        self,
        user_profile_system=None,
        secure_data_manager=None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize with dependencies.
        
        Args:
            user_profile_system: User profile system for user data
            secure_data_manager: Secure data manager for encryption
            config: Additional configuration options
        """
        self.user_profile_system = user_profile_system
        self.secure_data_manager = secure_data_manager
        self.config = config or {}
        
        # Initialize custodial implementation
        self.custodial_manager = SolanaWalletManager(
            user_profile_system=user_profile_system,
            secure_data_manager=secure_data_manager,
            config=config,
        )
        
        # Initialize non-custodial implementation lazily to avoid circular imports
        self.non_custodial_manager = None
        
        logger.info("WalletProviderFactory initialized")
    
    def _get_non_custodial_manager(self):
        """
        Lazily initialize non-custodial manager to avoid circular imports.
        
        Returns:
            NonCustodialWalletManager instance
        """
        if self.non_custodial_manager is None:
            # Import here to avoid circular imports
            from src.non_custodial_wallet import NonCustodialWalletManager
            
            self.non_custodial_manager = NonCustodialWalletManager(
                user_profile_system=self.user_profile_system,
                config=self.config,
            )
            
        return self.non_custodial_manager
    
    def get_wallet_manager(self, user_id: str) -> Any:
        """
        Get appropriate wallet manager based on user attributes.
        
        Args:
            user_id: User ID
            
        Returns:
            Appropriate wallet manager implementation
        """
        # Default to custodial implementation
        if not self.user_profile_system:
            logger.warning("No user profile system available, using custodial implementation")
            return self.custodial_manager
            
        try:
            # Get user profile
            user_profile = self.user_profile_system.get_user_profile(user_id)
            
            # Check if admin user (always custodial)
            if user_profile.get("email") == "kmanjo11@gmail.com":
                logger.info(f"Admin user {user_id} using custodial wallet")
                return self.custodial_manager
                
            # Check if existing user (created before non-custodial implementation)
            # Using a cutoff date for when non-custodial was implemented
            cutoff_date = "2025-05-31T00:00:00"  # Implementation date
            user_created_at = user_profile.get("created_at", "")
            
            if user_created_at < cutoff_date:
                logger.info(f"Existing user {user_id} using custodial wallet")
                return self.custodial_manager
                
            # New user gets non-custodial implementation
            logger.info(f"New user {user_id} using non-custodial wallet")
            return self._get_non_custodial_manager()
            
        except Exception as e:
            logger.error(f"Error determining wallet implementation: {str(e)}")
            # Fall back to custodial implementation for safety
            return self.custodial_manager
