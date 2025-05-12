"""
Mock Solana module for testing without Solana dependencies.

This module provides mock implementations of Solana classes and functions
for testing purposes when the actual Solana libraries are not available.
"""

import os
import base64
import secrets
from typing import List, Dict, Any, Optional, Tuple


class Keypair:
    """Mock implementation of Solana Keypair."""
    
    def __init__(self, secret_key: Optional[bytes] = None):
        """
        Initialize a mock Solana keypair.
        
        Args:
            secret_key: Optional secret key bytes
        """
        if secret_key is None:
            # Generate random bytes for secret key
            self._secret_key = secrets.token_bytes(32)
        else:
            self._secret_key = secret_key
            
        # First 32 bytes are the secret key, public key is derived from it
        self._public_key = self._derive_public_key(self._secret_key)
    
    @staticmethod
    def _derive_public_key(secret_key: bytes) -> bytes:
        """
        Derive a public key from a secret key.
        
        In a real implementation, this would use ed25519 derivation.
        For this mock, we'll just use a simple deterministic derivation.
        
        Args:
            secret_key: Secret key bytes
            
        Returns:
            bytes: Public key bytes
        """
        # Simple mock derivation - in reality this would use ed25519
        return bytes([b ^ 0xFF for b in secret_key[-32:]])
    
    @staticmethod
    def generate() -> 'Keypair':
        """
        Generate a new random keypair.
        
        Returns:
            Keypair: New keypair instance
        """
        return Keypair()
    
    @staticmethod
    def from_secret_key(secret_key: bytes) -> 'Keypair':
        """
        Create a keypair from a secret key.
        
        Args:
            secret_key: Secret key bytes
            
        Returns:
            Keypair: New keypair instance
        """
        return Keypair(secret_key)
    
    @property
    def secret_key(self) -> bytes:
        """
        Get the secret key.
        
        Returns:
            bytes: Secret key bytes
        """
        return self._secret_key
    
    @property
    def public_key(self) -> bytes:
        """
        Get the public key.
        
        Returns:
            bytes: Public key bytes
        """
        return self._public_key
    
    def public_key_base58(self) -> str:
        """
        Get the public key in a clean alphanumeric format.
        
        Returns:
            str: Hex-encoded public key (clean alphanumeric format)
        """
        # Use hex encoding instead of base64/base58 to ensure a clean alphanumeric format
        return self._public_key.hex()
    
    def __str__(self) -> str:
        """
        String representation of the keypair.
        
        Returns:
            str: String representation
        """
        return f"Keypair(public_key={self.public_key_base58()})"


class PublicKey:
    """Mock implementation of Solana PublicKey."""
    
    def __init__(self, value: str):
        """
        Initialize a mock Solana public key.
        
        Args:
            value: Public key as a string
        """
        self._value = value
    
    def __str__(self) -> str:
        """
        String representation of the public key.
        
        Returns:
            str: String representation
        """
        return self._value
    
    def to_base58(self) -> str:
        """
        Get the public key in base58 encoding.
        
        Returns:
            str: Base58-encoded public key
        """
        return self._value


class Transaction:
    """Mock implementation of Solana Transaction."""
    
    def __init__(self):
        """Initialize a mock Solana transaction."""
        self.signatures = []
        self.instructions = []
        self.recent_blockhash = None
    
    def add(self, instruction: Any) -> 'Transaction':
        """
        Add an instruction to the transaction.
        
        Args:
            instruction: Transaction instruction
            
        Returns:
            Transaction: Self for chaining
        """
        self.instructions.append(instruction)
        return self
    
    def sign(self, *signers: List[Keypair]) -> None:
        """
        Sign the transaction with the given signers.
        
        Args:
            signers: List of keypairs to sign with
        """
        for signer in signers:
            self.signatures.append({
                'signature': f"sig_{signer.public_key_base58()}",
                'public_key': signer.public_key_base58()
            })
    
    def serialize(self) -> bytes:
        """
        Serialize the transaction.
        
        Returns:
            bytes: Serialized transaction
        """
        # Mock serialization
        return b'mock_serialized_transaction'


class Connection:
    """Mock implementation of Solana Connection."""
    
    def __init__(self, endpoint: str, commitment: Optional[str] = None):
        """
        Initialize a mock Solana connection.
        
        Args:
            endpoint: RPC endpoint URL
            commitment: Commitment level
        """
        self.endpoint = endpoint
        self.commitment = commitment or 'confirmed'
    
    async def get_balance(self, public_key: PublicKey) -> int:
        """
        Get the balance for a public key.
        
        Args:
            public_key: Public key to get balance for
            
        Returns:
            int: Balance in lamports
        """
        # Mock balance - in reality this would query the Solana network
        # For testing, return a deterministic value based on the public key
        return int(hash(str(public_key)) % 1000000000)
    
    async def get_token_accounts_by_owner(self, owner: PublicKey, token_program_id: PublicKey) -> List[Dict[str, Any]]:
        """
        Get token accounts owned by the given public key.
        
        Args:
            owner: Owner public key
            token_program_id: Token program ID
            
        Returns:
            List[Dict[str, Any]]: List of token accounts
        """
        # Mock token accounts
        return [
            {
                'pubkey': 'TokenAccount1',
                'account': {
                    'data': {
                        'parsed': {
                            'info': {
                                'mint': 'So11111111111111111111111111111111111111112',
                                'owner': str(owner),
                                'tokenAmount': {
                                    'amount': '100000000',
                                    'decimals': 9,
                                    'uiAmount': 0.1
                                }
                            }
                        }
                    }
                }
            }
        ]
    
    async def get_recent_blockhash(self) -> Dict[str, Any]:
        """
        Get a recent blockhash.
        
        Returns:
            Dict[str, Any]: Recent blockhash info
        """
        # Mock blockhash
        return {
            'blockhash': 'mock_blockhash',
            'feeCalculator': {
                'lamportsPerSignature': 5000
            }
        }
    
    async def send_transaction(self, transaction: Transaction) -> str:
        """
        Send a transaction.
        
        Args:
            transaction: Transaction to send
            
        Returns:
            str: Transaction signature
        """
        # Mock transaction signature
        return 'mock_transaction_signature'
    
    async def confirm_transaction(self, signature: str) -> Dict[str, Any]:
        """
        Confirm a transaction.
        
        Args:
            signature: Transaction signature
            
        Returns:
            Dict[str, Any]: Confirmation info
        """
        # Mock confirmation
        return {
            'value': {
                'confirmations': 1,
                'status': {
                    'Ok': None
                }
            }
        }


# Export symbols
__all__ = ['Keypair', 'PublicKey', 'Transaction', 'Connection']
