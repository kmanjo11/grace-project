# Create a new file: mango_wallet_integrator.py
import logging
from typing import Dict, Any, Optional
from datetime import datetime

class MangoWalletIntegrator:
    """
    Non-invasive wallet linking mechanism for Mango Markets
    Designed to work seamlessly with existing infrastructure
    """
    
    def __init__(self, 
                 user_profile_system=None, 
                 mango_v3_client=None, 
                 logger=None):
        """
        Initialize with minimal dependencies
        
        Args:
            user_profile_system: Existing user profile management system
            mango_v3_client: Mango V3 client for wallet operations
            logger: Optional logger
        """
        self.user_profile_system = user_profile_system
        self.mango_v3_client = mango_v3_client
        self.logger = logger or logging.getLogger(__name__)
    
    def _is_wallet_linked(self, user_id: str) -> bool:
        """
        Check if wallet is already linked to Mango Markets
        
        Non-intrusive method that doesn't modify existing profile structure
        """
        try:
            user_profile = self.user_profile_system.get_user_profile(user_id)
            return user_profile.get('mango_markets_link', {}).get('status', False)
        except Exception as e:
            self.logger.warning(f"Wallet link check failed: {e}")
            return False
    
    def link_wallet_silently(self, user_id: str) -> Dict[str, Any]:
        """
        Attempt to link wallet without disrupting user flow
        
        Args:
            user_id: User's unique identifier
        
        Returns:
            Linking result dictionary
        """
        try:
            # Retrieve user's internal wallet
            user_profile = self.user_profile_system.get_user_profile(user_id)
            internal_wallet = user_profile.get('internal_wallet', {})
            
            if not internal_wallet:
                return {'success': False, 'message': 'No internal wallet found'}
            
            wallet_address = internal_wallet.get('public_key')
            
            # Attempt wallet linking
            link_result = self.mango_v3_client.link_wallet(
                wallet_address=wallet_address,
                user_id=user_id
            )
            
            # Optional: Update user profile (non-destructive)
            if link_result.get('success'):
                self.user_profile_system.update_user_data(user_id, {
                    'mango_markets_link': {
                        'status': True,
                        'linked_at': datetime.now().isoformat()
                    }
                })
            
            return link_result
        
        except Exception as e:
            self.logger.error(f"Silent wallet linking failed: {e}")
            return {'success': False, 'message': str(e)}
    
    def enhance_trade_execution(self, trade_func):
        """
        Decorator to automatically link wallet before trade execution
        
        Args:
            trade_func: Original trade execution function
        
        Returns:
            Enhanced trade execution function
        """
        def wrapper(*args, **kwargs):
            # Extract user_id from trade arguments
            user_id = kwargs.get('user_id') or (args[0] if args else None)
            
            if user_id and not self._is_wallet_linked(user_id):
                # Attempt silent wallet linking
                self.link_wallet_silently(user_id)
            
            # Execute original trade function
            return trade_func(*args, **kwargs)
        
        return wrapper