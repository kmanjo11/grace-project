"""
Centralized configuration system for Grace project.

This module provides a unified approach to configuration management,
loading settings from config files, environment variables, and defaults
in a consistent manner across all components.
"""

import os
import json
import logging
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("GraceConfig")


class GraceConfig:
    """
    Centralized configuration manager for Grace project.

    Loads configuration from:
    1. JSON config file (if provided)
    2. Environment variables (as fallback)
    3. Default values (as final fallback)
    """

    # Default configuration values
    DEFAULT_CONFIG = {
        # Data storage
        "data_dir": "/home/ubuntu/grace_project/data",
        "encryption_key": "grace_default_encryption_key",
        # Solana settings
        "solana_rpc_url": "https://mainnet.helius-rpc.com/?api-key=aa07df83-e1ac-4117-b00d-173e94e4fff7",
        "solana_network": "mainnet-beta",
        # API endpoints
        "nitter_instance": "http://localhost:8085",
        "gmgn_router_endpoint": "https://gmgn.ai/defi/router/v1/sol/tx/get_swap_route",
        "gmgn_price_endpoint": "https://www.gmgn.cc/kline/{chain}/{token}",
        # Authorization
        "authorized_admin_email": "kmanjo11@gmail.com",
        # Memory settings
        "short_term_memory_limit": 100,
        "medium_term_memory_limit": 1000,
        "memory_relevance_threshold": 0.7,
        # Transaction settings
        "transaction_confirmation_timeout": 300,  # seconds
        "max_slippage": 2.0,  # percentage
        # UI settings
        "ui_theme": "dark",
        "ui_port": 8080,
    }

    # Environment variable mapping
    ENV_MAPPING = {
        "GRACE_DATA_DIR": "data_dir",
        "GRACE_ENCRYPTION_KEY": "encryption_key",
        "SOLANA_RPC_URL": "solana_rpc_url",
        "SOLANA_NETWORK": "solana_network",
        "GMGN_ROUTER_ENDPOINT": "gmgn_router_endpoint",
        "GMGN_PRICE_ENDPOINT": "gmgn_price_endpoint",
        "AUTHORIZED_ADMIN_EMAIL": "authorized_admin_email",
        "SHORT_TERM_MEMORY_LIMIT": "short_term_memory_limit",
        "MEDIUM_TERM_MEMORY_LIMIT": "medium_term_memory_limit",
        "MEMORY_RELEVANCE_THRESHOLD": "memory_relevance_threshold",
        "TRANSACTION_CONFIRMATION_TIMEOUT": "transaction_confirmation_timeout",
        "MAX_SLIPPAGE": "max_slippage",
        "UI_THEME": "ui_theme",
        "UI_PORT": "ui_port",
    }

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration manager.

        Args:
            config_path: Path to JSON configuration file (optional)
        """
        self.config = self._load_config(config_path)
        logger.info("Grace configuration initialized")

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """
        Load configuration from file, environment variables, and defaults.

        Args:
            config_path: Path to JSON configuration file

        Returns:
            Dict[str, Any]: Configuration dictionary
        """
        # Start with default configuration
        config = self.DEFAULT_CONFIG.copy()

        # Load from config file if provided
        if config_path:
            try:
                with open(config_path, "r") as f:
                    file_config = json.load(f)
                    logger.info(f"Loaded configuration from {config_path}")

                    # Update config with file values
                    config.update(file_config)
            except Exception as e:
                logger.error(
                    f"Error loading configuration from {config_path}: {str(e)}"
                )
                logger.info("Falling back to environment variables and defaults")

        # Override with environment variables if present
        for env_var, config_key in self.ENV_MAPPING.items():
            env_value = os.environ.get(env_var)
            if env_value is not None:
                # Convert numeric values
                if config_key in [
                    "short_term_memory_limit",
                    "medium_term_memory_limit",
                    "transaction_confirmation_timeout",
                    "ui_port",
                ]:
                    try:
                        env_value = int(env_value)
                    except ValueError:
                        logger.warning(
                            f"Could not convert {env_var}={env_value} to int, using default"
                        )
                        continue

                # Convert float values
                elif config_key in ["memory_relevance_threshold", "max_slippage"]:
                    try:
                        env_value = float(env_value)
                    except ValueError:
                        logger.warning(
                            f"Could not convert {env_var}={env_value} to float, using default"
                        )
                        continue

                # Update config with environment value
                config[config_key] = env_value
                logger.debug(f"Using environment value for {config_key}: {env_value}")

        return config

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Any: Configuration value
        """
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value (runtime only, not persisted).

        Args:
            key: Configuration key
            value: Configuration value
        """
        self.config[key] = value
        logger.debug(f"Set runtime configuration {key}={value}")

    def save(self, config_path: str) -> bool:
        """
        Save current configuration to file.

        Args:
            config_path: Path to save configuration

        Returns:
            bool: Success status
        """
        try:
            with open(config_path, "w") as f:
                json.dump(self.config, f, indent=2)
            logger.info(f"Saved configuration to {config_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving configuration to {config_path}: {str(e)}")
            return False

    def __getitem__(self, key: str) -> Any:
        """
        Dictionary-style access to configuration.

        Args:
            key: Configuration key

        Returns:
            Any: Configuration value

        Raises:
            KeyError: If key not found
        """
        if key in self.config:
            return self.config[key]
        raise KeyError(f"Configuration key '{key}' not found")

    def __contains__(self, key: str) -> bool:
        """
        Check if configuration contains key.

        Args:
            key: Configuration key

        Returns:
            bool: True if key exists
        """
        return key in self.config


# Global configuration instance
grace_config = GraceConfig()


def get_config(config_path: Optional[str] = None) -> GraceConfig:
    """
    Get the global configuration instance.

    If config_path is provided, a new instance is created.
    Otherwise, the existing global instance is returned.

    Args:
        config_path: Path to configuration file (optional)

    Returns:
        GraceConfig: Configuration instance
    """
    global grace_config

    if config_path:
        grace_config = GraceConfig(config_path)

    return grace_config
