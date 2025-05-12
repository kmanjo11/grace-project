"""
Transaction Confirmation System for Grace - A crypto trading application based on Open Interpreter

This module implements a secure transaction confirmation system for Solana trading
via GMGN API. It provides a two-step confirmation process to ensure users explicitly
approve transactions before execution.
"""

import json
import time
import logging
import hashlib
import secrets
import re
import uuid
from typing import Dict, Optional, Any, Union
from datetime import datetime, timedelta
import requests

try:
    from src.config import get_config
except ImportError:
    from config import get_config
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("GraceTransactionConfirmation")

class TransactionConfirmationSystem:
    """System for confirming and executing transactions securely."""
    
    def __init__(
        self,
        user_profile_system = None,
        gmgn_service = None,
        solana_wallet_manager = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the Transaction Confirmation System.
        
        Args:
            user_profile_system: User profile system for user data
            gmgn_service: GMGN service for trading operations
            solana_wallet_manager: Solana wallet manager
            config: Additional configuration options
        """
        self.user_profile_system = user_profile_system
        self.gmgn_service = gmgn_service
        self.solana_wallet_manager = solana_wallet_manager
        self.config = config or {}
        
        # GMGN API endpoints
        self.gmgn_router_endpoint = get_config().get("gmgn_router_endpoint")
        # Extract the base URL for the trade endpoint (removing the get_swap_route part)
        base_url = self.gmgn_router_endpoint.rsplit('/', 1)[0] if self.gmgn_router_endpoint else "https://gmgn.ai/defi/router/v1/sol/tx"
        self.trade_endpoint = base_url
        
        # Transaction confirmation timeout (in seconds)
        self.confirmation_timeout = self.config.get("confirmation_timeout", 300)  # 5 minutes
        
        # In-memory cache of pending transactions (for quick access)
        self.pending_transactions = {}
        
        # Load any existing pending transactions from user profiles
        self._load_pending_transactions()
        
        logger.info(f"Initialized Transaction Confirmation System")
        logger.info(f"GMGN Router Endpoint: {self.gmgn_router_endpoint}")
    
    def prepare_transaction(
        self,
        user_id: str,
        transaction_type: str,
        parameters: Dict[str, Any],
        wallet_type: str = "internal"
    ) -> Dict[str, Any]:
        """
        Prepare a transaction for confirmation.
        
        Args:
            user_id: User ID
            transaction_type: Transaction type (swap, trade)
            parameters: Transaction parameters
            wallet_type: Wallet type (internal or phantom)
            
        Returns:
            Dict[str, Any]: Transaction preparation result
        """
        try:
            # Check if user profile system is available
            if not self.user_profile_system:
                logger.error("User profile system not available")
                return {
                    "status": "error",
                    "message": "User profile system not available"
                }
            
            # Handle 'send' transaction type
            if transaction_type == "send":
                # Validate parameters
                if "recipient_address" not in parameters:
                    logger.error("Missing recipient_address parameter")
                    return {
                        "status": "error",
                        "message": "Missing recipient_address parameter"
                    }
                
                if "amount" not in parameters:
                    logger.error("Missing amount parameter")
                    return {
                        "status": "error",
                        "message": "Missing amount parameter"
                    }
                
                recipient_address = parameters["recipient_address"]
                amount = float(parameters["amount"])
                token = parameters.get("token", "SOL")  # Default to SOL
                
                # Validate amount
                if amount <= 0:
                    logger.error(f"Invalid amount: {amount}")
                    return {
                        "status": "error",
                        "message": f"Invalid amount: {amount}"
                    }
                
                # Get wallet data
                if wallet_type == "internal":
                    wallet_data = self.solana_wallet_manager.wallet_connection_system.get_internal_wallet(user_id)
                    if not wallet_data:
                        logger.error(f"Internal wallet not found for user {user_id}")
                        return {
                            "status": "error",
                            "message": "Internal wallet not found"
                        }
                    
                    # Get wallet balance
                    wallet_balance = wallet_data.get("balance", {})
                    if token.lower() == "sol":
                        balance = wallet_balance.get("solana", 0)
                    else:
                        balance = wallet_balance.get("tether_usd", 0)
                    
                    # Check if sufficient balance
                    if amount > balance:
                        logger.error(f"Insufficient balance: {balance} {token} (needed: {amount} {token})")
                        return {
                            "status": "error",
                            "message": f"Insufficient balance: {balance} {token} (needed: {amount} {token})"
                        }
                    
                    # Generate confirmation ID
                    confirmation_id = self._generate_confirmation_id("send", user_id)
                    
                    # Create transaction data
                    transaction_data = {
                        "user_id": user_id,
                        "wallet_type": wallet_type,
                        "wallet_address": wallet_data["address"],
                        "transaction_type": "send",
                        "recipient_address": recipient_address,
                        "amount": amount,
                        "token": token,
                        "status": "pending",
                        "created_at": datetime.now().isoformat(),
                        "expires_at": (datetime.now() + timedelta(seconds=self.confirmation_timeout)).isoformat()
                    }
                    
                    # Store pending transaction
                    self.pending_transactions[confirmation_id] = transaction_data
                    
                    # Save to user profile
                    self._save_pending_transaction(user_id, confirmation_id, transaction_data)
                    
                    # Return confirmation data
                    return {
                        "status": "success",
                        "confirmation_id": confirmation_id,
                        "transaction_type": "send",
                        "recipient_address": recipient_address,
                        "amount": amount,
                        "token": token,
                        "wallet_type": wallet_type,
                        "expires_at": self.pending_transactions[confirmation_id]["expires_at"]
                    }
                elif wallet_type == "phantom":
                    # Get Phantom wallet data
                    phantom_wallets = self.solana_wallet_manager.wallet_connection_system.get_phantom_wallets(user_id)
                    if not phantom_wallets or len(phantom_wallets) == 0:
                        logger.error(f"Phantom wallet not found for user {user_id}")
                        return {
                            "status": "error",
                            "message": "Phantom wallet not connected"
                        }
                    
                    # Use the first Phantom wallet
                    wallet_data = phantom_wallets[0]
                    
                    # Generate confirmation ID
                    confirmation_id = self._generate_confirmation_id("send", user_id)
                    
                    # Create transaction data
                    transaction_data = {
                        "user_id": user_id,
                        "wallet_type": wallet_type,
                        "wallet_address": wallet_data["address"],
                        "transaction_type": "send",
                        "recipient_address": recipient_address,
                        "amount": amount,
                        "token": token,
                        "status": "pending",
                        "created_at": datetime.now().isoformat(),
                        "expires_at": (datetime.now() + timedelta(seconds=self.confirmation_timeout)).isoformat()
                    }
                    
                    # Store pending transaction
                    self.pending_transactions[confirmation_id] = transaction_data
                    
                    # Save to user profile
                    self._save_pending_transaction(user_id, confirmation_id, transaction_data)
                    
                    # Return confirmation data
                    return {
                        "status": "success",
                        "confirmation_id": confirmation_id,
                        "transaction_type": "send",
                        "recipient_address": recipient_address,
                        "amount": amount,
                        "token": token,
                        "wallet_type": wallet_type,
                        "expires_at": self.pending_transactions[confirmation_id]["expires_at"]
                    }
                else:
                    logger.error(f"Unsupported wallet type: {wallet_type}")
                    return {
                        "status": "error",
                        "message": f"Unsupported wallet type: {wallet_type}"
                    }
            
            # Check if GMGN service is available
            if not self.gmgn_service:
                logger.error("GMGN service not available")
                return {
                    "status": "error",
                    "message": "GMGN service not available"
                }
            
            # Check if Solana wallet manager is available
            if not self.solana_wallet_manager:
                logger.error("Solana wallet manager not available")
                return {
                    "status": "error",
                    "message": "Solana wallet manager not available"
                }
            
            # Get user data
            user_data = self.user_profile_system.get_user_data(user_id)
            
            if not user_data:
                logger.error(f"User {user_id} not found")
                return {
                    "status": "error",
                    "message": "User not found"
                }
            
            # Get wallet data
            wallet_data = None
            
            if wallet_type == "internal":
                if "internal_wallet" in user_data:
                    wallet_data = user_data["internal_wallet"]
                else:
                    logger.error(f"User {user_id} does not have an internal wallet")
                    return {
                        "status": "error",
                        "message": "No internal wallet found"
                    }
            elif wallet_type == "phantom":
                if "phantom_wallet" in user_data:
                    wallet_data = user_data["phantom_wallet"]
                else:
                    logger.error(f"User {user_id} does not have a connected Phantom wallet")
                    return {
                        "status": "error",
                        "message": "No Phantom wallet connected"
                    }
            else:
                logger.error(f"Invalid wallet type: {wallet_type}")
                return {
                    "status": "error",
                    "message": f"Invalid wallet type: {wallet_type}"
                }
            
            # Get wallet address
            wallet_address = wallet_data["address"]
            
            # Prepare transaction based on type
            if transaction_type == "swap":
                # Validate required parameters
                required_params = ["from_token", "to_token", "amount"]
                for param in required_params:
                    if param not in parameters:
                        return {
                            "status": "error",
                            "message": f"Missing required parameter: {param}"
                        }
                
                # Extract parameters
                from_token = parameters["from_token"]
                to_token = parameters["to_token"]
                amount = parameters["amount"]
                slippage = parameters.get("slippage", 10)  # Default 1% slippage
                
                # Convert token symbols to addresses
                from_token_address = self._get_token_address(from_token)
                to_token_address = self._get_token_address(to_token)
                
                # Query GMGN router for swap route
                route_params = {
                    "token_in_address": from_token_address,
                    "token_out_address": to_token_address,
                    "in_amount": self._convert_to_lamports(amount),
                    "from_address": wallet_address,
                    "slippage": slippage,
                    "swap_mode": "ExactIn",
                    "is_anti_mev": True
                }
                
                # Generate confirmation ID
                confirmation_id = self._generate_confirmation_id("swap", from_token, to_token, amount)
                
                # Store pending transaction
                self.pending_transactions[confirmation_id] = {
                    "user_id": user_id,
                    "transaction_type": "swap",
                    "parameters": route_params,
                    "wallet_type": wallet_type,
                    "wallet_address": wallet_address,
                    "created_at": datetime.now().isoformat(),
                    "expires_at": (datetime.now() + timedelta(seconds=self.confirmation_timeout)).isoformat()
                }
                
                # Return confirmation request
                return {
                    "status": "confirmation_required",
                    "confirmation_id": confirmation_id,
                    "transaction_type": "swap",
                    "from_token": from_token,
                    "to_token": to_token,
                    "amount": amount,
                    "slippage": slippage,
                    "wallet_address": wallet_address,
                    "wallet_type": wallet_type,
                    "expires_at": self.pending_transactions[confirmation_id]["expires_at"]
                }
            
            elif transaction_type == "trade":
                # Validate required parameters
                required_params = ["action", "token", "amount"]
                for param in required_params:
                    if param not in parameters:
                        return {
                            "status": "error",
                            "message": f"Missing required parameter: {param}"
                        }
                
                # Extract parameters
                action = parameters["action"]
                token = parameters["token"]
                amount = parameters["amount"]
                slippage = parameters.get("slippage", 10)  # Default 1% slippage
                
                # Determine from_token and to_token based on action
                if action == "buy":
                    from_token = "SOL"  # Use SOL symbol
                    to_token = token
                else:  # sell
                    from_token = token
                    to_token = "SOL"  # Use SOL symbol
                
                # Convert token symbols to addresses
                from_token_address = self._get_token_address(from_token)
                to_token_address = self._get_token_address(to_token)
                
                # Query GMGN router for trade route
                route_params = {
                    "token_in_address": from_token_address,
                    "token_out_address": to_token_address,
                    "in_amount": self._convert_to_lamports(amount),
                    "from_address": wallet_address,
                    "slippage": slippage,
                    "swap_mode": "ExactIn",
                    "is_anti_mev": True
                }
                
                # Generate confirmation ID
                confirmation_id = self._generate_confirmation_id(transaction_type, user_id)
                
                # Create transaction data
                transaction_data = {
                    "user_id": user_id,
                    "transaction_type": transaction_type,
                    "parameters": route_params,
                    "wallet_type": wallet_type,
                    "created_at": datetime.now().isoformat(),
                    "expires_at": (datetime.now() + timedelta(seconds=self.confirmation_timeout)).isoformat()
                }
                
                # Store in memory cache
                self.pending_transactions[confirmation_id] = transaction_data
                
                # Save to user profile
                self._save_pending_transaction(user_id, confirmation_id, transaction_data)
                
                # Return confirmation request
                return {
                    "status": "confirmation_required",
                    "confirmation_id": confirmation_id,
                    "transaction_type": "trade",
                    "action": action,
                    "token": token,
                    "amount": amount,
                    "slippage": slippage,
                    "wallet_address": wallet_address,
                    "wallet_type": wallet_type,
                    "expires_at": self.pending_transactions[confirmation_id]["expires_at"]
                }
            
            else:
                logger.error(f"Unsupported transaction type: {transaction_type}")
                return {
                    "status": "error",
                    "message": f"Unsupported transaction type: {transaction_type}"
                }
        except Exception as e:
            logger.error(f"Error preparing transaction: {str(e)}")
            return {
                "status": "error",
                "message": f"Error preparing transaction: {str(e)}"
            }
    
    def confirm_transaction(
        self,
        user_id: str,
        confirmation_id: str
    ) -> Dict[str, Any]:
        """
        Confirm and execute a transaction.
        
        Args:
            user_id: User ID
            confirmation_id: Confirmation ID
            
        Returns:
            Dict[str, Any]: Transaction result
        """
        try:
            # Check if confirmation ID exists
            if confirmation_id not in self.pending_transactions:
                logger.error(f"Confirmation ID not found: {confirmation_id}")
                return {
                    "status": "error",
                    "message": "Confirmation ID not found or expired"
                }
            
            # Get pending transaction
            pending_tx = self.pending_transactions[confirmation_id]
            
            # Check if user ID matches
            if pending_tx["user_id"] != user_id:
                logger.error(f"User ID mismatch: {user_id} vs {pending_tx['user_id']}")
                return {
                    "status": "error",
                    "message": "User ID mismatch"
                }
            
            # Check if transaction has expired
            expires_at = datetime.fromisoformat(pending_tx["expires_at"])
            if datetime.now() > expires_at:
                logger.error(f"Transaction expired: {confirmation_id}")
                del self.pending_transactions[confirmation_id]
                return {
                    "status": "error",
                    "message": "Transaction expired"
                }
            
            # Execute transaction based on type
            if pending_tx["transaction_type"] == "send":
                # Get transaction details
                recipient_address = pending_tx["recipient_address"]
                amount = pending_tx["amount"]
                token = pending_tx["token"]
                wallet_type = pending_tx["wallet_type"]
                wallet_address = pending_tx["wallet_address"]
                
                # Execute the send transaction
                try:
                    # For internal wallets, we update the balance in the user profile
                    if wallet_type == "internal":
                        # Get user profile
                        user_profile = self.user_profile_system.get_user_profile(user_id)
                        
                        if not user_profile.get('success') or 'profile' not in user_profile:
                            logger.error(f"User profile not found for user {user_id}")
                            return {
                                "status": "error",
                                "message": "User profile not found"
                            }
                        
                        profile = user_profile['profile']
                        
                        if "internal_wallet" not in profile:
                            logger.error(f"User {user_id} does not have an internal wallet")
                            return {
                                "status": "error",
                                "message": "No internal wallet found"
                            }
                        
                        # Update wallet balance
                        internal_wallet = profile["internal_wallet"]
                        balance = internal_wallet.get("balance", {})
                        
                        if token.lower() == "sol":
                            current_balance = balance.get("solana", 0)
                            if current_balance < amount:
                                logger.error(f"Insufficient balance: {current_balance} SOL (needed: {amount} SOL)")
                                return {
                                    "status": "error",
                                    "message": f"Insufficient balance: {current_balance} SOL (needed: {amount} SOL)"
                                }
                            balance["solana"] = current_balance - amount
                        else:  # USDC/Tether
                            current_balance = balance.get("tether_usd", 0)
                            if current_balance < amount:
                                logger.error(f"Insufficient balance: {current_balance} USDC (needed: {amount} USDC)")
                                return {
                                    "status": "error",
                                    "message": f"Insufficient balance: {current_balance} USDC (needed: {amount} USDC)"
                                }
                            balance["tether_usd"] = current_balance - amount
                        
                        # Update user profile
                        internal_wallet["balance"] = balance
                        profile["internal_wallet"] = internal_wallet
                        
                        # Create transaction record
                        transaction_record = {
                            "transaction_id": confirmation_id,
                            "type": "send",
                            "status": "completed",
                            "from_address": wallet_address,
                            "to_address": recipient_address,
                            "amount": amount,
                            "token": token,
                            "timestamp": datetime.now().isoformat(),
                            "fee": 0.000005  # Simulated transaction fee
                        }
                        
                        # Add transaction to user profile
                        if "transactions" not in profile:
                            profile["transactions"] = []
                        profile["transactions"].append(transaction_record)
                        
                        # Update the profile
                        self.user_profile_system.update_user_profile(user_id, {"internal_wallet": internal_wallet, "transactions": profile["transactions"]})
                        
                        # Remove pending transaction
                        del self.pending_transactions[confirmation_id]
                        self._remove_pending_transaction(user_id, confirmation_id)
                        
                        # Return success
                        return {
                            "status": "success",
                            "message": f"Successfully sent {amount} {token} to {recipient_address}",
                            "transaction": transaction_record
                        }
                    elif wallet_type == "phantom":
                        # For Phantom wallets, we'd need to create and sign a transaction
                        # This is a simplified version that just creates a record
                        logger.warning("Phantom wallet send not fully implemented - creating record only")
                        
                        # Get user profile
                        user_profile = self.user_profile_system.get_user_profile(user_id)
                        
                        if not user_profile.get('success') or 'profile' not in user_profile:
                            logger.error(f"User profile not found for user {user_id}")
                            return {
                                "status": "error",
                                "message": "User profile not found"
                            }
                        
                        profile = user_profile['profile']
                        
                        # Create transaction record
                        transaction_record = {
                            "transaction_id": confirmation_id,
                            "type": "send",
                            "status": "completed",
                            "from_address": wallet_address,
                            "to_address": recipient_address,
                            "amount": amount,
                            "token": token,
                            "timestamp": datetime.now().isoformat(),
                            "fee": 0.000005  # Simulated transaction fee
                        }
                        
                        # Add transaction to user profile
                        if "transactions" not in profile:
                            profile["transactions"] = []
                        profile["transactions"].append(transaction_record)
                        
                        # Update the profile
                        self.user_profile_system.update_user_profile(user_id, {"transactions": profile["transactions"]})
                        
                        # Remove pending transaction
                        del self.pending_transactions[confirmation_id]
                        self._remove_pending_transaction(user_id, confirmation_id)
                        
                        # Return success
                        return {
                            "status": "success",
                            "message": f"Successfully sent {amount} {token} to {recipient_address}",
                            "transaction": transaction_record
                        }
                    else:
                        logger.error(f"Unsupported wallet type: {wallet_type}")
                        return {
                            "status": "error",
                            "message": f"Unsupported wallet type: {wallet_type}"
                        }
                except Exception as e:
                    logger.error(f"Error executing send transaction: {str(e)}")
                    return {
                        "status": "error",
                        "message": f"Error executing send transaction: {str(e)}"
                    }
            elif pending_tx["transaction_type"] == "swap" or pending_tx["transaction_type"] == "trade":
                # Query GMGN router for swap route
                route_result = self._query_gmgn_router(pending_tx["parameters"])
                
                if route_result["status"] != "success":
                    logger.error(f"Error querying GMGN router: {route_result['message']}")
                    return route_result
                
                # Execute transaction with wallet
                tx_result = self._execute_transaction(
                    user_id,
                    pending_tx["wallet_type"],
                    route_result["data"]
                )
                
                # Remove pending transaction from memory cache
                del self.pending_transactions[confirmation_id]
                
                # Remove from user profile
                self._remove_pending_transaction(user_id, confirmation_id)
                
                return tx_result
            
            else:
                logger.error(f"Unsupported transaction type: {pending_tx['transaction_type']}")
                return {
                    "status": "error",
                    "message": f"Unsupported transaction type: {pending_tx['transaction_type']}"
                }
        except Exception as e:
            logger.error(f"Error confirming transaction: {str(e)}")
            return {
                "status": "error",
                "message": f"Error confirming transaction: {str(e)}"
            }
    
    def cancel_transaction(
        self,
        user_id: str,
        confirmation_id: str
    ) -> Dict[str, Any]:
        """
        Cancel a pending transaction.
        
        Args:
            user_id: User ID
            confirmation_id: Confirmation ID
            
        Returns:
            Dict[str, Any]: Cancellation result
        """
        try:
            # Check if confirmation ID exists
            if confirmation_id not in self.pending_transactions:
                logger.error(f"Confirmation ID not found: {confirmation_id}")
                return {
                    "status": "error",
                    "message": "Confirmation ID not found or expired"
                }
            
            # Get pending transaction
            pending_tx = self.pending_transactions[confirmation_id]
            
            # Check if user ID matches
            if pending_tx["user_id"] != user_id:
                logger.error(f"User ID mismatch: {user_id} vs {pending_tx['user_id']}")
                return {
                    "status": "error",
                    "message": "User ID mismatch"
                }
            
            # Remove pending transaction from memory cache
            del self.pending_transactions[confirmation_id]
            
            # Remove from user profile
            self._remove_pending_transaction(user_id, confirmation_id)
            
            return {
                "status": "success",
                "message": "Transaction cancelled successfully",
                "confirmation_id": confirmation_id
            }
        except Exception as e:
            logger.error(f"Error cancelling transaction: {str(e)}")
            return {
                "status": "error",
                "message": f"Error cancelling transaction: {str(e)}"
            }
    
    def get_pending_transactions(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Get pending transactions for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Dict[str, Any]: Pending transactions
        """
        try:
            # Filter pending transactions by user ID
            user_pending_txs = {}
            
            for confirmation_id, tx_data in self.pending_transactions.items():
                if tx_data["user_id"] == user_id:
                    # Check if transaction has expired
                    expires_at = datetime.fromisoformat(tx_data["expires_at"])
                    if datetime.now() > expires_at:
                        # Remove expired transaction
                        del self.pending_transactions[confirmation_id]
                        continue
                    
                    user_pending_txs[confirmation_id] = tx_data
            
            return {
                "status": "success",
                "pending_transactions": user_pending_txs
            }
        except Exception as e:
            logger.error(f"Error getting pending transactions: {str(e)}")
            return {
                "status": "error",
                "message": f"Error getting pending transactions: {str(e)}"
            }
    
    def _load_pending_transactions(self):
        """
        Load pending transactions from user profiles.
        """
        if not self.user_profile_system:
            logger.warning("User profile system not available, skipping transaction loading")
            return
            
        try:
            # Get all users
            users = self.user_profile_system.get_all_users()
            
            # For each user, load their pending transactions
            for user_id in users:
                user_data = self.user_profile_system.get_user_data(user_id)
                if user_data and "pending_transactions" in user_data:
                    pending_txs = user_data["pending_transactions"]
                    
                    # Add each transaction to the in-memory cache
                    for tx_id, tx_data in pending_txs.items():
                        # Check if transaction has expired
                        if "expires_at" in tx_data:
                            expires_at = datetime.fromisoformat(tx_data["expires_at"])
                            if datetime.now() > expires_at:
                                continue  # Skip expired transactions
                        
                        # Add to in-memory cache
                        self.pending_transactions[tx_id] = tx_data
            
            logger.info(f"Loaded {len(self.pending_transactions)} pending transactions from user profiles")
        except Exception as e:
            logger.error(f"Error loading pending transactions: {str(e)}")
    
    def _save_pending_transaction(self, user_id: str, confirmation_id: str, transaction_data: Dict[str, Any]):
        """
        Save a pending transaction to the user profile.
        
        Args:
            user_id: User ID
            confirmation_id: Confirmation ID
            transaction_data: Transaction data
        """
        if not self.user_profile_system:
            logger.warning("User profile system not available, skipping transaction saving")
            return
            
        try:
            # Get user data
            user_data = self.user_profile_system.get_user_data(user_id) or {}
            
            # Initialize pending transactions if not exists
            if "pending_transactions" not in user_data:
                user_data["pending_transactions"] = {}
            
            # Add transaction to pending transactions
            user_data["pending_transactions"][confirmation_id] = transaction_data
            
            # Update user data
            self.user_profile_system.update_user_data(user_id, user_data)
            
            logger.info(f"Saved pending transaction {confirmation_id} for user {user_id}")
        except Exception as e:
            logger.error(f"Error saving pending transaction: {str(e)}")
    
    def _remove_pending_transaction(self, user_id: str, confirmation_id: str):
        """
        Remove a pending transaction from the user profile.
        
        Args:
            user_id: User ID
            confirmation_id: Confirmation ID
        """
        if not self.user_profile_system:
            logger.warning("User profile system not available, skipping transaction removal")
            return
            
        try:
            # Get user data
            user_data = self.user_profile_system.get_user_data(user_id)
            
            if user_data and "pending_transactions" in user_data:
                # Remove transaction from pending transactions
                if confirmation_id in user_data["pending_transactions"]:
                    del user_data["pending_transactions"][confirmation_id]
                    
                    # Update user data
                    self.user_profile_system.update_user_data(user_id, user_data)
                    
                    logger.info(f"Removed pending transaction {confirmation_id} for user {user_id}")
        except Exception as e:
            logger.error(f"Error removing pending transaction: {str(e)}")
    
    def _get_token_address(self, token_symbol: str) -> str:
        """
        Convert token symbol to address.
        
        Args:
            token_symbol: Token symbol or address
            
        Returns:
            str: Token address
        """
        # Check if already an address (starts with a specific pattern or has correct length)
        if len(token_symbol) > 32 and not token_symbol.startswith("$"):
            # Likely already an address
            return token_symbol
        
        # Common Solana token addresses
        token_map = {
            "SOL": "So11111111111111111111111111111111111111112",  # Native SOL
            "USDC": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
            "USDT": "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",  # USDT
            "BTC": "9n4nbM75f5Ui33ZbPYXn59EwSgE8CGsHtAeTH5YFeJ9E",  # Wrapped BTC
            "ETH": "2FPyTwcZLUg1MDrwsyoP4D6s1tM7hAkHYRjkNb5w6Pxk",  # Wrapped ETH
            "SRM": "SRMuApVNdxXokk5GT7XD5cUUgXMBCoAz2LHeuAoKWRt",  # Serum
            "RAY": "4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R",  # Raydium
            "BONK": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",  # Bonk
            "SAMO": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",  # Samoyedcoin
            "ORCA": "orcaEKTdK7LKz57vaAYr9QeNsVEPfiu6QeMU1kektZE",  # Orca
        }
        
        # Normalize token symbol
        normalized_symbol = token_symbol.upper().strip()
        
        # Return address if found, otherwise return the original symbol
        # (which might be an address already)
        return token_map.get(normalized_symbol, token_symbol)
    
    def _convert_to_lamports(self, amount: Union[str, float, int]) -> int:
        """
        Convert amount to lamports (1 SOL = 1,000,000,000 lamports).
        
        Args:
            amount: Amount in user-friendly format
            
        Returns:
            int: Amount in lamports
        """
        try:
            # Convert amount to float first
            amount_float = float(amount)
            
            # Convert to lamports (1 SOL = 1,000,000,000 lamports)
            lamports = int(amount_float * 1_000_000_000)
            
            logger.info(f"Converted {amount} to {lamports} lamports")
            return lamports
        except (ValueError, TypeError) as e:
            logger.error(f"Error converting amount to lamports: {str(e)}")
            raise ValueError(f"Invalid amount format: {amount}")
        except Exception as e:
            logger.error(f"Unexpected error converting amount: {str(e)}")
            raise
    
    def process_phantom_callback(self, transaction_id: str, signature: str) -> Dict[str, Any]:
        """
        Process callback from Phantom wallet after transaction approval.
        
        Args:
            transaction_id: Transaction ID
            signature: Transaction signature
            
        Returns:
            Dict[str, Any]: Transaction result
        """
        try:
            # Check if transaction ID exists
            if transaction_id not in self.pending_transactions:
                logger.error(f"Transaction ID not found: {transaction_id}")
                return {
                    "status": "error",
                    "message": "Transaction ID not found or expired"
                }
            
            # Get pending transaction
            pending_tx = self.pending_transactions[transaction_id]
            
            # Check if transaction has expired
            expires_at = datetime.fromisoformat(pending_tx["expires_at"])
            if datetime.now() > expires_at:
                logger.error(f"Transaction expired: {transaction_id}")
                del self.pending_transactions[transaction_id]
                self._remove_pending_transaction(pending_tx["user_id"], transaction_id)
                return {
                    "status": "error",
                    "message": "Transaction expired"
                }
            
            # Submit the signature to the GMGN API
            submit_url = f"{self.trade_endpoint}/submit_signed_bundle_transaction"
            
            # Prepare payload
            payload = {
                "signature": signature,
                "wallet_address": pending_tx["wallet_address"]
            }
            
            # Make request
            response = requests.post(submit_url, json=payload, timeout=30)
            
            # Remove pending transaction
            del self.pending_transactions[transaction_id]
            self._remove_pending_transaction(pending_tx["user_id"], transaction_id)
            
            # Check response
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 0 and result.get("msg") == "success":
                    tx_hash = result.get("data", {}).get("hash")
                    
                    return {
                        "status": "success",
                        "message": "Transaction submitted successfully",
                        "transaction_hash": tx_hash
                    }
                else:
                    return {
                        "status": "error",
                        "message": f"GMGN API error: {result.get('msg')}"
                    }
            else:
                return {
                    "status": "error",
                    "message": f"HTTP error: {response.status_code}"
                }
        except Exception as e:
            logger.error(f"Error processing Phantom callback: {str(e)}")
            return {
                "status": "error",
                "message": f"Error processing Phantom callback: {str(e)}"
            }
    
    def check_transaction_status(self, transaction_hash: str) -> Dict[str, Any]:
        """
        Check the status of a transaction on the blockchain.
        
        Args:
            transaction_hash: Transaction hash
            
        Returns:
            Dict[str, Any]: Transaction status
        """
        try:
            # Use Solana RPC to check transaction status
            rpc_url = get_config().get("solana_rpc_url")
            
            if not rpc_url:
                logger.error("Solana RPC URL not configured")
                return {
                    "status": "error",
                    "message": "Solana RPC URL not configured"
                }
            
            # Build RPC request
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTransaction",
                "params": [
                    transaction_hash,
                    {"encoding": "json", "commitment": "confirmed"}
                ]
            }
            
            # Make request
            response = requests.post(rpc_url, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                if "result" in result and result["result"]:
                    tx_data = result["result"]
                    
                    # Check confirmation status
                    if tx_data.get("meta", {}).get("err") is None:
                        # Transaction was successful
                        return {
                            "status": "success",
                            "transaction_status": "confirmed",
                            "confirmations": tx_data.get("meta", {}).get("confirmations"),
                            "timestamp": tx_data.get("blockTime"),
                            "fee": tx_data.get("meta", {}).get("fee"),
                            "details": tx_data
                        }
                    else:
                        # Transaction failed
                        return {
                            "status": "error",
                            "transaction_status": "failed",
                            "error": tx_data.get("meta", {}).get("err"),
                            "details": tx_data
                        }
                else:
                    # Transaction not found or not confirmed yet
                    return {
                        "status": "pending",
                        "message": "Transaction not yet confirmed or not found"
                    }
            else:
                logger.error(f"Error checking transaction status: HTTP {response.status_code}")
                return {
                    "status": "error",
                    "message": f"Error checking transaction status: HTTP {response.status_code}"
                }
        except Exception as e:
            logger.error(f"Error checking transaction status: {str(e)}")
            return {
                "status": "error",
                "message": f"Error checking transaction status: {str(e)}"
            }
    
    def _generate_confirmation_id(self, *args) -> str:
        """
        Generate a unique confirmation ID.
        
        Args:
            *args: Arguments to include in the ID
            
        Returns:
            str: Confirmation ID
        """
        try:
            # Concatenate all arguments
            args_str = "_".join([str(arg) for arg in args])
            
            # Generate a timestamp
            timestamp = int(time.time())
            
            # Generate a random component
            random_component = secrets.token_hex(4)
            
            # Combine all components
            combined = f"{args_str}_{timestamp}_{random_component}"
            
            # Hash the combined string
            confirmation_id = hashlib.sha256(combined.encode()).hexdigest()[:16]
            
            return confirmation_id
        except Exception as e:
            logger.error(f"Error generating confirmation ID: {str(e)}")
            return f"tx_{int(time.time())}_{secrets.token_hex(4)}"
    
    def _convert_to_lamports(self, amount: Union[str, float]) -> str:
        """
        Convert SOL amount to lamports.
        
        Args:
            amount: Amount in SOL
            
        Returns:
            str: Amount in lamports
        """
        try:
            # 1 SOL = 10^9 lamports
            amount_float = float(amount)
            lamports = int(amount_float * 1_000_000_000)
            return str(lamports)
        except ValueError:
            logger.error(f"Invalid amount: {amount}")
            return "0"
    
    def _query_gmgn_router(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Query GMGN router for swap route.
        
        Args:
            params: Query parameters
            
        Returns:
            Dict[str, Any]: Query result
        """
        try:
            # Use the full endpoint URL
            url = self.gmgn_router_endpoint
            
            # Map our parameters to GMGN API parameters
            required_params = {
                "token_in_address": params.get("from_token"),
                "token_out_address": params.get("to_token"),
                "in_amount": params.get("amount"),
                "from_address": params.get("wallet_address"),
                "slippage": params.get("slippage", 0.5)  # Default 0.5% slippage
            }
            
            # Add optional parameters if present
            if "swap_mode" in params:
                required_params["swap_mode"] = params["swap_mode"]
            if "fee" in params:
                required_params["fee"] = params["fee"]
            if "is_anti_mev" in params:
                required_params["is_anti_mev"] = params["is_anti_mev"]
            
            logger.info(f"Querying GMGN router with params: {required_params}")
            
            # Make request
            response = requests.get(url, params=required_params, timeout=30)
            
            # Check response
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 0 and data.get("msg") == "success":
                    return {
                        "status": "success",
                        "data": data.get("data"),
                        "message": "Successfully retrieved swap route"
                    }
                else:
                    logger.error(f"GMGN API error: {data.get('msg')}")
                    return {
                        "status": "error",
                        "message": f"GMGN API error: {data.get('msg')}"
                    }
            else:
                logger.error(f"HTTP error: {response.status_code}")
                return {
                    "status": "error",
                    "message": f"HTTP error: {response.status_code}"
                }
        except Exception as e:
            logger.error(f"Error querying GMGN router: {str(e)}")
            return {
                "status": "error",
                "message": f"Error querying GMGN router: {str(e)}"
            }
    
    def _execute_transaction(
        self,
        user_id: str,
        wallet_type: str,
        transaction_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a transaction with wallet.
        
        Args:
            user_id: User ID
            wallet_type: Wallet type (internal or phantom)
            transaction_data: Transaction data from GMGN router
            
        Returns:
            Dict[str, Any]: Transaction result
        """
        try:
            # Extract transaction details
            swap_transaction = transaction_data.get("raw_tx", {}).get("swapTransaction")
            last_valid_block_height = transaction_data.get("raw_tx", {}).get("lastValidBlockHeight")
            
            if not swap_transaction:
                logger.error("Missing swap transaction data")
                return {
                    "status": "error",
                    "message": "Missing swap transaction data"
                }
            
            # Get quote details for response
            quote_details = {
                "inputMint": transaction_data.get("quote", {}).get("inputMint"),
                "inAmount": transaction_data.get("quote", {}).get("inAmount"),
                "outputMint": transaction_data.get("quote", {}).get("outputMint"),
                "outAmount": transaction_data.get("quote", {}).get("outAmount")
            }
            
            # For internal wallets, we need to sign the transaction
            if wallet_type == "internal":
                # Get user's wallet from user profile system
                user_data = self.user_profile_system.get_user_data(user_id)
                if not user_data or "internal_wallet" not in user_data:
                    return {
                        "status": "error",
                        "message": "Internal wallet not found for user"
                    }
                
                # Get wallet data
                internal_wallet = user_data["internal_wallet"]
                wallet_address = internal_wallet.get("address") or internal_wallet.get("public_key")
                private_key_encrypted = internal_wallet.get("private_key_encrypted")
                
                if not wallet_address or not private_key_encrypted:
                    return {
                        "status": "error",
                        "message": "Wallet data incomplete"
                    }
                
                try:
                    # Import required libraries
                    import base64
                    import nacl.signing
                    
                    # Decrypt private key
                    if self.user_profile_system and hasattr(self.user_profile_system, 'secure_data_manager'):
                        private_key_bytes = self.user_profile_system.secure_data_manager.decrypt(private_key_encrypted)
                    else:
                        # Fallback to base64 decoding if no secure data manager
                        private_key_bytes = base64.b64decode(private_key_encrypted)
                    
                    # Decode the transaction from base64
                    swap_transaction_buf = base64.b64decode(swap_transaction)
                    
                    # Create a signing key from the private key
                    signing_key = nacl.signing.SigningKey(private_key_bytes)
                    
                    # Sign the transaction data
                    signature = signing_key.sign(swap_transaction_buf)
                    
                    # In GMGN API, we need to submit the base64-encoded signed transaction
                    # This is a simplified approach since we don't have the full Solana SDK
                    # In a real implementation with the SDK, we would use:
                    # transaction.sign([keypair])
                    # signed_tx = base64.b64encode(transaction.serialize()).decode('utf-8')
                    signed_tx = base64.b64encode(signature).decode('utf-8')
                    
                    # Submit transaction
                    submit_url = f"{self.trade_endpoint}/submit_signed_transaction"
                    response = requests.post(
                        submit_url,
                        json={"signed_tx": signed_tx},
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result.get("code") == 0 and result.get("msg") == "success":
                            tx_hash = result.get("data", {}).get("hash")
                            
                            # Start checking transaction status
                            return {
                                "status": "success",
                                "message": "Transaction submitted successfully",
                                "transaction_hash": tx_hash,
                                "last_valid_block_height": last_valid_block_height,
                                "details": quote_details
                            }
                        else:
                            return {
                                "status": "error",
                                "message": f"GMGN API error: {result.get('msg')}"
                            }
                    else:
                        return {
                            "status": "error",
                            "message": f"HTTP error: {response.status_code}"
                        }
                except ImportError as e:
                    logger.error(f"Missing required libraries: {str(e)}")
                    return {
                        "status": "error",
                        "message": f"Missing required libraries: {str(e)}",
                        "details": "Please install solana-sdk package"
                    }
                except Exception as e:
                    logger.error(f"Error signing and submitting transaction: {str(e)}")
                    return {
                        "status": "error",
                        "message": f"Error signing and submitting transaction: {str(e)}"
                    }
            
            # For Phantom wallets, we need to redirect the user to approve the transaction
            elif wallet_type == "phantom":
                # Get user's wallet from user profile system
                user_data = self.user_profile_system.get_user_data(user_id)
                phantom_wallets = user_data.get("phantom_wallets", [])
                
                if not phantom_wallets:
                    return {
                        "status": "error",
                        "message": "No Phantom wallet connected for user"
                    }
                
                # Use the first connected Phantom wallet
                phantom_wallet = phantom_wallets[0] if isinstance(phantom_wallets, list) else phantom_wallets
                wallet_address = phantom_wallet.get("wallet_address") or phantom_wallet.get("address")
                
                if not wallet_address:
                    return {
                        "status": "error",
                        "message": "Phantom wallet address not found"
                    }
                
                try:
                    # For Phantom, we need to create a deep link to the Phantom app
                    phantom_app_url = get_config().get("phantom_app_url", "https://phantom.app")
                    api_base_url = get_config().get("api_base_url", "")
                    
                    # Generate a unique transaction ID
                    transaction_id = f"phantom_tx_{int(time.time())}_{uuid.uuid4().hex[:8]}"
                    
                    # Store transaction data in memory for callback processing
                    self.pending_transactions[transaction_id] = {
                        "user_id": user_id,
                        "transaction_type": "phantom_approval",
                        "transaction_data": swap_transaction,
                        "wallet_address": wallet_address,
                        "created_at": datetime.now().isoformat(),
                        "expires_at": (datetime.now() + timedelta(seconds=self.confirmation_timeout)).isoformat()
                    }
                    
                    # Save to user profile
                    self._save_pending_transaction(user_id, transaction_id, self.pending_transactions[transaction_id])
                    
                    # Create callback URL
                    callback_path = get_config().get("phantom_callback_path", "/auth/phantom/callback")
                    callback_url = f"{api_base_url}{callback_path}?tx_id={transaction_id}"
                    
                    # Create deep link to Phantom app
                    # Format: phantom://ul/v1/connect?app_url={callback_url}&redirect_link=true
                    deep_link = f"{phantom_app_url}/ul/v1/connect?app_url={callback_url}&redirect_link=true"
                    
                    # For web app, create a URL that will open Phantom app
                    web_link = f"https://phantom.app/ul/v1/connect?app_url={callback_url}&redirect_link=true"
                    
                    return {
                        "status": "pending_approval",
                        "message": "Transaction requires approval in Phantom wallet",
                        "transaction_id": transaction_id,
                        "approval_url": web_link,
                        "deep_link": deep_link,
                        "wallet_address": wallet_address,
                        "details": quote_details,
                        "expires_at": self.pending_transactions[transaction_id]["expires_at"]
                    }
                except Exception as e:
                    logger.error(f"Error preparing Phantom transaction: {str(e)}")
                    return {
                        "status": "error",
                        "message": f"Error preparing Phantom transaction: {str(e)}"
                    }
            
            # Should never reach here
            return {
                "status": "error",
                "message": f"Unsupported wallet type: {wallet_type}"
            }
        except Exception as e:
            logger.error(f"Error executing transaction: {str(e)}")
            return {
                "status": "error",
                "message": f"Error executing transaction: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Error executing transaction: {str(e)}")
            return {
                "status": "error",
                "message": f"Error executing transaction: {str(e)}"
            }
    
    def process_natural_language_request(
        self,
        user_id: str,
        request: str
    ) -> Dict[str, Any]:
        """
        Process a natural language request related to transactions.
        
        Args:
            user_id: User ID
            request: Natural language request
            
        Returns:
            Dict[str, Any]: Response to the request
        """
        request_lower = request.lower()
        
        # Check for transaction confirmation
        confirm_patterns = [
            r"confirm (transaction|tx) ([a-zA-Z0-9_]+)",
            r"approve (transaction|tx) ([a-zA-Z0-9_]+)",
            r"execute (transaction|tx) ([a-zA-Z0-9_]+)"
        ]
        
        for pattern in confirm_patterns:
            match = re.search(pattern, request_lower)
            if match:
                confirmation_id = match.group(2)
                return self.confirm_transaction(user_id, confirmation_id)
        
        # Check for transaction cancellation
        cancel_patterns = [
            r"cancel (transaction|tx) ([a-zA-Z0-9_]+)",
            r"reject (transaction|tx) ([a-zA-Z0-9_]+)",
            r"decline (transaction|tx) ([a-zA-Z0-9_]+)"
        ]
        
        for pattern in cancel_patterns:
            match = re.search(pattern, request_lower)
            if match:
                confirmation_id = match.group(2)
                return self.cancel_transaction(user_id, confirmation_id)
        
        # Check for pending transactions
        pending_patterns = [
            r"(show|list|get) (pending|my) transactions",
            r"what transactions (are pending|do i have)",
            r"pending transactions"
        ]
        
        for pattern in pending_patterns:
            if re.search(pattern, request_lower):
                return self.get_pending_transactions(user_id)
        
        # If no specific transaction request was identified, return an error
        return {
            "status": "error",
            "message": "I'm not sure what you're asking about transactions. Try asking about confirming, cancelling, or listing pending transactions."
        }

# Example usage
if __name__ == "__main__":
    # Initialize Transaction Confirmation System
    tx_system = TransactionConfirmationSystem()
    
    # Prepare a transaction
    result = tx_system.prepare_transaction(
        user_id="test_user",
        transaction_type="swap",
        parameters={
            "from_token": "So11111111111111111111111111111111111111112",
            "to_token": "7EYnhQoR9YM3N7UoaKRoA44Uy8JeaZV3qyouov87awMs",
            "amount": "0.1"
        }
    )
    print(json.dumps(result, indent=2))
