"""
Non-Custodial Wallet Manager for Grace Project

This module implements non-custodial wallet functionality for Solana wallets.
Private keys are never stored on the server, only public keys.
"""

import os
import json
import base64
import logging
import requests
from datetime import datetime
from typing import Dict, Any, Optional

from src.config import get_config

logger = logging.getLogger("NonCustodialWalletManager")

class NonCustodialWalletManager:
    """
    Non-custodial wallet manager for Solana wallets.
    Private keys are never stored on the server.
    """
    
    def __init__(
        self,
        user_profile_system=None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the Non-Custodial Wallet Manager.
        
        Args:
            user_profile_system: User profile system for user data
            config: Additional configuration options
        """
        self.user_profile_system = user_profile_system
        self.config = config or {}
        
        # Use existing Solana RPC settings
        self.solana_rpc_url = get_config().get("solana_rpc_url")
        self.solana_network = get_config().get("solana_network")
        
        logger.info(f"Initialized Non-Custodial Wallet Manager")
        logger.info(f"Solana RPC URL: {self.solana_rpc_url}")
        logger.info(f"Solana network: {self.solana_network}")
    
    def generate_internal_wallet(self, user_id: str) -> Dict[str, Any]:
        """
        Register a client-generated wallet for a user.
        In non-custodial mode, this only stores the public key.
        
        Args:
            user_id: User ID
            
        Returns:
            Dict[str, Any]: Wallet information with status and message
        """
        logger.info(f"Registering non-custodial wallet for user: {user_id}")
        
        # Validate user_id
        if not user_id or not isinstance(user_id, str):
            error_msg = f"Invalid user_id: {user_id}"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}
        
        try:
            # Check for existing wallet
            if self.user_profile_system:
                user_data = self.user_profile_system.get_user_profile(user_id)
                if user_data and "internal_wallet" in user_data:
                    wallet_address = user_data["internal_wallet"].get("public_key")
                    if wallet_address:
                        logger.info(f"User {user_id} already has a registered wallet")
                        return {
                            "status": "success",
                            "message": "User already has a registered wallet",
                            "wallet_address": wallet_address,
                        }
            
            # For non-custodial, we only store a placeholder
            # The actual wallet will be created client-side
            wallet_data = {
                "wallet_type": "non_custodial",
                "status": "pending_client_generation",
                "created_at": datetime.utcnow().isoformat(),
            }
            
            # Save to user profile
            if self.user_profile_system:
                self.user_profile_system.update_user_data(
                    user_id, {"internal_wallet": wallet_data}
                )
            
            logger.info(f"Non-custodial wallet placeholder registered for user {user_id}")
            return {
                "status": "success",
                "message": "Non-custodial wallet registration initiated",
                "wallet_data": wallet_data,
            }
            
        except Exception as e:
            error_msg = f"Error registering non-custodial wallet: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {"status": "error", "message": error_msg}
    
    def register_public_key(self, user_id: str, public_key: str) -> Dict[str, Any]:
        """
        Register a client-generated public key.
        
        Args:
            user_id: User ID
            public_key: Public key generated client-side
            
        Returns:
            Dict[str, Any]: Registration result
        """
        try:
            # Validate public key format
            if not public_key or len(public_key) < 32:
                return {"status": "error", "message": "Invalid public key format"}
            
            # Update user profile with public key
            wallet_data = {
                "public_key": public_key,
                "wallet_type": "non_custodial",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "status": "active",
            }
            
            if self.user_profile_system:
                self.user_profile_system.update_user_data(
                    user_id, {"internal_wallet": wallet_data}
                )
            
            logger.info(f"Registered public key for user {user_id}: {public_key}")
            return {
                "status": "success",
                "message": "Public key registered successfully",
                "wallet_address": public_key,
            }
            
        except Exception as e:
            logger.error(f"Error registering public key: {str(e)}")
            return {"status": "error", "message": f"Error registering public key: {str(e)}"}
    
    def get_wallet_balance(self, user_id: str, wallet_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Get wallet balance for a user.
        
        Args:
            user_id: User ID
            wallet_type: Wallet type (internal, phantom, or None for both)
            
        Returns:
            Dict[str, Any]: Wallet balance
        """
        try:
            # Get user profile
            if not self.user_profile_system:
                return {"status": "error", "message": "User profile system not available"}
                
            user_data = self.user_profile_system.get_user_profile(user_id)
            if not user_data:
                return {"status": "error", "message": "User not found"}
            
            # Get wallet address based on type
            wallet_address = None
            if not wallet_type or wallet_type == "internal":
                if "internal_wallet" in user_data:
                    wallet_address = user_data["internal_wallet"].get("public_key")
            elif wallet_type == "phantom":
                if "phantom_wallet" in user_data:
                    wallet_address = user_data["phantom_wallet"].get("address")
            
            if not wallet_address:
                return {"status": "error", "message": f"No {wallet_type or 'internal'} wallet found"}
            
            # Query balance from Solana RPC
            # Using existing Solana RPC URL from config
            balance = self._query_solana_balance(wallet_address)
            
            return {
                "status": "success",
                "wallet_address": wallet_address,
                "balance": balance,
            }
            
        except Exception as e:
            logger.error(f"Error getting wallet balance: {str(e)}")
            return {"status": "error", "message": f"Error getting wallet balance: {str(e)}"}
    
    def _query_solana_balance(self, wallet_address: str) -> float:
        """
        Query balance from Solana RPC.
        
        Args:
            wallet_address: Wallet address
            
        Returns:
            float: Balance in SOL
        """
        # Implementation using Solana's getBalance API
        # Following Solana API docs: https://solana.com/docs/rpc
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getBalance",
                "params": [wallet_address]
            }
            
            response = requests.post(self.solana_rpc_url, json=payload)
            data = response.json()
            
            if "result" in data and "value" in data["result"]:
                # Convert lamports to SOL (1 SOL = 10^9 lamports)
                balance_lamports = data["result"]["value"]
                balance_sol = balance_lamports / 1_000_000_000
                return balance_sol
            else:
                logger.error(f"Invalid response from Solana RPC: {data}")
                return 0.0
                
        except Exception as e:
            logger.error(f"Error querying Solana balance: {str(e)}")
            return 0.0
    
    def connect_phantom_wallet(self, user_id: str, phantom_address: str) -> Dict[str, Any]:
        """
        Connect a Phantom wallet to a user account.
        
        Args:
            user_id: User ID
            phantom_address: Phantom wallet address
            
        Returns:
            Dict[str, Any]: Connection result
        """
        # This method can remain the same as in the custodial implementation
        # since it only stores the public address of the Phantom wallet
        try:
            # Check if user profile system is available
            if not self.user_profile_system:
                logger.error("User profile system not available")
                return {
                    "status": "error",
                    "message": "User profile system not available",
                }

            # Validate Phantom address
            if not phantom_address or len(phantom_address) < 32:
                return {"status": "error", "message": "Invalid Phantom wallet address"}

            # Save to user profile
            phantom_data = {
                "address": phantom_address,
                "connected_at": datetime.utcnow().isoformat(),
            }

            self.user_profile_system.update_user_data(
                user_id, {"phantom_wallet": phantom_data}
            )

            logger.info(
                f"Connected Phantom wallet for user {user_id}: {phantom_address}"
            )

            return {
                "status": "success",
                "message": "Phantom wallet connected successfully",
                "wallet_address": phantom_address,
            }
        except Exception as e:
            logger.error(f"Error connecting Phantom wallet: {str(e)}")
            return {
                "status": "error",
                "message": f"Error connecting Phantom wallet: {str(e)}",
            }
