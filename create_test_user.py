#!/usr/bin/env python3
"""
Quick script to create a test user for Grace project
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.grace_core import GraceCore

def create_test_user():
    """Create a test user for login testing"""
    
    # Initialize Grace core
    config_path = None
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    encryption_key = os.environ.get('FERNET_KEY', None)
    
    grace_instance = GraceCore(
        config_path=config_path,
        data_dir=data_dir,
        encryption_key=encryption_key,
        test_mode=True
    )
    
    # Create test user
    import asyncio
    result = asyncio.run(grace_instance.user_profile_system.create_user(
        username="test_user",
        email="test@example.com",
        password="TestPassword123"
    ))
    
    if result and result.get("success"):
        print(f"✅ Test user created successfully!")
        print(f"Username: test_user")
        print(f"Password: TestPassword123")
        print(f"User ID: {result.get('user_id')}")
    else:
        print(f"❌ Failed to create test user: {result}")
        
    return result

if __name__ == "__main__":
    create_test_user()
