#!/bin/bash

# Grace Project Integration Test Script
# This script tests the integration of all Grace components

# Set the working directory to the project root
cd "$(dirname "$0")/.."

echo "===== Grace Project Integration Test ====="
echo "Starting integration tests at $(date)"
echo

# Check Python installation
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi
python3 --version
echo "Python check: PASSED"
echo

# Check required Python packages
echo "Checking required Python packages..."
python3 -c "
import sys
required_packages = [
    'chromadb', 'pyjwt', 'cryptography', 'requests', 
    'solana', 'flask', 'redis', 'ntscraper'
]
missing_packages = []
for package in required_packages:
    try:
        __import__(package)
        print(f'✓ {package}')
    except ImportError:
        missing_packages.append(package)
        print(f'✗ {package}')
if missing_packages:
    print(f'\nError: Missing required packages: {", ".join(missing_packages)}')
    sys.exit(1)
else:
    print('\nAll required packages are installed.')
"
if [ $? -ne 0 ]; then
    echo "Package check: FAILED"
    exit 1
fi
echo "Package check: PASSED"
echo

# Run the comprehensive testing module
echo "Running comprehensive tests..."
python3 src/comprehensive_testing.py
if [ $? -ne 0 ]; then
    echo "Comprehensive tests: FAILED"
    exit 1
fi
echo "Comprehensive tests: PASSED"
echo

# Test user profile system
echo "Testing user profile system..."
python3 -c "
import sys
sys.path.append('.')
from src.user_profile import UserProfileSystem
from src.password_recovery import PasswordRecoverySystem

try:
    # Initialize systems
    user_profile = UserProfileSystem()
    password_recovery = PasswordRecoverySystem()
    
    # Test user creation
    test_user = user_profile.create_user('test_user', 'test@example.com', 'TestPassword123!')
    if not test_user:
        print('Failed to create test user')
        sys.exit(1)
    
    # Test authentication
    auth_result = user_profile.authenticate_user('test_user', 'TestPassword123!')
    if not auth_result or not auth_result.get('success'):
        print('Failed to authenticate test user')
        sys.exit(1)
    
    # Test password recovery
    token = password_recovery.generate_recovery_token('test@example.com')
    if not token:
        print('Failed to generate recovery token')
        sys.exit(1)
    
    verify_result = password_recovery.verify_recovery_token(token)
    if not verify_result or not verify_result.get('success'):
        print('Failed to verify recovery token')
        sys.exit(1)
    
    print('User profile system tests completed successfully')
except Exception as e:
    print(f'Error testing user profile system: {str(e)}')
    sys.exit(1)
"
if [ $? -ne 0 ]; then
    echo "User profile system test: FAILED"
    exit 1
fi
echo "User profile system test: PASSED"
echo

# Test wallet integration
echo "Testing wallet integration..."
python3 -c "
import sys
sys.path.append('.')
try:
    from src.solana_wallet import SolanaWalletManager
    from src.wallet_connection import WalletConnectionManager
    
    # Initialize wallet manager
    wallet_manager = SolanaWalletManager()
    
    # Test wallet generation
    wallet = wallet_manager.generate_wallet()
    if not wallet or not wallet.get('public_key'):
        print('Failed to generate wallet')
        sys.exit(1)
    
    # Test wallet connection manager
    connection_manager = WalletConnectionManager()
    connection_status = connection_manager.check_connection_status()
    print(f'Wallet connection status: {connection_status}')
    
    print('Wallet integration tests completed successfully')
except Exception as e:
    print(f'Error testing wallet integration: {str(e)}')
    sys.exit(1)
"
if [ $? -ne 0 ]; then
    echo "Wallet integration test: FAILED"
    exit 1
fi
echo "Wallet integration test: PASSED"
echo

# Test GMGN service
echo "Testing GMGN service..."
python3 -c "
import sys
sys.path.append('.')
try:
    from src.gmgn_service import GMGNService
    
    # Initialize GMGN service
    gmgn = GMGNService()
    
    # Test connection to GMGN API
    status = gmgn.check_api_status()
    print(f'GMGN API status: {status}')
    
    print('GMGN service tests completed successfully')
except Exception as e:
    print(f'Error testing GMGN service: {str(e)}')
    sys.exit(1)
"
if [ $? -ne 0 ]; then
    echo "GMGN service test: FAILED"
    exit 1
fi
echo "GMGN service test: PASSED"
echo

# Test Nitter service
echo "Testing Nitter service..."
python3 -c "
import sys
sys.path.append('.')
try:
    from src.nitter_service import NitterService
    
    # Initialize Nitter service with mock mode for testing
    nitter = NitterService(test_mode=True)
    
    # Test Nitter service functionality
    status = nitter.check_service_status()
    print(f'Nitter service status: {status}')
    
    print('Nitter service tests completed successfully')
except Exception as e:
    print(f'Error testing Nitter service: {str(e)}')
    sys.exit(1)
"
if [ $? -ne 0 ]; then
    echo "Nitter service test: FAILED"
    exit 1
fi
echo "Nitter service test: PASSED"
echo

# Test memory system
echo "Testing memory system..."
python3 -c "
import sys
sys.path.append('.')
try:
    from src.memory_system import MemorySystem
    
    # Initialize memory system
    memory = MemorySystem()
    
    # Test memory operations
    memory.add_to_short_term_memory('test_user', 'This is a test memory')
    result = memory.query_short_term_memory('test_user', 'test')
    if not result or len(result) == 0:
        print('Failed to retrieve memory')
        sys.exit(1)
    
    print('Memory system tests completed successfully')
except Exception as e:
    print(f'Error testing memory system: {str(e)}')
    sys.exit(1)
"
if [ $? -ne 0 ]; then
    echo "Memory system test: FAILED"
    exit 1
fi
echo "Memory system test: PASSED"
echo

# Test transaction confirmation
echo "Testing transaction confirmation..."
python3 -c "
import sys
sys.path.append('.')
try:
    from src.transaction_confirmation import TransactionConfirmationSystem
    
    # Initialize transaction confirmation system
    tx_system = TransactionConfirmationSystem()
    
    # Test transaction preparation
    tx = tx_system.prepare_transaction('test_user', 'swap', {
        'from_token': 'SOL',
        'to_token': 'BONK',
        'amount': '0.01'
    })
    if not tx or not tx.get('confirmation_id'):
        print('Failed to prepare transaction')
        sys.exit(1)
    
    # Test transaction confirmation
    confirmation_id = tx.get('confirmation_id')
    result = tx_system.get_transaction_details(confirmation_id)
    if not result:
        print('Failed to get transaction details')
        sys.exit(1)
    
    print('Transaction confirmation tests completed successfully')
except Exception as e:
    print(f'Error testing transaction confirmation: {str(e)}')
    sys.exit(1)
"
if [ $? -ne 0 ]; then
    echo "Transaction confirmation test: FAILED"
    exit 1
fi
echo "Transaction confirmation test: PASSED"
echo

# Test multi-agent system
echo "Testing multi-agent system..."
python3 -c "
import sys
sys.path.append('.')
try:
    from src.multi_agent_system import MultiAgentSystem
    
    # Initialize multi-agent system
    agents = MultiAgentSystem()
    
    # Test agent initialization
    status = agents.check_agents_status()
    print(f'Agents status: {status}')
    
    # Test task routing
    task_result = agents.route_task('test_task', {'type': 'test'})
    print(f'Task routing result: {task_result}')
    
    print('Multi-agent system tests completed successfully')
except Exception as e:
    print(f'Error testing multi-agent system: {str(e)}')
    sys.exit(1)
"
if [ $? -ne 0 ]; then
    echo "Multi-agent system test: FAILED"
    exit 1
fi
echo "Multi-agent system test: PASSED"
echo

# Test Grace core
echo "Testing Grace core..."
python3 -c "
import sys
sys.path.append('.')
try:
    from src.grace_core import GraceCore
    
    # Initialize Grace core
    grace = GraceCore(test_mode=True)
    
    # Test message processing
    response = grace.process_message('test_user', 'Hello Grace')
    if not response:
        print('Failed to process message')
        sys.exit(1)
    
    # Test command processing
    command_response = grace.process_message('test_user', '!grace.help')
    if not command_response:
        print('Failed to process command')
        sys.exit(1)
    
    print('Grace core tests completed successfully')
except Exception as e:
    print(f'Error testing Grace core: {str(e)}')
    sys.exit(1)
"
if [ $? -ne 0 ]; then
    echo "Grace core test: FAILED"
    exit 1
fi
echo "Grace core test: PASSED"
echo

echo "===== Integration Test Summary ====="
echo "All integration tests PASSED!"
echo "Grace is ready for deployment."
echo "Completed at $(date)"
echo "=================================="

exit 0
