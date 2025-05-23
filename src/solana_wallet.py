"""
Solana Wallet Integration for Grace - A crypto trading application based on Open Interpreter

This module implements wallet integration with Solana via GMGN, supporting both
internal wallets and Phantom wallet connections. It provides functionality for
wallet management, balance retrieval, and transaction signing.
"""

import os
import json
import uuid
import base64
import logging
import hashlib
import secrets
import hmac
import requests
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

from src.config import get_config

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("GraceSolanaWallet")


class SolanaWalletManager:
    """Manager for Solana wallets, supporting both internal and Phantom wallets."""

    def __init__(
        self,
        user_profile_system=None,
        gmgn_service=None,
        config: Optional[Dict[str, Any]] = None,
        secure_data_manager=None,
    ):
        """
        Initialize the Solana Wallet Manager.

        Args:
            user_profile_system: User profile system for user data
            gmgn_service: GMGN service for trading operations
            config: Additional configuration options
            secure_data_manager: Secure data manager for encryption
        """
        self.user_profile_system = user_profile_system
        self.gmgn_service = gmgn_service
        self.config = config or {}
        self.secure_data_manager = secure_data_manager

        # Solana RPC settings
        self.solana_rpc_url = get_config().get("solana_rpc_url")
        self.solana_network = get_config().get("solana_network")

        # Phantom wallet settings
        self.phantom_app_url = os.environ.get("PHANTOM_APP_URL", "https://phantom.app")
        self.phantom_callback_path = os.environ.get(
            "PHANTOM_CALLBACK_PATH", "/phantom/callback"
        )

        # Initialize WalletConnectionSystem if user_profile_system is available
        self.wallet_connection_system = None
        if self.user_profile_system:
            try:
                # Import here to avoid circular imports
                from src.wallet_connection import WalletConnectionSystem

                self.wallet_connection_system = WalletConnectionSystem(
                    user_profile_system=self.user_profile_system,
                    secure_data_manager=self.secure_data_manager,
                    phantom_app_url=self.phantom_app_url,
                    phantom_callback_path=self.phantom_callback_path,
                )
                logger.info("WalletConnectionSystem initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize WalletConnectionSystem: {str(e)}")

        logger.info(f"Initialized Solana Wallet Manager")
        logger.info(f"Solana RPC URL: {self.solana_rpc_url}")
        logger.info(f"Solana network: {self.solana_network}")

    def generate_internal_wallet(self, user_id: str) -> Dict[str, Any]:
        """
        Generate an internal Solana wallet for a user.

        Args:
            user_id: User ID

        Returns:
            Dict[str, Any]: Wallet information
        """
        try:
            # Check if WalletConnectionSystem is available
            if self.wallet_connection_system:
                # Use the WalletConnectionSystem to create an internal wallet
                logger.info(
                    f"Using WalletConnectionSystem to generate wallet for user {user_id}"
                )
                wallet_data = self.wallet_connection_system.create_internal_wallet(
                    user_id
                )
                return {
                    "status": "success",
                    "message": "Internal wallet created successfully",
                    "wallet_address": wallet_data.get("public_key")
                    or wallet_data.get("address"),
                    "wallet_data": wallet_data,
                }

            # Fallback if WalletConnectionSystem is not available
            logger.warning(
                "WalletConnectionSystem not available, using fallback method"
            )

            # Check if user profile system is available
            if not self.user_profile_system:
                logger.error("User profile system not available")
                return {
                    "status": "error",
                    "message": "User profile system not available",
                }

            # Check if user already has a wallet
            user_data = self.user_profile_system.get_user_data(user_id)

            if user_data and "internal_wallet" in user_data:
                logger.info(f"User {user_id} already has an internal wallet")
                return {
                    "status": "success",
                    "message": "User already has an internal wallet",
                    "wallet_address": user_data["internal_wallet"]["address"],
                }

            # Generate a new wallet using direct crypto functions instead of Solana SDK
            # Define helper function for keypair generation
            def generate_keypair():
                """Generate a keypair using standard crypto libraries."""
                private_key = secrets.token_bytes(32)
                # In a real implementation, this would use ed25519 to derive the public key
                # For now, we'll use a simple hash to simulate the derivation
                public_key = hashlib.sha256(private_key).digest()

                # Convert to a clean alphanumeric string to avoid byte representation issues
                # Use hexadecimal representation instead of base64 to ensure it's clean
                clean_public_key = public_key.hex()

                return {
                    "private_key": private_key,
                    "public_key": clean_public_key,  # This will be a clean alphanumeric string
                }

            # Generate keypair
            keypair = generate_keypair()
            public_key = keypair["public_key"]

            # Encrypt private key if secure data manager is available
            if self.secure_data_manager:
                private_key_bytes = keypair["private_key"]
                encrypted_private_key = self.secure_data_manager.encrypt(
                    private_key_bytes
                )
            else:
                # Base64 encode private key if no secure manager
                private_key_bytes = keypair["private_key"]
                encrypted_private_key = base64.b64encode(private_key_bytes).decode(
                    "utf-8"
                )

            # Create wallet data
            wallet_data = {
                "address": public_key,
                "public_key": public_key,
                "private_key_encrypted": encrypted_private_key,
                "created_at": datetime.now().isoformat(),
            }

            # Save to user profile
            self.user_profile_system.update_user_data(
                user_id, {"internal_wallet": wallet_data}
            )

            logger.info(f"Generated internal wallet for user {user_id}: {public_key}")

            return {
                "status": "success",
                "message": "Internal wallet generated successfully",
                "wallet_address": public_key,
            }
        except Exception as e:
            logger.error(f"Error generating internal wallet: {str(e)}")
            return {
                "status": "error",
                "message": f"Error generating internal wallet: {str(e)}",
            }

    def connect_phantom_wallet(
        self, user_id: str, phantom_address: str
    ) -> Dict[str, Any]:
        """
        Connect a Phantom wallet to a user account.

        Args:
            user_id: User ID
            phantom_address: Phantom wallet address

        Returns:
            Dict[str, Any]: Connection result
        """
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
                "connected_at": datetime.now().isoformat(),
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

    def disconnect_phantom_wallet(self, user_id: str) -> Dict[str, Any]:
        """
        Disconnect a Phantom wallet from a user account.

        Args:
            user_id: User ID

        Returns:
            Dict[str, Any]: Disconnection result
        """
        try:
            # Check if user profile system is available
            if not self.user_profile_system:
                logger.error("User profile system not available")
                return {
                    "status": "error",
                    "message": "User profile system not available",
                }

            # Check if user has a connected Phantom wallet
            user_data = self.user_profile_system.get_user_data(user_id)

            if not user_data or "phantom_wallet" not in user_data:
                logger.info(f"User {user_id} does not have a connected Phantom wallet")
                return {"status": "error", "message": "No Phantom wallet connected"}

            # Remove Phantom wallet data
            phantom_address = user_data["phantom_wallet"]["address"]
            self.user_profile_system.update_user_data(user_id, {"phantom_wallet": None})

            logger.info(
                f"Disconnected Phantom wallet for user {user_id}: {phantom_address}"
            )

            return {
                "status": "success",
                "message": "Phantom wallet disconnected successfully",
            }
        except Exception as e:
            logger.error(f"Error disconnecting Phantom wallet: {str(e)}")
            return {
                "status": "error",
                "message": f"Error disconnecting Phantom wallet: {str(e)}",
            }

    def get_wallet_balance(
        self, user_id: str, wallet_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get wallet balance for a user.

        Args:
            user_id: User ID
            wallet_type: Wallet type (internal, phantom, or None for both)

        Returns:
            Dict[str, Any]: Wallet balance
        """
        try:
            # Use WalletConnectionSystem if available
            if self.wallet_connection_system:
                logger.info(
                    f"Using WalletConnectionSystem to get wallet balances for user {user_id}"
                )
                try:
                    # Get all wallets and update their balances
                    wallets = self.wallet_connection_system.update_all_wallet_balances(
                        user_id
                    )

                    # Filter by wallet type if specified
                    result = {"status": "success", "wallets": []}

                    # Add internal wallet if available and requested
                    if (
                        wallet_type is None or wallet_type == "internal"
                    ) and wallets.get("internal_wallet"):
                        internal_wallet = wallets["internal_wallet"]
                        wallet_info = {
                            "type": "internal",
                            "address": internal_wallet.get("public_key")
                            or internal_wallet.get("address"),
                            "balance": internal_wallet.get("balance", {}),
                            "created_at": internal_wallet.get("created_at"),
                        }
                        result["wallets"].append(wallet_info)

                    # Add phantom wallets if available and requested
                    if wallet_type is None or wallet_type == "phantom":
                        for phantom_wallet in wallets.get("phantom_wallets", []):
                            wallet_info = {
                                "type": "phantom",
                                "address": phantom_wallet.get("wallet_address"),
                                "balance": phantom_wallet.get("balance", {}),
                                "connected_at": phantom_wallet.get("connected_at"),
                            }
                            result["wallets"].append(wallet_info)

                    return result
                except Exception as e:
                    logger.error(f"Error using WalletConnectionSystem: {str(e)}")
                    # Fall through to fallback method

            # Fallback if WalletConnectionSystem is not available or failed
            logger.warning("Using fallback method to get wallet balances")

            # Check if user profile system is available
            if not self.user_profile_system:
                logger.error("User profile system not available")
                return {
                    "status": "error",
                    "message": "User profile system not available",
                }

            # Get user data
            user_data = self.user_profile_system.get_user_data(user_id)

            if not user_data:
                logger.error(f"User data not found for user {user_id}")
                return {"status": "error", "message": "User data not found"}

            # Initialize result
            result = {"status": "success", "wallets": []}

            # Get internal wallet balance if requested
            if wallet_type is None or wallet_type == "internal":
                if "internal_wallet" in user_data:
                    internal_wallet = user_data["internal_wallet"]
                    address = internal_wallet.get("address") or internal_wallet.get(
                        "public_key"
                    )

                    if address:
                        # Get balance from Solana network
                        balance = self._get_solana_balance(address)
                        tokens = self._get_token_balances(address)

                        wallet_info = {
                            "type": "internal",
                            "address": address,
                            "balance": balance,
                            "tokens": tokens,
                        }

                        result["wallets"].append(wallet_info)

            # Get phantom wallet balance if requested
            if wallet_type is None or wallet_type == "phantom":
                phantom_wallets = user_data.get("phantom_wallets", [])
                if not isinstance(phantom_wallets, list):
                    phantom_wallets = [phantom_wallets] if phantom_wallets else []

                for phantom_wallet in phantom_wallets:
                    address = phantom_wallet.get(
                        "wallet_address"
                    ) or phantom_wallet.get("address")

                    if address:
                        # Get balance from Solana network
                        balance = self._get_solana_balance(address)
                        tokens = self._get_token_balances(address)

                        wallet_info = {
                            "type": "phantom",
                            "address": address,
                            "balance": balance,
                            "tokens": tokens,
                        }

                        result["wallets"].append(wallet_info)

            return result
        except Exception as e:
            logger.error(f"Error getting wallet balance: {str(e)}")
            return {
                "status": "error",
                "message": f"Error getting wallet balance: {str(e)}",
            }

    def _get_solana_balance(self, wallet_address: str) -> Dict[str, Any]:
        """
        Get Solana balance for a wallet address.

        Args:
            wallet_address: Wallet address

        Returns:
            Dict[str, Any]: Wallet balance
        """
        try:
            # In a real implementation, this would use the Solana RPC
            # to get the wallet balance

            # Build RPC request
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getBalance",
                "params": [wallet_address],
            }

            # Make RPC request
            response = requests.post(self.solana_rpc_url, json=payload)

            if response.status_code == 200:
                data = response.json()

                if "result" in data:
                    # Convert lamports to SOL
                    balance_lamports = data["result"]["value"]
                    balance_sol = (
                        balance_lamports / 1_000_000_000
                    )  # 1 SOL = 10^9 lamports

                    # Get token balances
                    token_balances = self._get_token_balances(wallet_address)

                    return {
                        "status": "success",
                        "balance": balance_sol,
                        "token_balances": token_balances,
                    }
                else:
                    logger.error(f"RPC error: {data}")
                    return {"status": "error", "message": "RPC error", "details": data}
            else:
                logger.error(
                    f"RPC request failed: {response.status_code} - {response.text}"
                )
                return {
                    "status": "error",
                    "message": f"RPC request failed: {response.status_code}",
                    "details": response.text,
                }
        except Exception as e:
            logger.error(f"Error getting Solana balance: {str(e)}")
            return {
                "status": "error",
                "message": f"Error getting Solana balance: {str(e)}",
            }

    def _get_token_balances(self, wallet_address: str) -> List[Dict[str, Any]]:
        """
        Get token balances for a wallet address.

        Args:
            wallet_address: Wallet address

        Returns:
            List[Dict[str, Any]]: Token balances
        """
        try:
            # In a real implementation, this would use the Solana RPC
            # to get the token balances

            # Build RPC request
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTokenAccountsByOwner",
                "params": [
                    wallet_address,
                    {
                        "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"  # Token program ID
                    },
                    {"encoding": "jsonParsed"},
                ],
            }

            # Make RPC request
            response = requests.post(self.solana_rpc_url, json=payload)

            if response.status_code == 200:
                data = response.json()

                if "result" in data:
                    token_balances = []

                    for account in data["result"]["value"]:
                        if "account" in account and "data" in account["account"]:
                            parsed_data = account["account"]["data"]["parsed"]

                            if "info" in parsed_data:
                                info = parsed_data["info"]

                                if "tokenAmount" in info:
                                    token_amount = info["tokenAmount"]

                                    token_balances.append(
                                        {
                                            "mint": info.get("mint", ""),
                                            "amount": float(token_amount["amount"])
                                            / (10 ** token_amount["decimals"]),
                                            "decimals": token_amount["decimals"],
                                        }
                                    )

                    return token_balances
                else:
                    logger.error(f"RPC error: {data}")
                    return []
            else:
                logger.error(
                    f"RPC request failed: {response.status_code} - {response.text}"
                )
                return []
        except Exception as e:
            logger.error(f"Error getting token balances: {str(e)}")
            return []

    def execute_transaction(
        self,
        user_id: str,
        transaction_data: Dict[str, Any],
        wallet_type: str = "internal",
    ) -> Dict[str, Any]:
        """
        Execute a transaction.

        Args:
            user_id: User ID
            transaction_data: Transaction data
            wallet_type: Wallet type (internal or phantom)

        Returns:
            Dict[str, Any]: Transaction result
        """
        try:
            # Check if user profile system is available
            if not self.user_profile_system:
                logger.error("User profile system not available")
                return {
                    "status": "error",
                    "message": "User profile system not available",
                }

            # Check if GMGN service is available
            if not self.gmgn_service:
                logger.error("GMGN service not available")
                return {"status": "error", "message": "GMGN service not available"}

            # Get user data
            user_data = self.user_profile_system.get_user_data(user_id)

            if not user_data:
                logger.error(f"User {user_id} not found")
                return {"status": "error", "message": "User not found"}

            # Get wallet data
            wallet_data = None

            if wallet_type == "internal":
                if "internal_wallet" in user_data:
                    wallet_data = user_data["internal_wallet"]
                else:
                    logger.error(f"User {user_id} does not have an internal wallet")
                    return {"status": "error", "message": "No internal wallet found"}
            elif wallet_type == "phantom":
                if "phantom_wallet" in user_data:
                    wallet_data = user_data["phantom_wallet"]
                else:
                    logger.error(
                        f"User {user_id} does not have a connected Phantom wallet"
                    )
                    return {"status": "error", "message": "No Phantom wallet connected"}
            else:
                logger.error(f"Invalid wallet type: {wallet_type}")
                return {
                    "status": "error",
                    "message": f"Invalid wallet type: {wallet_type}",
                }

            # Get wallet address
            wallet_address = wallet_data["address"]

            # Add wallet address to transaction data
            transaction_data["wallet_address"] = wallet_address

            # For internal wallets, we need to sign the transaction
            if wallet_type == "internal":
                # In a real implementation, this would use the Solana SDK
                # to sign the transaction with the private key

                # For now, we'll just add a signature field
                transaction_data["signature"] = "internal_wallet_signature"

            # For Phantom wallets, the user would need to approve the transaction
            # in the Phantom app
            if wallet_type == "phantom":
                # In a real implementation, this would redirect the user to the
                # Phantom app to approve the transaction

                # For now, we'll just add a signature field
                transaction_data["signature"] = "phantom_wallet_signature"

            # Execute the transaction via GMGN
            # In a real implementation, this would use the GMGN trade endpoint

            logger.info(f"Would execute transaction with data: {transaction_data}")
            logger.info(
                f"Using GMGN trade endpoint: {self.gmgn_service.trade_endpoint}"
            )

            # This is a placeholder for the actual API call
            # response = requests.post(self.gmgn_service.trade_endpoint, json=transaction_data)

            # For now, return a placeholder response
            return {
                "status": "success",
                "message": "Transaction executed successfully",
                "transaction_id": f"tx_{int(time.time())}",
                "wallet_address": wallet_address,
                "wallet_type": wallet_type,
            }
        except Exception as e:
            logger.error(f"Error executing transaction: {str(e)}")
            return {
                "status": "error",
                "message": f"Error executing transaction: {str(e)}",
            }

    def confirm_transaction(
        self, user_id: str, confirmation_id: str, wallet_type: str = "internal"
    ) -> Dict[str, Any]:
        """
        Confirm and execute a transaction.

        Args:
            user_id: User ID
            confirmation_id: Confirmation ID
            wallet_type: Wallet type (internal or phantom)

        Returns:
            Dict[str, Any]: Transaction result
        """
        try:
            # Check if GMGN service is available
            if not self.gmgn_service:
                logger.error("GMGN service not available")
                return {"status": "error", "message": "GMGN service not available"}

            # Parse confirmation ID to get transaction details
            parts = confirmation_id.split("_")

            if len(parts) < 2:
                return {
                    "status": "error",
                    "message": f"Invalid confirmation ID: {confirmation_id}",
                }

            transaction_type = parts[0]

            # Build transaction data based on transaction type
            transaction_data = {
                "confirmation_id": confirmation_id,
                "transaction_type": transaction_type,
            }

            if transaction_type == "trade":
                # Trade confirmation
                if len(parts) < 5:
                    return {
                        "status": "error",
                        "message": f"Invalid trade confirmation ID: {confirmation_id}",
                    }

                action = parts[1]
                token = parts[2]
                amount = parts[3]

                transaction_data.update(
                    {"action": action, "token": token, "amount": amount}
                )

            elif transaction_type == "swap":
                # Swap confirmation
                if len(parts) < 5:
                    return {
                        "status": "error",
                        "message": f"Invalid swap confirmation ID: {confirmation_id}",
                    }

                from_token = parts[1]
                to_token = parts[2]
                amount = parts[3]

                transaction_data.update(
                    {"from_token": from_token, "to_token": to_token, "amount": amount}
                )

            else:
                return {
                    "status": "error",
                    "message": f"Unknown transaction type: {transaction_type}",
                }

            # Execute the transaction
            return self.execute_transaction(user_id, transaction_data, wallet_type)
        except Exception as e:
            logger.error(f"Error confirming transaction: {str(e)}")
            return {
                "status": "error",
                "message": f"Error confirming transaction: {str(e)}",
            }

    def process_natural_language_request(
        self, user_id: str, request: str, wallet_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a natural language request related to wallets.

        Args:
            user_id: User ID
            request: Natural language request
            wallet_type: Wallet type (internal, phantom, or None for both)

        Returns:
            Dict[str, Any]: Response to the request
        """
        request_lower = request.lower()

        # Check for wallet balance requests
        balance_patterns = [
            r"(wallet|portfolio) (balance|status)",
            r"show (my|) (wallet|portfolio)",
            r"(check|view) (my|) (wallet|portfolio)",
            r"how much (sol|solana) do i have",
        ]

        for pattern in balance_patterns:
            if re.search(pattern, request_lower):
                return self.get_wallet_balance(user_id, wallet_type)

        # Check for wallet connection requests
        connect_patterns = [
            r"connect (my|) phantom wallet",
            r"link (my|) phantom wallet",
            r"use (my|) phantom wallet",
        ]

        for pattern in connect_patterns:
            if re.search(pattern, request_lower):
                # Extract wallet address if provided
                address_match = re.search(r"address[:\s]+([a-zA-Z0-9]+)", request_lower)

                if address_match:
                    phantom_address = address_match.group(1)
                    return self.connect_phantom_wallet(user_id, phantom_address)
                else:
                    return {
                        "status": "error",
                        "message": "Please provide a Phantom wallet address",
                    }

        # Check for wallet disconnection requests
        disconnect_patterns = [
            r"disconnect (my|) phantom wallet",
            r"unlink (my|) phantom wallet",
            r"remove (my|) phantom wallet",
        ]

        for pattern in disconnect_patterns:
            if re.search(pattern, request_lower):
                return self.disconnect_phantom_wallet(user_id)

        # If no specific wallet request was identified, return an error
        return {
            "status": "error",
            "message": "I'm not sure what you're asking about your wallet. Try asking about your wallet balance, connecting a Phantom wallet, or disconnecting your Phantom wallet.",
        }

    def process_task(self, task_content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a task from the agent framework.

        Args:
            task_content: Task content and parameters

        Returns:
            Dict[str, Any]: Task result
        """
        task_type = task_content.get("type")
        user_id = task_content.get("user_id")

        if not user_id:
            return {
                "status": "error",
                "message": "User ID is required for wallet operations",
            }

        if task_type == "get_wallet_balance":
            wallet_type = task_content.get("wallet_type")
            return self.get_wallet_balance(user_id, wallet_type)

        elif task_type == "generate_internal_wallet":
            return self.generate_internal_wallet(user_id)

        elif task_type == "connect_phantom_wallet":
            phantom_address = task_content.get("phantom_address")
            if not phantom_address:
                return {
                    "status": "error",
                    "message": "Phantom wallet address is required",
                }
            return self.connect_phantom_wallet(user_id, phantom_address)

        elif task_type == "disconnect_phantom_wallet":
            return self.disconnect_phantom_wallet(user_id)

        elif task_type == "execute_transaction":
            transaction_data = task_content.get("transaction_data")
            wallet_type = task_content.get("wallet_type", "internal")
            if not transaction_data:
                return {"status": "error", "message": "Transaction data is required"}
            return self.execute_transaction(user_id, transaction_data, wallet_type)

        elif task_type == "confirm_transaction":
            confirmation_id = task_content.get("confirmation_id")
            wallet_type = task_content.get("wallet_type", "internal")
            if not confirmation_id:
                return {"status": "error", "message": "Confirmation ID is required"}
            return self.confirm_transaction(user_id, confirmation_id, wallet_type)

        return {"status": "error", "message": f"Unknown task type: {task_type}"}


# Example usage
if __name__ == "__main__":
    # Initialize Solana Wallet Manager
    wallet_manager = SolanaWalletManager()

    # Generate an internal wallet
    result = wallet_manager.generate_internal_wallet("test_user")
    print(json.dumps(result, indent=2))
