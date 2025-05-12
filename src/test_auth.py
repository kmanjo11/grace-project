"""
Simple test script for authentication endpoints
This script tests the login, logout, and registration functionality
without needing to run the full application.
"""
import requests
import json
import time

# Base URL for the API
BASE_URL = "http://localhost:8000"

def print_separator():
    print("\n" + "="*50 + "\n")

def test_registration(username, email, password):
    print("TESTING REGISTRATION")
    print(f"Registering user: {username}")
    
    url = f"{BASE_URL}/api/auth/register"
    data = {
        "username": username,
        "email": email,
        "password": password
    }
    
    try:
        response = requests.post(url, json=data)
        result = response.json()
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if result.get('success'):
            return result.get('token')
        else:
            print(f"Registration failed: {result.get('message')}")
            return None
    except Exception as e:
        print(f"Error during registration: {str(e)}")
        return None

def test_login(username, password, remember_me=False):
    print("TESTING LOGIN")
    print(f"Logging in user: {username}")
    
    url = f"{BASE_URL}/api/auth/login"
    data = {
        "username": username,
        "password": password,
        "remember_me": remember_me
    }
    
    try:
        response = requests.post(url, json=data)
        result = response.json()
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if result.get('success'):
            return result.get('token')
        else:
            print(f"Login failed: {result.get('message')}")
            return None
    except Exception as e:
        print(f"Error during login: {str(e)}")
        return None

def test_verify_token(token):
    print("TESTING TOKEN VERIFICATION")
    
    url = f"{BASE_URL}/api/auth/verify"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        result = response.json()
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(result, indent=2)}")
        
        return result.get('success', False)
    except Exception as e:
        print(f"Error during token verification: {str(e)}")
        return False

def test_logout(token):
    print("TESTING LOGOUT")
    
    url = f"{BASE_URL}/api/auth/logout"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.post(url, headers=headers)
        result = response.json()
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(result, indent=2)}")
        
        return result.get('success', False)
    except Exception as e:
        print(f"Error during logout: {str(e)}")
        return False

def run_full_auth_test():
    """Run a complete test of the authentication flow"""
    # Generate a unique username for testing
    timestamp = int(time.time())
    test_username = f"test_user_{timestamp}"
    test_email = f"test_{timestamp}@example.com"
    test_password = "TestPassword123!"
    
    print_separator()
    print(f"Starting full authentication test with user: {test_username}")
    print_separator()
    
    # Test registration
    token = test_registration(test_username, test_email, test_password)
    if not token:
        print("Registration failed, skipping remaining tests")
        return
    
    print_separator()
    
    # Test token verification after registration
    success = test_verify_token(token)
    if not success:
        print("Token verification failed after registration")
    
    print_separator()
    
    # Test logout
    success = test_logout(token)
    if not success:
        print("Logout failed")
    
    print_separator()
    
    # Test login
    token = test_login(test_username, test_password, True)
    if not token:
        print("Login failed, skipping remaining tests")
        return
    
    print_separator()
    
    # Test token verification after login
    success = test_verify_token(token)
    if not success:
        print("Token verification failed after login")
    
    print_separator()
    
    # Test final logout
    success = test_logout(token)
    if not success:
        print("Final logout failed")
    
    print_separator()
    print("Authentication test completed")

def run_login_test(username, password):
    """Test just the login functionality with an existing user"""
    print_separator()
    print(f"Testing login for existing user: {username}")
    print_separator()
    
    token = test_login(username, password)
    if not token:
        print("Login failed, skipping remaining tests")
        return
    
    print_separator()
    
    success = test_verify_token(token)
    if not success:
        print("Token verification failed")
    
    print_separator()
    
    success = test_logout(token)
    if not success:
        print("Logout failed")
    
    print_separator()
    print("Login test completed")

if __name__ == "__main__":
    # Choose which test to run
    print("Authentication Test Script")
    print("1. Run full authentication test (register, verify, logout, login, verify, logout)")
    print("2. Test login with existing user")
    
    choice = input("Enter your choice (1 or 2): ")
    
    if choice == "1":
        run_full_auth_test()
    elif choice == "2":
        username = input("Enter username: ")
        password = input("Enter password: ")
        run_login_test(username, password)
    else:
        print("Invalid choice")
