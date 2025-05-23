"""
Wallet Connection System for Grace - A crypto trading application based on Open Interpreter

This module implements wallet connection functionality for both internal and Phantom wallets.
"""

import os
import uuid
import base64
import logging
import requests
import hashlib
import secrets
from typing import Dict, List, Optional, Any
from datetime import datetime

from src.config import get_config

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("GraceWalletConnection")


class InternalWalletManager:
    """
    Manages internal wallets for Grace users.
    """

    def __init__(self, secure_data_manager=None):
        """
        Initialize the internal wallet manager.

        Args:
            secure_data_manager: Secure data manager for encryption
        """
        self.secure_data_manager = secure_data_manager
        self.solana_rpc_url = get_config().get("solana_rpc_url")
        self.logger = logging.getLogger("GraceInternalWallet")

    def generate_wallet(self) -> Dict[str, Any]:
        """
        Generate a new Solana wallet.

        Returns:
            Dict: Wallet information
        """
        try:
            # Generate new keypair using standard crypto libraries
            private_key = secrets.token_bytes(32)
            # In a real implementation, this would use ed25519 to derive the public key
            # For now, we'll use a simple hash to simulate the derivation
            public_key_bytes = hashlib.sha256(private_key).digest()
            # Use hex encoding instead of base64 to ensure a clean alphanumeric address
            public_key = public_key_bytes.hex()

            # Encrypt private key if secure data manager is available
            if self.secure_data_manager:
                encrypted_private_key = self.secure_data_manager.encrypt(private_key)
            else:
                # Base64 encode private key if no secure manager
                encrypted_private_key = base64.b64encode(private_key).decode("utf-8")

            # Create wallet data
            wallet_data = {
                "public_key": public_key,
                "encrypted_private_key": encrypted_private_key,
                "balance": {"solana": 0.0, "tether_usd": 0.0},
                "created_at": datetime.now().isoformat(),
                "wallet_type": "internal",
            }

            self.logger.info(f"Generated new internal wallet: {public_key}")
            return wallet_data
        except Exception as e:
            self.logger.error(f"Error generating wallet: {str(e)}")
            raise

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


class PhantomWalletConnector:
    """
    Manages connections to Phantom wallets.
    """

    def __init__(
        self,
        phantom_app_url: str = "https://phantom.app",
        phantom_callback_path: str = "/phantom/callback",
        session_prefix: str = "phantom:session:",
        wallet_prefix: str = "phantom:wallet:",
    ):
        """
        Initialize the Phantom wallet connector.

        Args:
            phantom_app_url: Phantom app URL
            phantom_callback_path: Callback path for Phantom connections
            session_prefix: Prefix for session storage keys
            wallet_prefix: Prefix for wallet storage keys
        """
        self.phantom_app_url = phantom_app_url
        self.phantom_callback_path = phantom_callback_path
        self.session_prefix = session_prefix
        self.wallet_prefix = wallet_prefix
        self.solana_rpc_url = get_config().get("solana_rpc_url")
        self.logger = logging.getLogger("GracePhantomWallet")
        self.sessions = {}
        self.connected_wallets = {}

    def create_connection_session(self) -> Dict[str, Any]:
        """
        Create a new connection session for Phantom wallet.

        Returns:
            Dict: Session information
        """
        try:
            session_id = str(uuid.uuid4())
            session_data = {
                "session_id": session_id,
                "created_at": datetime.now().isoformat(),
                "status": "pending",
                "expires_at": (datetime.now().timestamp() + 3600),  # 1 hour expiry
            }

            # Store session
            self.sessions[f"{self.session_prefix}{session_id}"] = session_data

            self.logger.info(f"Created new Phantom connection session: {session_id}")
            return session_data
        except Exception as e:
            self.logger.error(f"Error creating connection session: {str(e)}")
            raise

    def generate_connection_url(self, session_id: str, redirect_url: str) -> str:
        """
        Generate URL for connecting Phantom wallet.

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

    def verify_session(self, session_id: str) -> bool:
        """
        Verify if a session is valid.

        Args:
            session_id: Session ID

        Returns:
            bool: Session validity
        """
        session_key = f"{self.session_prefix}{session_id}"

        if session_key not in self.sessions:
            return False

        session_data = self.sessions[session_key]

        # Check if session is expired
        if session_data.get("expires_at", 0) < datetime.now().timestamp():
            return False

        # Check if session is pending
        if session_data.get("status") != "pending":
            return False

        return True

    def complete_connection(
        self, session_id: str, wallet_address: str
    ) -> Dict[str, Any]:
        """
        Complete Phantom wallet connection.

        Args:
            session_id: Session ID
            wallet_address: Wallet address

        Returns:
            Dict: Connected wallet information
        """
        try:
            # Verify session
            if not self.verify_session(session_id):
                raise ValueError(f"Invalid or expired session: {session_id}")

            # Update session status
            session_key = f"{self.session_prefix}{session_id}"
            self.sessions[session_key]["status"] = "completed"

            # Create wallet data
            wallet_key = f"{self.wallet_prefix}{wallet_address}"
            wallet_data = {
                "wallet_address": wallet_address,
                "connected_at": datetime.now().isoformat(),
                "status": "connected",
                "wallet_type": "phantom",
                "session_id": session_id,
            }

            # Store wallet data
            self.connected_wallets[wallet_key] = wallet_data

            self.logger.info(f"Completed connection for wallet: {wallet_address}")
            return wallet_data
        except Exception as e:
            self.logger.error(f"Error completing connection: {str(e)}")
            raise

    def get_wallet_balance(self, wallet_address: str) -> Dict[str, float]:
        """
        Get Phantom wallet balance.

        Args:
            wallet_address: Wallet address

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
                "params": [wallet_address],
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
            self.logger.error(f"Error getting Phantom wallet balance: {str(e)}")
            return {"solana": 0.0, "tether_usd": 0.0}

    def disconnect_wallet(self, wallet_address: str) -> bool:
        """
        Disconnect a Phantom wallet.

        Args:
            wallet_address: Wallet address

        Returns:
            bool: Success status
        """
        try:
            wallet_key = f"{self.wallet_prefix}{wallet_address}"

            if wallet_key not in self.connected_wallets:
                return False

            # Remove wallet
            del self.connected_wallets[wallet_key]

            self.logger.info(f"Disconnected wallet: {wallet_address}")
            return True
        except Exception as e:
            self.logger.error(f"Error disconnecting wallet: {str(e)}")
            return False


class WalletConnectionSystem:
    """
    Manages wallet connections for Grace users.
    """

    def __init__(
        self,
        user_profile_system,
        secure_data_manager=None,
        phantom_app_url: str = "https://phantom.app",
        phantom_callback_path: str = "/phantom/callback",
    ):
        """
        Initialize the wallet connection system.

        Args:
            user_profile_system: User profile system
            secure_data_manager: Secure data manager for encryption
            phantom_app_url: Phantom app URL
            phantom_callback_path: Callback path for Phantom connections
        """
        self.user_profile_system = user_profile_system
        self.internal_wallet_manager = InternalWalletManager(secure_data_manager)
        self.phantom_connector = PhantomWalletConnector(
            phantom_app_url, phantom_callback_path
        )
        self.logger = logging.getLogger("GraceWalletConnection")

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
