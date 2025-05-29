"""
Custom exceptions for the Grace wallet connection system.
"""

class PhantomWalletError(Exception):
    """Base exception for Phantom wallet errors."""
    pass

class SessionExpiredError(PhantomWalletError):
    """Raised when a session has expired."""
    pass

class InvalidWalletAddressError(PhantomWalletError):
    """Raised when an invalid wallet address is provided."""
    pass

class InvalidSessionError(PhantomWalletError):
    """Raised when an invalid session is detected."""
    pass

class WalletConnectionError(PhantomWalletError):
    """Raised when there's an error connecting to the wallet."""
    pass

class InvalidConfigurationError(PhantomWalletError):
    """Raised when there's an error in the wallet configuration."""
    pass
