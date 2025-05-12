"""
User Profile System for Grace - A crypto trading application based on Open Interpreter

This module implements a secure user profile system with:
- User authentication (username/password, email, optional phone number, Gmail)
- Secure profile storage with encryption
- JWT token-based session management
- Integration with memory system
"""

import os
import json
import time
import uuid
import hashlib
import logging
import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta

import bcrypt
import jwt
from cryptography.fernet import Fernet

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("GraceUserProfile")

class SecureDataManager:
    """
    Handles secure storage and encryption of user data.
    """
    
    def __init__(self, encryption_key_file: str = "encryption_key.key"):
        """
        Initialize the secure data manager.
        
        Args:
            encryption_key_file: File to store/retrieve encryption key
        """
        self.encryption_key_file = encryption_key_file
        self.encryption_key = self._get_or_create_key()
        self.cipher_suite = Fernet(self.encryption_key)
        self.logger = logging.getLogger("GraceSecureData")
        self._lock = asyncio.Lock()
    
    def _get_or_create_key(self) -> bytes:
        """
        Get existing encryption key or create a new one.
        
        Returns:
            bytes: Encryption key
        """
        try:
            if os.path.exists(self.encryption_key_file):
                with open(self.encryption_key_file, "rb") as key_file:
                    return key_file.read()
            else:
                # Generate a new key
                key = Fernet.generate_key()
                with open(self.encryption_key_file, "wb") as key_file:
                    key_file.write(key)
                return key
        except Exception as e:
            logger.error(f"Error with encryption key: {str(e)}")
            # Fallback to a derived key if file operations fail
            return Fernet.generate_key()
    
    async def encrypt_data(self, data: str) -> str:
        """
        Encrypt data asynchronously.
        
        Args:
            data: Data to encrypt
            
        Returns:
            str: Encrypted data (base64 encoded)
        """
        async with self._lock:
            try:
                encrypted_data = self.cipher_suite.encrypt(data.encode())
                return encrypted_data.decode()
            except Exception as e:
                self.logger.error(f"Encryption error: {str(e)}")
                raise
    
    async def decrypt_data(self, encrypted_data: str) -> str:
        """
        Decrypt data asynchronously.
        
        Args:
            encrypted_data: Encrypted data to decrypt
            
        Returns:
            str: Decrypted data
        """
        async with self._lock:
            try:
                decrypted_data = self.cipher_suite.decrypt(encrypted_data.encode())
                return decrypted_data.decode()
            except Exception as e:
                self.logger.error(f"Decryption error: {str(e)}")
                raise


class UserProfileManager:
    """
    Manages user profiles, authentication, and session management.
    """
    
    def __init__(
        self, 
        profiles_file: str = "profiles.json",
        jwt_secret: Optional[str] = None,
        token_expiry_days: int = 7
    ):
        """
        Initialize the user profile manager.
        
        Args:
            profiles_file: File to store user profiles
            jwt_secret: Secret for JWT token signing (generated if None)
            token_expiry_days: Days until tokens expire
        """
        self.profiles_file = profiles_file
        self.jwt_secret = jwt_secret or self._generate_jwt_secret()
        self.token_expiry_days = token_expiry_days
        self.secure_data_manager = SecureDataManager()
        self.logger = logging.getLogger("GraceUserProfile")
        self._lock = asyncio.Lock()
        self.profiles = {}
        self._load_profiles()
    
    def _generate_jwt_secret(self) -> str:
        """
        Generate a JWT secret key.
        
        Returns:
            str: JWT secret key
        """
        return str(uuid.uuid4())
    
    def _load_profiles(self):
        """
        Load user profiles from file.
        """
        try:
            if os.path.exists(self.profiles_file):
                with open(self.profiles_file, "r") as f:
                    self.profiles = json.load(f)
            else:
                self.profiles = {}
                self._save_profiles()
        except Exception as e:
            self.logger.error(f"Error loading profiles: {str(e)}")
            self.profiles = {}
    
    async def _save_profiles(self):
        """
        Save user profiles to file asynchronously.
        """
        async with self._lock:
            try:
                with open(self.profiles_file, "w") as f:
                    json.dump(self.profiles, f, indent=2)
            except Exception as e:
                self.logger.error(f"Error saving profiles: {str(e)}")
                raise
    
    async def register_user(
        self,
        username: str,
        password: str,
        email: str,
        phone_number: Optional[str] = None,
        gmail_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Register a new user.
        
        Args:
            username: Username
            password: Password
            email: Email address
            phone_number: Optional phone number
            gmail_id: Optional Gmail ID for OAuth login
            
        Returns:
            Dict: Registration result
        """
        async with self._lock:
            # Check if username or email already exists
            for user_id, user_data in self.profiles.items():
                if user_data.get("username") == username:
                    return {"success": False, "error": "Username already exists"}
                if user_data.get("email") == email:
                    return {"success": False, "error": "Email already exists"}
            
            # Create user ID
            user_id = str(uuid.uuid4())
            
            # Hash password
            hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            
            # Create user profile
            user_profile = {
                "username": username,
                "password": hashed_password,
                "email": email,
                "phone_number": phone_number,
                "gmail_id": gmail_id,
                "created_at": time.time(),
                "last_login": None,
                "settings": {
                    "theme": "light",
                    "notifications_enabled": True
                },
                "wallet_connected": False
            }
            
            # Encrypt sensitive data
            encrypted_profile = await self._encrypt_profile(user_profile)
            
            # Save user profile
            self.profiles[user_id] = encrypted_profile
            await self._save_profiles()
            
            # Generate token
            token = self._generate_token(user_id)
            
            return {
                "success": True,
                "user_id": user_id,
                "token": token,
                "username": username
            }
    
    async def login_user(
        self,
        username_or_email: str,
        password: Optional[str] = None,
        gmail_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Login a user with username/password or Gmail ID.
        
        Args:
            username_or_email: Username or email
            password: Password (required for standard login)
            gmail_id: Gmail ID (required for Gmail login)
            
        Returns:
            Dict: Login result
        """
        # Check login method
        if not password and not gmail_id:
            return {"success": False, "error": "No authentication method provided"}
        
        # Find user
        user_id = None
        user_data = None
        
        for uid, encrypted_profile in self.profiles.items():
            try:
                profile = await self._decrypt_profile(encrypted_profile)
                
                # Check if username or email matches
                if (profile.get("username") == username_or_email or 
                    profile.get("email") == username_or_email):
                    user_id = uid
                    user_data = profile
                    break
                
                # Check Gmail ID if provided
                if gmail_id and profile.get("gmail_id") == gmail_id:
                    user_id = uid
                    user_data = profile
                    break
            except Exception as e:
                self.logger.error(f"Error decrypting profile during login: {str(e)}")
                continue
        
        if not user_id or not user_data:
            return {"success": False, "error": "User not found"}
        
        # Authenticate
        if gmail_id:
            # Gmail authentication
            if user_data.get("gmail_id") != gmail_id:
                return {"success": False, "error": "Invalid Gmail authentication"}
        else:
            # Password authentication
            if not bcrypt.checkpw(password.encode(), user_data["password"].encode()):
                return {"success": False, "error": "Invalid password"}
        
        # Update last login
        user_data["last_login"] = time.time()
        encrypted_profile = await self._encrypt_profile(user_data)
        
        async with self._lock:
            self.profiles[user_id] = encrypted_profile
            await self._save_profiles()
        
        # Generate token
        token = self._generate_token(user_id)
        
        return {
            "success": True,
            "user_id": user_id,
            "token": token,
            "username": user_data["username"]
        }
    
    async def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """
        Get a user's profile.
        
        Args:
            user_id: User ID
            
        Returns:
            Dict: User profile
        """
        if user_id not in self.profiles:
            return {"success": False, "error": "User not found"}
        
        try:
            encrypted_profile = self.profiles[user_id]
            profile = await self._decrypt_profile(encrypted_profile)
            
            # Remove sensitive data
            if "password" in profile:
                del profile["password"]
            
            return {
                "success": True,
                "profile": profile
            }
        except Exception as e:
            self.logger.error(f"Error getting user profile: {str(e)}")
            return {"success": False, "error": "Error retrieving profile"}
    
    async def update_user_profile(
        self,
        user_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update a user's profile.
        
        Args:
            user_id: User ID
            updates: Profile updates
            
        Returns:
            Dict: Update result
        """
        if user_id not in self.profiles:
            return {"success": False, "error": "User not found"}
        
        try:
            encrypted_profile = self.profiles[user_id]
            profile = await self._decrypt_profile(encrypted_profile)
            
            # Handle password update separately
            if "password" in updates:
                new_password = updates["password"]
                hashed_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
                profile["password"] = hashed_password
                del updates["password"]
            
            # Update other fields
            for key, value in updates.items():
                if key not in ["user_id", "created_at"]:  # Protect immutable fields
                    profile[key] = value
            
            # Encrypt and save
            encrypted_profile = await self._encrypt_profile(profile)
            
            async with self._lock:
                self.profiles[user_id] = encrypted_profile
                await self._save_profiles()
            
            return {"success": True}
        except Exception as e:
            self.logger.error(f"Error updating user profile: {str(e)}")
            return {"success": False, "error": "Error updating profile"}
    
    async def delete_user(self, user_id: str) -> Dict[str, Any]:
        """
        Delete a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Dict: Deletion result
        """
        if user_id not in self.profiles:
            return {"success": False, "error": "User not found"}
        
        try:
            async with self._lock:
                del self.profiles[user_id]
                await self._save_profiles()
            
            return {"success": True}
        except Exception as e:
            self.logger.error(f"Error deleting user: {str(e)}")
            return {"success": False, "error": "Error deleting user"}
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify a JWT token.
        
        Args:
            token: JWT token
            
        Returns:
            Dict: Verification result
        """
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            user_id = payload.get("user_id")
            
            if not user_id or user_id not in self.profiles:
                return {"success": False, "error": "Invalid token"}
            
            return {
                "success": True,
                "user_id": user_id
            }
        except jwt.ExpiredSignatureError:
            return {"success": False, "error": "Token expired"}
        except jwt.InvalidTokenError:
            return {"success": False, "error": "Invalid token"}
        except Exception as e:
            self.logger.error(f"Error verifying token: {str(e)}")
            return {"success": False, "error": "Error verifying token"}
    
    def _generate_token(self, user_id: str) -> str:
        """
        Generate a JWT token for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            str: JWT token
        """
        expiry = datetime.utcnow() + timedelta(days=self.token_expiry_days)
        payload = {
            "user_id": user_id,
            "exp": expiry
        }
        token = jwt.encode(payload, self.jwt_secret, algorithm="HS256")
        return token
    
    async def _encrypt_profile(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Encrypt sensitive fields in a user profile.
        
        Args:
            profile: User profile
            
        Returns:
            Dict: Profile with encrypted sensitive fields
        """
        encrypted_profile = profile.copy()
        
        # Encrypt sensitive fields
        sensitive_fields = ["password", "email", "phone_number", "gmail_id"]
        
        for field in sensitive_fields:
            if field in encrypted_profile and encrypted_profile[field]:
                encrypted_profile[field] = await self.secure_data_manager.encrypt_data(
                    str(encrypted_profile[field])
                )
        
        return encrypted_profile
    
    async def _decrypt_profile(self, encrypted_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decrypt sensitive fields in an encrypted user profile.
        
        Args:
            encrypted_profile: Encrypted user profile
            
        Returns:
            Dict: Decrypted user profile
        """
        decrypted_profile = encrypted_profile.copy()
        
        # Decrypt sensitive fields
        sensitive_fields = ["password", "email", "phone_number", "gmail_id"]
        
        for field in sensitive_fields:
            if field in decrypted_profile and decrypted_profile[field]:
                decrypted_profile[field] = await self.secure_data_manager.decrypt_data(
                    decrypted_profile[field]
                )
        
        return decrypted_profile


class UserSessionManager:
    """
    Manages user sessions and integrates with memory system.
    """
    
    def __init__(
        self,
        user_profile_manager: UserProfileManager,
        memory_system_initializer = None  # Function to initialize memory system
    ):
        """
        Initialize the user session manager.
        
        Args:
            user_profile_manager: UserProfileManager instance
            memory_system_initializer: Function to initialize memory system
        """
        self.user_profile_manager = user_profile_manager
        self.memory_system_initializer = memory_system_initializer
        self.active_sessions = {}
        self.logger = logging.getLogger("GraceUserSession")
        self._lock = asyncio.Lock()
    
    async def create_session(self, token: str) -> Dict[str, Any]:
        """
        Create a new user session.
        
        Args:
            token: JWT token
            
        Returns:
            Dict: Session creation result
        """
        # Verify token
        verification = self.user_profile_manager.verify_token(token)
        
        if not verification["success"]:
            return verification
        
        user_id = verification["user_id"]
        
        # Get user profile
        profile_result = await self.user_profile_manager.get_user_profile(user_id)
        
        if not profile_result["success"]:
            return profile_result
        
        username = profile_result["profile"]["username"]
        
        # Create session ID
        session_id = str(uuid.uuid4())
        
        # Initialize memory system if provided
        memory_components = None
        if self.memory_system_initializer:
            try:
                memory_components = await self.memory_system_initializer()
            except Exception as e:
                self.logger.error(f"Error initializing memory system: {str(e)}")
        
        # Create session
        session = {
            "user_id": user_id,
            "username": username,
            "created_at": time.time(),
            "last_activity": time.time(),
            "memory_components": memory_components
        }
        
        # Store session
        async with self._lock:
            self.active_sessions[session_id] = session
        
        return {
            "success": True,
            "session_id": session_id,
            "username": username
        }
    
    async def get_session(self, session_id: str) -> Dict[str, Any]:
        """
        Get a user session.
        
        Args:
            session_id: Session ID
            
        Returns:
            Dict: Session data
        """
        if session_id not in self.active_sessions:
            return {"success": False, "error": "Session not found"}
        
        session = self.active_sessions[session_id]
        
        # Update last activity
        session["last_activity"] = time.time()
        
        return {
            "success": True,
            "session": session
        }
    
    async def end_session(self, session_id: str) -> Dict[str, Any]:
        """
        End a user session.
        
        Args:
            session_id: Session ID
            
        Returns:
            Dict: Session end result
        """
        if session_id not in self.active_sessions:
            return {"success": False, "error": "Session not found"}
        
        # Remove session
        async with self._lock:
            del self.active_sessions[session_id]
        
        return {"success": True}
    
    async def cleanup_inactive_sessions(self, max_inactive_time: int = 3600) -> int:
        """
        Clean up inactive sessions.
        
        Args:
            max_inactive_time: Maximum inactive time in seconds
            
        Returns:
            int: Number of sessions cleaned up
        """
        current_time = time.time()
        sessions_to_remove = []
        
        # Find inactive sessions
        for session_id, session in self.active_sessions.items():
            if current_time - session["last_activity"] > max_inactive_time:
                sessions_to_remove.append(session_id)
        
        # Remove inactive sessions
        async with self._lock:
            for session_id in sessions_to_remove:
                del self.active_sessions[session_id]
        
        return len(sessions_to_remove)


# Initialize the user profile system
async def create_user_profile_system(
    profiles_file: str = "profiles.json",
    memory_system_initializer = None
):
    """
    Create and initialize the complete user profile system.
    
    Args:
        profiles_file: File to store user profiles
        memory_system_initializer: Function to initialize memory system
        
    Returns:
        Tuple: (UserProfileManager, UserSessionManager)
    """
    user_profile_manager = UserProfileManager(profiles_file)
    user_session_manager = UserSessionManager(user_profile_manager, memory_system_initializer)
    
    return user_profile_manager, user_session_manager
