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
                 wallet_manager=None,
                 logger=None):
        """
        Initialize with minimal dependencies
        
        Args:
            user_profile_system: Existing user profile management system
            mango_v3_client: Mango V3 client for wallet operations
            wallet_manager: Internal wallet management system
            logger: Optional logger
        """
        self.user_profile_system = user_profile_system
        self.mango_v3_client = mango_v3_client
        self.logger = logger or logging.getLogger(__name__)
        
        # Initialize wallet manager if not provided
        if not wallet_manager and user_profile_system:
            try:
                from src.solana_wallet import SolanaWalletManager
                self.wallet_manager = SolanaWalletManager(
                    user_profile_system=user_profile_system,
                    secure_data_manager=user_profile_system.secure_data_manager
                )
                self.logger.info("Initialized SolanaWalletManager")
            except Exception as e:
                self.logger.error(f"Failed to initialize SolanaWalletManager: {e}")
                self.wallet_manager = wallet_manager
        else:
            self.wallet_manager = wallet_manager
    
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
            # First ensure user has an internal wallet
            if not self.wallet_manager:
                return {'success': False, 'message': 'Wallet manager not available'}
                
            # Get or create internal wallet
            wallet_result = self.wallet_manager.generate_internal_wallet(user_id)
            if not wallet_result.get('status') == 'success':
                return {'success': False, 'message': f"Failed to get/create wallet: {wallet_result.get('message')}"}
            
            # Get the clean public key
            public_key = wallet_result['wallet_address']
            if not public_key:
                return {'success': False, 'message': 'Invalid wallet public key'}
                
            # Verify wallet exists in profile
            user_profile = self.user_profile_system.get_user_profile(user_id)
            internal_wallet = user_profile.get('internal_wallet', {})
            if not internal_wallet or internal_wallet.get('public_key') != public_key:
                return {'success': False, 'message': 'Wallet verification failed'}
            
            # Link wallet to Mango
            link_result = self.mango_v3_client.link_wallet(
                wallet_address=public_key,
                user_id=user_id
            )
            
            # Track the link in user profile
            if link_result.get('success'):
                self.user_profile_system.update_user_data(user_id, {
                    'mango_markets_link': {
                        'status': True,
                        'linked_at': datetime.now().isoformat(),
                        'wallet_address': public_key
                    }
                })
            
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
    
    def get_mango_balance(self, user_id: str) -> Dict[str, Any]:
        """
        Get user's balance allocated to Mango V3 trading
        
        Args:
            user_id: User's unique identifier
            
        Returns:
            Balance information dictionary
        """
        try:
            if not self._is_wallet_linked(user_id):
                return {'success': False, 'message': 'Wallet not linked'}
                
            return self.mango_v3_client.get_wallet_balances()
        except Exception as e:
            self.logger.error(f"Failed to get Mango balance: {e}")
            return {'success': False, 'message': str(e)}
    
    def allocate_funds(self, user_id: str, amount: float, asset: str) -> Dict[str, Any]:
        """
        Allocate funds from internal wallet to Mango V3 trading
        
        Args:
            user_id: User's unique identifier
            amount: Amount to allocate
            asset: Asset type (e.g., 'USDC')
            
        Returns:
            Allocation result
        """
        try:
            # Check internal balance first
            internal_balance = self.wallet_manager.get_balance(user_id, asset)
            if not internal_balance['success'] or internal_balance['balance'] < amount:
                return {'success': False, 'message': 'Insufficient internal balance'}
            
            # Transfer to Mango V3
            transfer_result = self.mango_v3_client.deposit_funds(
                user_id=user_id,
                amount=amount,
                asset=asset
            )
            
            if transfer_result['success']:
                # Update internal records
                self.wallet_manager.update_balance(
                    user_id=user_id,
                    asset=asset,
                    amount=-amount,  # Deduct from internal balance
                    memo=f"Allocated to Mango V3 trading"
                )
            
            return transfer_result
            
        except Exception as e:
            self.logger.error(f"Fund allocation failed: {e}")
            return {'success': False, 'message': str(e)}
    
    def enhance_trade_execution(self, trade_func):
        """
        Decorator to automatically handle wallet linking and fund allocation
        
        Args:
            trade_func: Original trade execution function
        
        Returns:
            Enhanced trade execution function with automatic fund management
        """
        def wrapper(*args, **kwargs):
            user_id = kwargs.get('user_id') or (args[0] if args else None)
            trade_amount = kwargs.get('amount', 0)
            asset = kwargs.get('asset', 'USDC')  # Default to USDC
            
            if not user_id:
                return {'success': False, 'message': 'User ID required'}
            
            # Step 1: Ensure wallet is linked
            if not self._is_wallet_linked(user_id):
                link_result = self.link_wallet_silently(user_id)
                if not link_result['success']:
                    return link_result
            
            # Step 2: Check Mango V3 balance
            mango_balance = self.get_mango_balance(user_id)
            required_amount = trade_amount * 1.1  # Add 10% buffer for fees/slippage
            
            # Step 3: Auto-allocate if needed
            if not mango_balance['success'] or mango_balance.get('balance', 0) < required_amount:
                # Check internal balance
                internal_balance = self.wallet_manager.get_balance(user_id, asset)
                if not internal_balance['success']:
                    return {'success': False, 'message': 'Failed to check internal balance'}
                
                # Calculate needed allocation
                current_mango_balance = mango_balance.get('balance', 0) if mango_balance['success'] else 0
                needed_amount = required_amount - current_mango_balance
                
                if internal_balance['balance'] < needed_amount:
                    return {
                        'success': False,
                        'message': f'Insufficient balance. Need {needed_amount} {asset}, have {internal_balance["balance"]}'
                    }
                
                # Auto-allocate funds
                allocation_result = self.allocate_funds(
                    user_id=user_id,
                    amount=needed_amount,
                    asset=asset
                )
                
                if not allocation_result['success']:
                    return allocation_result
                
                # Refresh Mango balance after allocation
                mango_balance = self.get_mango_balance(user_id)
            
            # Step 4: Execute trade with verified balance
            kwargs['available_balance'] = mango_balance
            return trade_func(*args, **kwargs)
        
        return wrapper