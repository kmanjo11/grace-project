"""
Dynamic Crypto Data Service for Grace - A crypto trading application based on Open Interpreter

This module implements a dynamic approach for crypto data using GMGN or Mango
based on natural language requests. It provides a flexible interface for
retrieving price data, executing trades, and managing liquidity pools.
"""

import os
import sys
import json
import time
import logging
import random
import requests
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import re

from src.config import get_config

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("GraceCryptoDataService")


class DynamicCryptoDataService:
    """Service for dynamically accessing crypto data from GMGN or Mango."""

    def __init__(
        self,
        gmgn_api_url: Optional[str] = None,
        memory_system=None,
        cache_duration: int = 300,  # 5 minutes cache by default
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the Dynamic Crypto Data Service.

        Args:
            gmgn_api_url: URL for GMGN API
            memory_system: Memory system for storing and retrieving data
            cache_duration: Duration in seconds to cache results
            config: Additional configuration options
        """
        self.gmgn_api_url = gmgn_api_url or os.environ.get("GMGN_API_URL")
        self.memory_system = memory_system
        self.cache_duration = cache_duration
        self.config = config or {}
        self.cache = {}

        logger.info(f"Initialized Dynamic Crypto Data Service")

    def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Get data from cache if available and not expired.

        Args:
            cache_key: Cache key

        Returns:
            Optional[Dict[str, Any]]: Cached data or None
        """
        if cache_key in self.cache:
            cache_entry = self.cache[cache_key]
            if datetime.now() < cache_entry["expires_at"]:
                logger.info(f"Cache hit for key: {cache_key}")
                return cache_entry["data"]
            else:
                logger.info(f"Cache expired for key: {cache_key}")
                del self.cache[cache_key]

        return None

    def _add_to_cache(
        self, cache_key: str, data: Dict[str, Any], duration: Optional[int] = None
    ) -> None:
        """
        Add data to cache.

        Args:
            cache_key: Cache key
            data: Data to cache
            duration: Cache duration in seconds (overrides default)
        """
        cache_duration = duration or self.cache_duration
        expires_at = datetime.now() + timedelta(seconds=cache_duration)

        self.cache[cache_key] = {"data": data, "expires_at": expires_at}

        logger.info(f"Added to cache with key: {cache_key}, expires at: {expires_at}")

    def _parse_natural_language_request(self, request: str) -> Dict[str, Any]:
        """
        Parse a natural language request to determine the appropriate API and parameters.

        Args:
            request: Natural language request

        Returns:
            Dict[str, Any]: Parsed request with API and parameters
        """
        request_lower = request.lower()

        # Initialize result
        result = {"api": None, "function": None, "parameters": {}, "confidence": 0.0}

        # Check for price/chart related requests
        price_patterns = [
            r"price of (\w+)",
            r"(\w+) price",
            r"how much is (\w+)",
            r"chart for (\w+)",
            r"(\w+) chart",
        ]

        for pattern in price_patterns:
            match = re.search(pattern, request_lower)
            if match:
                token = match.group(1)
                result["api"] = "gmgn"
                result["function"] = "get_token_price"
                result["parameters"]["token"] = token
                result["confidence"] = 0.8

                # Check for timeframe
                timeframe_match = re.search(r"(1h|1d|1w|1m|1y)", request_lower)
                if timeframe_match:
                    result["parameters"]["timeframe"] = timeframe_match.group(1)
                else:
                    result["parameters"]["timeframe"] = "1d"  # Default timeframe

                break

        # Check for trading related requests
        if not result["function"]:
            trade_patterns = [
                r"(buy|purchase) (\d+) (\w+)",
                r"(sell|trade) (\d+) (\w+)",
                r"swap (\d+) (\w+) (to|for) (\w+)",
            ]

            for pattern in trade_patterns:
                match = re.search(pattern, request_lower)
                if match:
                    if "swap" in pattern:
                        amount = match.group(1)
                        from_token = match.group(2)
                        to_token = match.group(4)

                        result["api"] = "mango"
                        result["function"] = "execute_swap"
                        result["parameters"]["amount"] = amount
                        result["parameters"]["from_token"] = from_token
                        result["parameters"]["to_token"] = to_token
                    else:
                        action = match.group(1)
                        amount = match.group(2)
                        token = match.group(3)

                        result["api"] = "mango"
                        result["function"] = "execute_trade"
                        result["parameters"]["action"] = action
                        result["parameters"]["amount"] = amount
                        result["parameters"]["token"] = token

                    result["confidence"] = 0.9
                    break

        # Check for liquidity pool related requests
        if not result["function"]:
            liquidity_patterns = [
                r"(create|add) liquidity (\w+) and (\w+)",
                r"liquidity pool for (\w+) and (\w+)",
                r"provide liquidity (\w+) (\w+)",
            ]

            for pattern in liquidity_patterns:
                match = re.search(pattern, request_lower)
                if match:
                    token_a = match.group(2)
                    token_b = match.group(3)

                    result["api"] = "mango"
                    result["function"] = "create_liquidity_pool"
                    result["parameters"]["token_a"] = token_a
                    result["parameters"]["token_b"] = token_b

                    # Check for amounts
                    amount_match = re.search(
                        r"(\d+) (\w+) and (\d+) (\w+)", request_lower
                    )
                    if amount_match:
                        result["parameters"]["amount_a"] = amount_match.group(1)
                        result["parameters"]["amount_b"] = amount_match.group(3)

                    result["confidence"] = 0.85
                    break

        # Check for wallet related requests
        if not result["function"]:
            wallet_patterns = [
                r"(wallet|portfolio) (balance|status)",
                r"show (my|) (wallet|portfolio)",
                r"(check|view) (my|) (wallet|portfolio)",
            ]

            for pattern in wallet_patterns:
                match = re.search(pattern, request_lower)
                if match:
                    result["api"] = "mango"
                    result["function"] = "get_wallet_balance"
                    result["confidence"] = 0.75
                    break

        # If no specific function was identified, default to general market info
        if not result["function"]:
            result["api"] = "gmgn"
            result["function"] = "get_market_info"

            # Try to extract token from request
            token_match = re.search(r"(\w+)", request_lower)
            if token_match:
                result["parameters"]["token"] = token_match.group(1)

            result["confidence"] = 0.5

        return result

    def process_natural_language_request(
        self, request: str, user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a natural language request and execute the appropriate function.

        Args:
            request: Natural language request
            user_id: User ID for personalized responses

        Returns:
            Dict[str, Any]: Response to the request
        """
        # Parse request
        parsed_request = self._parse_natural_language_request(request)
        logger.info(f"Parsed request: {parsed_request}")

        # Check confidence
        if parsed_request["confidence"] < 0.6:
            return {
                "status": "unclear",
                "message": "I'm not sure what you're asking for. Could you please be more specific?",
                "parsed_request": parsed_request,
            }

        # Execute function based on API and function name
        api = parsed_request["api"]
        function_name = parsed_request["function"]
        parameters = parsed_request["parameters"]

        if api == "gmgn":
            return self._execute_gmgn_function(function_name, parameters, user_id)
        elif api == "mango":
            return self._execute_mango_function(function_name, parameters, user_id)
        else:
            return {
                "status": "error",
                "message": f"Unknown API: {api}",
                "parsed_request": parsed_request,
            }

    def _execute_gmgn_function(
        self,
        function_name: str,
        parameters: Dict[str, Any],
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute a GMGN API function.

        Args:
            function_name: Function name
            parameters: Function parameters
            user_id: User ID for personalized responses

        Returns:
            Dict[str, Any]: Function result
        """
        # Check if GMGN API URL is available
        if not self.gmgn_api_url:
            logger.warning("GMGN API URL not available, using mock data")
            return self._generate_mock_data(function_name, parameters)

        # Create cache key
        cache_key = f"gmgn_{function_name}_{json.dumps(parameters, sort_keys=True)}"

        # Check cache
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            return cached_data

        try:
            # Map function names to GMGN API endpoints
            endpoint_map = {
                "get_token_price": "/price",
                "get_market_info": "/market",
                "get_token_chart": "/chart",
            }

            if function_name not in endpoint_map:
                logger.error(f"Unknown GMGN function: {function_name}")
                return {
                    "status": "error",
                    "message": f"Unknown GMGN function: {function_name}",
                }

            # Build API URL
            endpoint = endpoint_map[function_name]
            url = f"{self.gmgn_api_url}{endpoint}"

            # Make API request
            response = requests.get(url, params=parameters)

            if response.status_code == 200:
                result = response.json()

                # Cache result
                self._add_to_cache(cache_key, result)

                return result
            else:
                logger.error(
                    f"GMGN API error: {response.status_code} - {response.text}"
                )
                return {
                    "status": "error",
                    "message": f"GMGN API error: {response.status_code}",
                    "details": response.text,
                }
        except Exception as e:
            logger.error(f"Error executing GMGN function {function_name}: {str(e)}")
            return {
                "status": "error",
                "message": f"Error executing GMGN function: {str(e)}",
            }

    def _execute_mango_function(
        self,
        function_name: str,
        parameters: Dict[str, Any],
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute a Mango API function.

        Args:
            function_name: Function name
            parameters: Function parameters
            user_id: User ID for personalized responses

        Returns:
            Dict[str, Any]: Function result
        """
        # For now, use mock data since we don't have actual Mango integration yet
        logger.warning("Mango integration not available, using mock data")
        return self._generate_mock_data(function_name, parameters)

    def _generate_mock_data(
        self, function_name: str, parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate mock data for testing.

        Args:
            function_name: Function name
            parameters: Function parameters

        Returns:
            Dict[str, Any]: Mock data
        """
        if function_name == "get_token_price":
            token = parameters.get("token", "unknown").upper()
            timeframe = parameters.get("timeframe", "1d")

            # Generate random price based on token name for consistency
            import hashlib

            token_hash = int(hashlib.md5(token.encode()).hexdigest(), 16)
            base_price = (token_hash % 10000) / 100  # Price between 0 and 100

            # Add some randomness
            import random

            current_price = base_price * (0.9 + 0.2 * random.random())

            # Generate price history
            price_history = []
            num_points = {"1h": 60, "1d": 24, "1w": 7, "1m": 30, "1y": 12}[timeframe]

            for i in range(num_points):
                # Random price fluctuation
                price = base_price * (0.8 + 0.4 * random.random())

                # Calculate timestamp
                if timeframe == "1h":
                    timestamp = datetime.now() - timedelta(minutes=i)
                elif timeframe == "1d":
                    timestamp = datetime.now() - timedelta(hours=i)
                elif timeframe == "1w":
                    timestamp = datetime.now() - timedelta(days=i)
                elif timeframe == "1m":
                    timestamp = datetime.now() - timedelta(days=i)
                else:  # 1y
                    timestamp = datetime.now() - timedelta(days=i * 30)

                price_history.append(
                    {"timestamp": timestamp.isoformat(), "price": price}
                )

            # Reverse to get chronological order
            price_history.reverse()

            return {
                "status": "success",
                "token": token,
                "timeframe": timeframe,
                "current_price": current_price,
                "price_change_24h": random.uniform(-5, 5),
                "price_history": price_history,
                "mock_data": True,
            }

        elif function_name == "get_market_info":
            token = parameters.get("token", "unknown").upper()

            return {
                "status": "success",
                "token": token,
                "market_cap": random.randint(1000000, 1000000000),
                "volume_24h": random.randint(100000, 10000000),
                "circulating_supply": random.randint(1000000, 1000000000),
                "total_supply": random.randint(1000000, 1000000000),
                "rank": random.randint(1, 100),
                "mock_data": True,
            }

        elif function_name == "execute_trade" or function_name == "execute_swap":
            # For trades, we need to return a confirmation request first
            # The actual execution would happen after user confirmation

            if function_name == "execute_trade":
                action = parameters.get("action", "buy")
                amount = parameters.get("amount", "0")
                token = parameters.get("token", "unknown").upper()

                return {
                    "status": "confirmation_required",
                    "action": action,
                    "amount": amount,
                    "token": token,
                    "estimated_price": random.uniform(0.1, 100),
                    "estimated_total": float(amount) * random.uniform(0.1, 100),
                    "confirmation_id": f"trade_{int(time.time())}",
                    "mock_data": True,
                }
            else:  # execute_swap
                amount = parameters.get("amount", "0")
                from_token = parameters.get("from_token", "unknown").upper()
                to_token = parameters.get("to_token", "unknown").upper()

                return {
                    "status": "confirmation_required",
                    "amount": amount,
                    "from_token": from_token,
                    "to_token": to_token,
                    "estimated_rate": random.uniform(0.1, 10),
                    "estimated_receive": float(amount) * random.uniform(0.1, 10),
                    "confirmation_id": f"swap_{int(time.time())}",
                    "mock_data": True,
                }

        elif function_name == "create_liquidity_pool":
            token_a = parameters.get("token_a", "unknown").upper()
            token_b = parameters.get("token_b", "unknown").upper()
            amount_a = parameters.get("amount_a", "0")
            amount_b = parameters.get("amount_b", "0")

            return {
                "status": "confirmation_required",
                "token_a": token_a,
                "token_b": token_b,
                "amount_a": amount_a,
                "amount_b": amount_b,
                "estimated_fee": random.uniform(0.1, 1),
                "confirmation_id": f"pool_{int(time.time())}",
                "mock_data": True,
            }

        elif function_name == "get_wallet_balance":
            # Generate random wallet balance
            tokens = ["SOL", "BTC", "ETH", "USDC", "BONK", "MANGO"]
            balances = []

            for token in tokens:
                balances.append(
                    {
                        "token": token,
                        "balance": random.uniform(0.1, 100),
                        "usd_value": random.uniform(10, 10000),
                    }
                )

            return {
                "status": "success",
                "wallet_type": random.choice(["internal", "phantom"]),
                "total_usd_value": sum(b["usd_value"] for b in balances),
                "balances": balances,
                "mock_data": True,
            }

        else:
            return {
                "status": "error",
                "message": f"Unknown function: {function_name}",
                "mock_data": True,
            }

    def confirm_transaction(
        self, confirmation_id: str, user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Confirm a transaction.

        Args:
            confirmation_id: Confirmation ID
            user_id: User ID

        Returns:
            Dict[str, Any]: Confirmation result
        """
        # In a real implementation, this would execute the actual transaction
        # For now, return mock success

        transaction_type = confirmation_id.split("_")[0]

        if transaction_type == "trade":
            return {
                "status": "success",
                "transaction_type": "trade",
                "transaction_id": f"tx_{int(time.time())}",
                "execution_time": datetime.now().isoformat(),
                "fee": random.uniform(0.01, 0.1),
                "mock_data": True,
            }
        elif transaction_type == "swap":
            return {
                "status": "success",
                "transaction_type": "swap",
                "transaction_id": f"tx_{int(time.time())}",
                "execution_time": datetime.now().isoformat(),
                "fee": random.uniform(0.01, 0.1),
                "rate": random.uniform(0.1, 10),
                "mock_data": True,
            }
        elif transaction_type == "pool":
            return {
                "status": "success",
                "transaction_type": "liquidity_pool",
                "transaction_id": f"tx_{int(time.time())}",
                "execution_time": datetime.now().isoformat(),
                "fee": random.uniform(0.01, 0.1),
                "pool_id": f"pool_{int(time.time())}",
                "mock_data": True,
            }
        else:
            return {
                "status": "error",
                "message": f"Unknown confirmation ID: {confirmation_id}",
                "mock_data": True,
            }

    def cancel_transaction(
        self, confirmation_id: str, user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Cancel a transaction.

        Args:
            confirmation_id: Confirmation ID
            user_id: User ID

        Returns:
            Dict[str, Any]: Cancellation result
        """
        return {
            "status": "success",
            "message": "Transaction cancelled",
            "confirmation_id": confirmation_id,
            "mock_data": True,
        }


# Example usage
if __name__ == "__main__":
    # Initialize Dynamic Crypto Data Service
    crypto_service = DynamicCryptoDataService()

    # Process a natural language request
    result = crypto_service.process_natural_language_request(
        "What's the price of Bitcoin?"
    )
    print(json.dumps(result, indent=2))
