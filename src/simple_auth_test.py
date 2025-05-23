"""
Simple script to test authentication functionality
This doesn't need Quart or Flask - just uses requests to test endpoints
"""

import requests
import json
import time
from datetime import datetime


def print_separator():
    print("\n" + "=" * 50 + "\n")


def test_login():
    """Test login with the existing test_user"""
    print_separator()
    print("TESTING LOGIN WITH EXISTING USER")

    # Using the test user from the JavaScript code
    username = input("Enter username: ")
    password = input("Enter password: ")

    url = "http://localhost:8000/api/auth/login"
    data = {"username": username, "password": password, "remember_me": True}

    try:
        print(f"Sending login request for {username}...")
        print(f"URL: {url}")
        print(f"Data: {json.dumps(data)}")

        response = requests.post(url, json=data)
        print(f"Status code: {response.status_code}")

        try:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")

            if result.get("success"):
                token = result.get("token")
                print(f"Login successful. Token: {token[:10]}...")
                return token
            else:
                print(f"Login failed: {result.get('message', 'Unknown error')}")
                return None
        except json.JSONDecodeError:
            print(f"Could not parse JSON response: {response.text}")
            return None

    except requests.RequestException as e:
        print(f"Request error: {str(e)}")
        return None


def test_token_verify(token):
    """Test token verification"""
    if not token:
        print("No token to verify")
        return

    print_separator()
    print("TESTING TOKEN VERIFICATION")

    url = "http://localhost:8000/api/auth/verify"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        print(f"Sending verify request...")
        print(f"URL: {url}")
        print(f"Headers: {json.dumps(headers)}")

        response = requests.get(url, headers=headers)
        print(f"Status code: {response.status_code}")

        try:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")

            if result.get("success"):
                print("Token verification successful")
                return True
            else:
                print(
                    f"Token verification failed: {result.get('message', 'Unknown error')}"
                )
                return False
        except json.JSONDecodeError:
            print(f"Could not parse JSON response: {response.text}")
            return False

    except requests.RequestException as e:
        print(f"Request error: {str(e)}")
        return False


def test_logout(token):
    """Test logout functionality"""
    if not token:
        print("No token to logout with")
        return

    print_separator()
    print("TESTING LOGOUT")

    url = "http://localhost:8000/api/auth/logout"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        print(f"Sending logout request...")
        print(f"URL: {url}")
        print(f"Headers: {json.dumps(headers)}")

        response = requests.post(url, headers=headers)
        print(f"Status code: {response.status_code}")

        try:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")

            if result.get("success"):
                print("Logout successful")
                print(f"Sessions removed: {result.get('sessions_removed', 0)}")
                return True
            else:
                print(f"Logout failed: {result.get('message', 'Unknown error')}")
                return False
        except json.JSONDecodeError:
            print(f"Could not parse JSON response: {response.text}")
            return False

    except requests.RequestException as e:
        print(f"Request error: {str(e)}")
        return False


def test_register():
    """Test registration of a new user"""
    print_separator()
    print("TESTING USER REGISTRATION")

    # Generate a unique username
    timestamp = int(time.time())
    username = f"test_user_{timestamp}"
    email = f"test_{timestamp}@example.com"
    password = "Test123!"

    print(f"Registering new user:")
    print(f"  Username: {username}")
    print(f"  Email: {email}")
    print(f"  Password: {password}")

    url = "http://localhost:8000/api/auth/register"
    data = {"username": username, "email": email, "password": password}

    try:
        print(f"Sending registration request...")
        print(f"URL: {url}")
        print(f"Data: {json.dumps(data)}")

        response = requests.post(url, json=data)
        print(f"Status code: {response.status_code}")

        try:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")

            if result.get("success"):
                token = result.get("token")
                print(f"Registration successful. Token: {token[:10]}...")
                return (username, password, token)
            else:
                print(f"Registration failed: {result.get('message', 'Unknown error')}")
                return None
        except json.JSONDecodeError:
            print(f"Could not parse JSON response: {response.text}")
            return None

    except requests.RequestException as e:
        print(f"Request error: {str(e)}")
        return None


def main():
    """Main test function"""
    print("AUTH TESTING UTILITY")
    print("====================")
    print("1. Test login with existing user")
    print("2. Test registration, verification, and logout")
    print("3. Full test flow (register, verify, logout, login, verify, logout)")

    choice = input("Enter your choice (1-3): ")

    if choice == "1":
        # Test login and logout with existing user
        token = test_login()
        if token:
            test_token_verify(token)
            test_logout(token)

    elif choice == "2":
        # Test registration
        result = test_register()
        if result:
            username, password, token = result
            test_token_verify(token)
            test_logout(token)

    elif choice == "3":
        # Full flow
        print_separator()
        print("RUNNING FULL AUTH TEST FLOW")

        # Register
        result = test_register()
        if not result:
            print("Registration failed, cannot continue test")
            return

        username, password, token = result

        # Verify token
        if not test_token_verify(token):
            print("Verification failed after registration")

        # Logout
        if not test_logout(token):
            print("Logout failed")

        print("Waiting 2 seconds before login...")
        time.sleep(2)

        # Login with new user
        print(f"Now logging in with newly created user: {username}")
        url = "http://localhost:8000/api/auth/login"
        data = {"username": username, "password": password}

        try:
            response = requests.post(url, json=data)
            result = response.json()

            if result.get("success"):
                token = result.get("token")
                print(f"Login successful. Token: {token[:10]}...")

                # Verify token
                test_token_verify(token)

                # Final logout
                test_logout(token)
            else:
                print(f"Login failed: {result.get('message')}")
        except Exception as e:
            print(f"Error during login test: {str(e)}")

    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()
