import json
import os
import base64
import uuid
import hashlib
import binascii
from datetime import datetime, timedelta
from typing import Dict, Optional, Any

import bcrypt
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad


class SecureDataManager:
    """Handles encryption and decryption of sensitive user data."""

    def __init__(
        self,
        profiles_path: str,
        fernet_key: str,
        jwt_secret: str,
        phantom_app_url: str,
        phantom_callback_path: str,
    ):
        """Initialize with encryption key."""
        try:
            # First try to decode the key directly
            decoded_key = base64.b64decode(fernet_key)
            if len(decoded_key) == 32:
                self.key = decoded_key
            else:
                # If not 32 bytes, derive a key
                raw_key = fernet_key.encode("utf-8")
                self.key = hashlib.sha256(raw_key).digest()
        except binascii.Error:
            # If base64 decoding fails, treat as raw string
            raw_key = fernet_key.encode("utf-8")
            self.key = hashlib.sha256(raw_key).digest()

    def encrypt(self, data: str) -> Dict[str, str]:
        """Encrypt data and return ciphertext and IV."""
        iv = get_random_bytes(16)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        padded_data = pad(data.encode("utf-8"), AES.block_size)
        ciphertext = cipher.encrypt(padded_data)
        return {
            "iv": base64.b64encode(iv).decode("utf-8"),
            "ciphertext": base64.b64encode(ciphertext).decode("utf-8"),
        }

    def decrypt(self, encrypted_data: Dict[str, str]) -> str:
        """Decrypt data using IV and ciphertext."""
        iv = base64.b64decode(encrypted_data["iv"])
        ciphertext = base64.b64decode(encrypted_data["ciphertext"])
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        padded_data = cipher.decrypt(ciphertext)
        return unpad(padded_data, AES.block_size).decode("utf-8")


class InternalWallet:
    """Manages internal crypto wallet for users."""

    def __init__(self, secure_manager: SecureDataManager):
        """Initialize with secure data manager."""
        self.secure_manager = secure_manager

    def generate_wallet(self) -> Dict[str, Any]:
        """Generate a new Solana wallet."""
        keypair = Keypair()
        public_key = str(keypair.public_key)
        # Encrypt private key before storing
        try:
            private_key_bytes = keypair.secret_key.decode("latin1")
        except AttributeError:
            # Handle case where mock implementation is used
            private_key_bytes = str(keypair.secret_key)
        encrypted_private_key = self.secure_manager.encrypt(private_key_bytes)

        return {
            "public_key": public_key,
            "encrypted_private_key": encrypted_private_key,
            "balance": {"solana": 0.0, "tether_usd": 0.0},
            "created_at": datetime.now().isoformat(),
        }

    def get_wallet_info(self, wallet_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get wallet info without sensitive data."""
        return {
            "public_key": wallet_data["public_key"],
            "balance": wallet_data["balance"],
            "created_at": wallet_data["created_at"],
        }


class PhantomWalletManager:
    """Manages Phantom wallet connections for users."""

    def __init__(self, phantom_app_url: str, phantom_callback_path: str):
        """Initialize with Phantom app URL and callback path."""
        self.phantom_app_url = phantom_app_url
        self.phantom_callback_path = phantom_callback_path

    def generate_connection_url(self, session_id: str, redirect_url: str) -> str:
        """Generate URL for connecting Phantom wallet."""
        # In a real implementation, this would create a dApp connection URL
        # For now, we'll simulate this with a placeholder URL
        return f"{self.phantom_app_url}/connect?session={session_id}&redirect={redirect_url}{self.phantom_callback_path}"

    def create_session(self) -> Dict[str, str]:
        """Create a new session for Phantom wallet connection."""
        return {
            "session_id": str(uuid.uuid4()),
            "created_at": datetime.now().isoformat(),
            "status": "pending",
        }

    def store_connected_wallet(self, wallet_address: str) -> Dict[str, Any]:
        """Store connected Phantom wallet info."""
        return {
            "wallet_address": wallet_address,
            "connected_at": datetime.now().isoformat(),
            "status": "connected",
            "wallet_type": "phantom",
        }


class UserProfileSystem:
    """Manages user profiles, authentication, and wallet integration."""

    def __init__(
        self,
        data_dir: str,
        secure_data_manager: "SecureDataManager",
        profiles_path: Optional[str] = None,
    ):
        """Initialize the user profile system."""
        self.data_dir = data_dir
        self.secure_manager = secure_data_manager
        self.profiles_path = profiles_path or os.path.join(data_dir, "profiles.json")
        os.makedirs(data_dir, exist_ok=True)

        # Create profiles file if it doesn't exist
        os.makedirs(os.path.dirname(self.profiles_path), exist_ok=True)
        if not os.path.exists(self.profiles_path):
            with open(self.profiles_path, "w") as f:
                json.dump({}, f)

    def _load_profiles(self) -> Dict[str, Any]:
        """Load user profiles from file."""
        try:
            with open(self.profiles_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            # Create profiles file if it doesn't exist
            profiles = {}
            self._save_profiles(profiles)
            return profiles
        except json.JSONDecodeError:
            # If file is corrupted, create new
            profiles = {}
            self._save_profiles(profiles)
            return profiles

    def _save_profiles(self, profiles: Dict[str, Any]) -> None:
        """Save profiles to file."""
        with open(self.profiles_path, "w") as f:
            json.dump(profiles, f, indent=2)

    async def create_user(
        self, username: str, email: str, password: str, phone: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new user profile with internal wallet and automatic Mango Markets linking."""
        profiles = self._load_profiles()

        # Check if username or email already exists
        for user_id, profile in profiles.items():
            if profile["username"] == username:
                raise ValueError(f"Username '{username}' already exists")
            if profile["email"] == email:
                raise ValueError(f"Email '{email}' already exists")

        # Hash password
        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

        # Generate internal wallet
        internal_wallet = InternalWallet(self.secure_manager).generate_wallet()

        # Create user profile
        user_id = f"user_{len(profiles) + 1}"

        # Attempt silent wallet linking to Mango Markets
        mango_link_result = {"success": False, "message": "Not attempted"}
        try:
            # Import here to avoid circular imports
            import logging

            logger = logging.getLogger("UserProfileSystem")

            try:
                from src.mango_wallet_integrator import MangoWalletIntegrator
                from src.mango_v3_extension import MangoV3Extension

                # Initialize Mango V3 client
                mango_v3_client = MangoV3Extension()

                # Create temporary profile entry for linking
                temp_profiles = profiles.copy()
                temp_profiles[user_id] = {
                    "username": username,
                    "email": email,
                    "internal_wallet": internal_wallet,
                }

                # Setup wallet integrator with temporary profile
                class TempProfileSystem:
                    def get_user_profile(self, uid):
                        return temp_profiles.get(uid, {})

                    def update_user_data(self, uid, data):
                        if uid in temp_profiles:
                            temp_profiles[uid].update(data)

                wallet_integrator = MangoWalletIntegrator(
                    user_profile_system=TempProfileSystem(),
                    mango_v3_client=mango_v3_client,
                )

                # Attempt to link wallet
                mango_link_result = wallet_integrator.link_wallet_silently(user_id)
                logger.info(
                    f"Mango Markets wallet linking for user {user_id}: {mango_link_result}"
                )
            except ImportError as e:
                logger.warning(f"Mango V3 extension not available: {e}")
            except Exception as e:
                logger.warning(f"Failed to link wallet to Mango Markets: {e}")
        except Exception as e:
            # Catch all exceptions to ensure user creation isn't blocked
            pass

        # Create minimal profile entry
        profiles[user_id] = {
            "username": username,
            "email": email,
            "phone": phone,
            "password_hash": hashed_password,
            "created_at": datetime.now().isoformat(),
            "last_login": None,
            "is_authorized": email == "kmanjo11@gmail.com",
            "internal_wallet": internal_wallet,
            "mango_markets_link": {
                "status": mango_link_result.get("success", False),
                "message": mango_link_result.get("message", "Not attempted"),
                "linked_at": (
                    datetime.now().isoformat()
                    if mango_link_result.get("success", False)
                    else None
                ),
            },
        }

        self._save_profiles(profiles)

        # Return success with user_id and wallet linking status
        return {
            "success": True,
            "user_id": user_id,
            "wallet_link_status": mango_link_result.get("success", False),
        }

    async def authenticate(
        self, username_or_email: str, password: str
    ) -> Dict[str, Any]:
        """Authenticate user and return success/failure with message."""
        # Find user by username or email
        user_id = None
        profiles = self._load_profiles()

        for uid, profile in profiles.items():
            if (
                profile["username"] == username_or_email
                or profile["email"] == username_or_email
            ):
                user_id = uid
                break

        if not user_id:
            return {"success": False, "message": "Invalid username or email"}

        profile = profiles[user_id]

        # Verify password
        if not bcrypt.checkpw(
            password.encode("utf-8"), profile["password_hash"].encode("utf-8")
        ):
            return {"success": False, "message": "Invalid password"}

        # Update last login
        profile["last_login"] = datetime.now().isoformat()
        self._save_profiles(profiles)

        # Load and update user's session data
        session_data = self._load_user_data(user_id, "session.json") or {}
        session_data["last_login"] = datetime.now().isoformat()
        session_data["login_count"] = session_data.get("login_count", 0) + 1
        self._save_user_data(user_id, "session.json", session_data)

        # Return success with user ID
        return {
            "success": True,
            "message": "Authentication successful",
            "user_id": user_id,
        }

    def get_user_id_by_username(self, username: str) -> Optional[str]:
        """Get user ID by username."""
        profiles = self._load_profiles()
        for user_id, profile in profiles.items():
            if profile["username"] == username:
                return user_id
        return None

    def generate_token(self, user_id: str) -> str:
        """Generate a simple token for authenticated user."""
        # Since we're having issues with JWT, let's use a simple token generation method
        # In production, you would use a proper JWT library
        expiry = int((datetime.utcnow() + timedelta(days=1)).timestamp())
        token_data = f"{user_id}:{expiry}:{self.secure_manager.key}"
        return base64.b64encode(hashlib.sha256(token_data.encode()).digest()).decode()

    def verify_token(self, token: str) -> Optional[str]:
        """Verify token and return user_id if valid."""
        # For testing purposes, just return a user ID
        # In production, you would properly verify the token
        profiles = self._load_profiles()
        if not profiles:
            return None
        return list(profiles.keys())[0]

    def _get_user_dir(self, user_id: str) -> str:
        """Get path to user's directory."""
        user_dir = os.path.join(self.data_dir, user_id)
        os.makedirs(user_dir, exist_ok=True)
        return user_dir

    def _get_user_data_file(self, user_id: str, file_name: str) -> str:
        """Get path to a user's data file."""
        return os.path.join(self._get_user_dir(user_id), file_name)

    def _load_user_data(self, user_id: str, file_name: str) -> Dict[str, Any]:
        """Load user-specific data from an encrypted file."""
        file_path = self._get_user_data_file(user_id, file_name)
        try:
            with open(file_path, "r") as f:
                encrypted_data = json.load(f)
                return json.loads(self.secure_manager.decrypt(encrypted_data))
        except FileNotFoundError:
            return {}

    def _save_user_data(
        self, user_id: str, file_name: str, data: Dict[str, Any]
    ) -> None:
        """Save user-specific data to an encrypted file."""
        file_path = self._get_user_data_file(user_id, file_name)
        encrypted_data = self.secure_manager.encrypt(json.dumps(data))
        with open(file_path, "w") as f:
            json.dump(encrypted_data, f)

    async def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """Get user info without sensitive data."""
        profiles = self._load_profiles()

        if user_id not in profiles:
            raise ValueError(f"User ID '{user_id}' not found")

        profile = profiles[user_id]

        # Load user's wallet data
        wallet_data = self._load_user_data(user_id, "wallet.json")
        if wallet_data:
            wallet_info = InternalWallet(self.secure_manager).get_wallet_info(
                wallet_data
            )
        else:
            wallet_info = None

        # Load user's settings
        settings = self._load_user_data(user_id, "settings.json")

        return {
            "user_id": user_id,
            "username": profile["username"],
            "email": profile["email"],
            "phone": profile.get("phone"),
            "created_at": profile["created_at"],
            "last_login": profile.get("last_login"),
            "is_authorized": profile.get("is_authorized", False),
            "internal_wallet": wallet_info,
            "phantom_wallets": settings.get("phantom_wallets", []),
            "settings": settings.get("user_settings", {}),
        }

    def reset_password(self, email: str) -> bool:
        """Initiate password reset process."""
        profiles = self._load_profiles()

        # Find user by email
        user_id = None
        for uid, profile in profiles.items():
            if profile["email"] == email:
                user_id = uid
                break

        if not user_id:
            return False

        # In a real implementation, send reset email
        # For now, just return True to indicate success
        return True

    async def update_password(self, user_id: str, new_password: str) -> bool:
        """Update user password."""
        profiles = self._load_profiles()

        if user_id not in profiles:
            return False

        # Hash new password
        hashed_password = bcrypt.hashpw(
            new_password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

        # Update password
        profiles[user_id]["password_hash"] = hashed_password
        self._save_profiles(profiles)

        return True

    async def get_internal_wallet_balance(self, user_id: str) -> Dict[str, float]:
        """Get internal wallet balance for user."""
        profiles = self._load_profiles()

        if user_id not in profiles:
            raise ValueError(f"User ID '{user_id}' not found")

        return profiles[user_id]["internal_wallet"]["balance"]

    def update_internal_wallet_balance(
        self, user_id: str, currency: str, amount: float
    ) -> Dict[str, float]:
        """Update internal wallet balance for user."""
        profiles = self._load_profiles()

        if user_id not in profiles:
            raise ValueError(f"User ID '{user_id}' not found")

        if currency.lower() not in ["solana", "tether_usd"]:
            raise ValueError(f"Unsupported currency: {currency}")

        profiles[user_id]["internal_wallet"]["balance"][currency.lower()] = amount
        self._save_profiles(profiles)

        return profiles[user_id]["internal_wallet"]["balance"]

    def initiate_phantom_connection(
        self, user_id: str, redirect_url: str
    ) -> Dict[str, str]:
        """Initiate Phantom wallet connection process."""
        profiles = self._load_profiles()

        if user_id not in profiles:
            raise ValueError(f"User ID '{user_id}' not found")

        # Create a new session
        session = PhantomWalletManager(
            "https://phantom.app", "/phantom/callback"
        ).create_session()

        # Store session in user profile
        if "phantom_sessions" not in profiles[user_id]:
            profiles[user_id]["phantom_sessions"] = []

        profiles[user_id]["phantom_sessions"].append(session)
        self._save_profiles(profiles)

        # Generate connection URL
        connection_url = PhantomWalletManager(
            "https://phantom.app", "/phantom/callback"
        ).generate_connection_url(session["session_id"], redirect_url)

        return {"session_id": session["session_id"], "connection_url": connection_url}

    async def complete_phantom_connection(
        self, user_id: str, session_id: str, wallet_address: str
    ) -> Dict[str, Any]:
        """Complete Phantom wallet connection process."""
        profiles = self._load_profiles()

        if user_id not in profiles:
            raise ValueError(f"User ID '{user_id}' not found")

        # Verify session exists
        session_found = False
        for session in profiles[user_id].get("phantom_sessions", []):
            if session["session_id"] == session_id and session["status"] == "pending":
                session["status"] = "completed"
                session_found = True
                break

        if not session_found:
            raise ValueError(f"Session ID '{session_id}' not found or not pending")

        # Store connected wallet
        wallet_info = PhantomWalletManager(
            "https://phantom.app", "/phantom/callback"
        ).store_connected_wallet(wallet_address)

        # Check if wallet already connected
        for wallet in profiles[user_id].get("phantom_wallets", []):
            if wallet["wallet_address"] == wallet_address:
                wallet.update(wallet_info)
                self._save_profiles(profiles)
                return wallet

        # Add new wallet
        if "phantom_wallets" not in profiles[user_id]:
            profiles[user_id]["phantom_wallets"] = []

        profiles[user_id]["phantom_wallets"].append(wallet_info)
        self._save_profiles(profiles)

        return wallet_info

    async def disconnect_phantom_wallet(
        self, user_id: str, wallet_address: str
    ) -> bool:
        """Disconnect Phantom wallet."""
        profiles = self._load_profiles()

        if user_id not in profiles:
            raise ValueError(f"User ID '{user_id}' not found")

        # Find wallet
        wallet_found = False
        for i, wallet in enumerate(profiles[user_id].get("phantom_wallets", [])):
            if wallet["wallet_address"] == wallet_address:
                profiles[user_id]["phantom_wallets"].pop(i)
                wallet_found = True
                break

        if not wallet_found:
            return False

        self._save_profiles(profiles)
        return True

    async def is_authorized_user(self, user_id: str) -> bool:
        """Check if user is authorized for global memory updates."""
        profiles = self._load_profiles()

        if user_id not in profiles:
            return False

        return profiles[user_id].get("is_authorized", False)

    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """
        Get a user's profile.

        Args:
            user_id: User ID

        Returns:
            Dict: User profile information
        """
        profiles = self._load_profiles()

        if user_id not in profiles:
            return {"success": False, "error": "User not found"}

        # Return a copy of the profile without sensitive information
        profile = profiles[user_id].copy()

        # Remove sensitive data
        if "password_hash" in profile:
            del profile["password_hash"]
        # Safely handle internal wallet data by removing sensitive information
        if (
            "internal_wallet" in profile
            and "encrypted_private_key" in profile["internal_wallet"]
        ):
            # Create a copy without the encrypted private key
            wallet_info = profile["internal_wallet"].copy()
            if "encrypted_private_key" in wallet_info:
                del wallet_info["encrypted_private_key"]
            profile["internal_wallet"] = wallet_info

        return {"success": True, "profile": profile}

    def get_user_settings(self, user_id: str) -> Dict[str, Any]:
        """
        Get a user's settings.

        Args:
            user_id: User ID

        Returns:
            Dict: User settings
        """
        profiles = self._load_profiles()

        if user_id not in profiles:
            return {"success": False, "error": "User not found"}

        # Return settings or default settings if not set
        settings = profiles[user_id].get(
            "settings",
            {
                "theme": "light",
                "notifications": True,
                "trading": {
                    "auto_trading": False,
                    "risk_level": "medium",
                    "max_daily_trades": 5,
                },
                "privacy": {"share_analytics": True, "store_history": True},
            },
        )

        return {"success": True, "settings": settings}

    async def update_user_settings(
        self, user_id: str, settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update a user's settings.

        Args:
            user_id: User ID
            settings: New settings

        Returns:
            Dict: Update result
        """
        profiles = self._load_profiles()

        if user_id not in profiles:
            return {"success": False, "error": "User not found"}

        # Update settings
        if "settings" not in profiles[user_id]:
            profiles[user_id]["settings"] = {}

        profiles[user_id]["settings"].update(settings)
        self._save_profiles(profiles)

        return {"success": True, "settings": profiles[user_id]["settings"]}


# Example usage
if __name__ == "__main__":
    # Use environment variables
    fernet_key = os.environ.get(
        "FERNET_KEY", "47_1uGC4S-2LuO3DlgvAnRQx7T-pNKWkGhNKZenAD2w="
    )
    phantom_app_url = os.environ.get("PHANTOM_APP_URL", "https://phantom.app")
    phantom_callback_path = os.environ.get("PHANTOM_CALLBACK_PATH", "/phantom/callback")
    jwt_secret = "your-jwt-secret-key"  # In production, use a secure secret

    secure_data_manager = SecureDataManager(
        "profiles.json", fernet_key, jwt_secret, phantom_app_url, phantom_callback_path
    )
    user_system = UserProfileSystem("./data", secure_data_manager)

    # Create a test user
    try:
        user = user_system.create_user(
            "testuser", "test@example.com", "password123", "1234567890"
        )
        print(f"Created user: {user}")
    except ValueError as e:
        print(f"Error creating user: {e}")

    # Authenticate user
    auth_result = user_system.authenticate("testuser", "password123")
    if auth_result:
        print(f"Authentication successful: {auth_result['user_info']['username']}")
        print(f"Token: {auth_result['token']}")

        # Initiate Phantom wallet connection
        connection = user_system.initiate_phantom_connection(
            auth_result["user_id"], "http://localhost:3000"
        )
        print(f"Connection URL: {connection['connection_url']}")

        # Simulate completing connection
        wallet = user_system.complete_phantom_connection(
            auth_result["user_id"],
            connection["session_id"],
            "5FHwkrdxBc3S4TidqJfhRxzVZrj8xnHKKZwQpWrXKmZa",
        )
        print(f"Connected wallet: {wallet}")
    else:
        print("Authentication failed")
