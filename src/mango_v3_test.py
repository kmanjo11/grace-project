"""
Quick test script for Mango V3 Extension - Testing All Endpoints
"""
import logging
from mango_v3_extension import MangoV3Extension

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_endpoints():
    """Test all available Mango V3 endpoints"""
    
    # Initialize with localhost
    mango = MangoV3Extension(
        base_url="http://localhost",
        logger=logger
    )
    client = mango.client
    
    # Test all available GET endpoints
    endpoints = {
        "Get Positions": client.get_positions,
        "Get Coins": client.get_coins,
        "Get Wallet Balances": client.get_wallet_balances,
        "Get All Markets": client.get_markets,
        "Get BTC Market": lambda: client.get_market_by_name("BTC-PERP"),
    }
    
    results = {}
    for name, endpoint_func in endpoints.items():
        try:
            logger.info(f"Testing: {name}")
            response = endpoint_func()
            results[name] = {
                "success": True,
                "response": response
            }
            logger.info(f"✅ {name}: {response}")
        except Exception as e:
            results[name] = {
                "success": False,
                "error": str(e)
            }
            logger.error(f"❌ {name} failed: {e}")
    
    # Test extension methods
    extension_endpoints = {
        "Get Market Data": lambda: mango.get_market_data(),
        "Get Portfolio Summary": mango.get_portfolio_summary
    }
    
    for name, endpoint_func in extension_endpoints.items():
        try:
            logger.info(f"Testing Extension: {name}")
            response = endpoint_func()
            results[name] = {
                "success": True,
                "response": response
            }
            logger.info(f"✅ {name}: {response}")
        except Exception as e:
            results[name] = {
                "success": False,
                "error": str(e)
            }
            logger.error(f"❌ {name} failed: {e}")
    
    return results

if __name__ == "__main__":
    logger.info("Starting Mango V3 endpoint tests...")
    results = test_endpoints()
    
    # Summary
    logger.info("\n=== Test Summary ===")
    for name, result in results.items():
        status = "✅" if result["success"] else "❌"
        logger.info(f"{status} {name}")
