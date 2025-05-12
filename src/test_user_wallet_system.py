"""
Test script for Grace's user profile and wallet connection systems.

This script tests the functionality of:
1. User profile creation and authentication
2. Password recovery
3. Internal wallet generation
4. Phantom wallet connection
"""

import os
import sys
import json
import logging
from datetime import datetime

from src.config import get_config
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("GraceTest")

# Import user profile and wallet connection systems
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from user_profile import UserProfileSystem
from password_recovery import PasswordRecoverySystem

def test_user_profile_system():
    """Test user profile system functionality."""
    logger.info("Testing user profile system...")
    
    # Use environment variables or defaults
    fernet_key = os.environ.get('FERNET_KEY', '47_1uGC4S-2LuO3DlgvAnRQx7T-pNKWkGhNKZenAD2w=')
    phantom_app_url = os.environ.get('PHANTOM_APP_URL', 'https://phantom.app')
    phantom_callback_path = os.environ.get('PHANTOM_CALLBACK_PATH', '/phantom/callback')
    jwt_secret = "test-jwt-secret-key"
    test_profiles_path = "test_profiles.json"
    
    # Remove test profiles file if it exists
    if os.path.exists(test_profiles_path):
        os.remove(test_profiles_path)
    
    # Initialize user profile system
    user_system = UserProfileSystem(
        test_profiles_path,
        fernet_key,
        jwt_secret,
        phantom_app_url,
        phantom_callback_path
    )
    
    # Test user creation
    try:
        logger.info("Creating test user...")
        user = user_system.create_user('testuser', 'test@example.com', 'password123', '1234567890')
        logger.info(f"Created user: {user['username']}")
        
        # Test authentication
        logger.info("Testing authentication...")
        auth_result = user_system.authenticate('testuser', 'password123')
        
        if auth_result:
            logger.info(f"Authentication successful for user: {auth_result['user_info']['username']}")
            user_id = auth_result['user_id']
            token = auth_result['token']
            
            # Test token verification
            logger.info("Testing token verification...")
            verification = user_system.verify_token(token)
            
            if verification:
                logger.info("Token verification successful")
            else:
                logger.error("Token verification failed")
                return False
            
            # Test getting user info
            logger.info("Testing get user info...")
            user_info = user_system.get_user_info(user_id)
            logger.info(f"User info retrieved: {user_info['username']}")
            
            # Test updating password
            logger.info("Testing password update...")
            update_result = user_system.update_password(user_id, 'newpassword123')
            
            if update_result:
                logger.info("Password update successful")
                
                # Test authentication with new password
                auth_result = user_system.authenticate('testuser', 'newpassword123')
                
                if auth_result:
                    logger.info("Authentication with new password successful")
                else:
                    logger.error("Authentication with new password failed")
                    return False
            else:
                logger.error("Password update failed")
                return False
            
            # Test Phantom wallet connection
            logger.info("Testing Phantom wallet connection...")
            connection = user_system.initiate_phantom_connection(user_id, 'http://localhost:3000')
            logger.info(f"Connection initiated with session ID: {connection['session_id']}")
            
            wallet = user_system.complete_phantom_connection(
                user_id, connection['session_id'], '5FHwkrdxBc3S4TidqJfhRxzVZrj8xnHKKZwQpWrXKmZa')
            logger.info(f"Phantom wallet connected: {wallet['wallet_address']}")
            
            # Test disconnecting Phantom wallet
            logger.info("Testing Phantom wallet disconnection...")
            disconnect_result = user_system.disconnect_phantom_wallet(
                user_id, '5FHwkrdxBc3S4TidqJfhRxzVZrj8xnHKKZwQpWrXKmZa')
            
            if disconnect_result:
                logger.info("Phantom wallet disconnection successful")
            else:
                logger.error("Phantom wallet disconnection failed")
                return False
            
            logger.info("User profile system tests passed")
            return True
        else:
            logger.error("Authentication failed")
            return False
    except Exception as e:
        logger.error(f"Error testing user profile system: {str(e)}")
        return False

def test_password_recovery_system():
    """Test password recovery system functionality."""
    logger.info("Testing password recovery system...")
    
    # Use environment variables or defaults
    test_recovery_tokens_file = "test_recovery_tokens.json"
    
    # Remove test recovery tokens file if it exists
    if os.path.exists(test_recovery_tokens_file):
        os.remove(test_recovery_tokens_file)
    
    # Initialize password recovery system
    recovery_system = PasswordRecoverySystem(
        recovery_tokens_file=test_recovery_tokens_file,
        token_expiry_hours=24
    )
    
    try:
        # Generate recovery token
        logger.info("Generating recovery token...")
        token = recovery_system.generate_recovery_token(
            'test_user_id',
            'test@example.com'
        )
        logger.info(f"Generated token: {token}")
        
        # Verify token
        logger.info("Verifying token...")
        verification = recovery_system.verify_recovery_token(token)
        
        if verification['valid']:
            logger.info("Token verification successful")
            
            # Mark token as used
            logger.info("Marking token as used...")
            result = recovery_system.mark_token_used(token)
            
            if result:
                logger.info("Token marked as used successfully")
                
                # Verify token again (should fail)
                verification = recovery_system.verify_recovery_token(token)
                
                if not verification['valid'] and verification['error'] == 'Token already used':
                    logger.info("Used token verification correctly failed")
                else:
                    logger.error("Used token verification should have failed")
                    return False
            else:
                logger.error("Failed to mark token as used")
                return False
            
            logger.info("Password recovery system tests passed")
            return True
        else:
            logger.error(f"Token verification failed: {verification['error']}")
            return False
    except Exception as e:
        logger.error(f"Error testing password recovery system: {str(e)}")
        return False

def run_all_tests():
    """Run all tests and report results."""
    logger.info("Starting Grace user profile and wallet connection tests...")
    
    results = {
        "user_profile_system": test_user_profile_system(),
        "password_recovery_system": test_password_recovery_system()
    }
    
    # Report results
    logger.info("Test results:")
    for test_name, result in results.items():
        status = "PASSED" if result else "FAILED"
        logger.info(f"{test_name}: {status}")
    
    # Overall result
    if all(results.values()):
        logger.info("All tests PASSED - Grace is alive!")
        return True
    else:
        logger.error("Some tests FAILED - Grace needs attention!")
        return False

if __name__ == "__main__":
    run_all_tests()
