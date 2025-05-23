import pytest
from src.gmgn_service import GMGNService
from src.mango_v3_extension import MangoV3Extension  # Importing Mango V3 if needed

# Initialize the service with configuration
default_config = {"mango_v3": {"enabled": True, "url": "http://localhost:8000"}}
service = GMGNService(config=default_config)

# Define trade parameters for spot trade
spot_market = "KDOT"
spot_side = "buy"
spot_price = 1.00
spot_size = 10.0
spot_trade_type = "spot"

# Define trade parameters for leverage trade
leverage_market = "KDOT"
leverage_side = "buy"
leverage_price = 1.00
leverage_size = 10.0
leverage_trade_type = "leverage"


def test_spot_trade():
    try:
        # Call the actual method to execute the spot trade
        spot_result = service.place_limit_order(
            spot_market, spot_side, spot_price, spot_size, trade_type=spot_trade_type
        )
        print("Spot Trade Result:", spot_result)
    except Exception as e:
        print(f"Error executing spot trade: {e}")


def test_leverage_trade():
    try:
        # Call the actual method to execute the leverage trade
        leverage_result = service.place_limit_order(
            leverage_market,
            leverage_side,
            leverage_price,
            leverage_size,
            trade_type=leverage_trade_type,
        )
        print("Leverage Trade Result:", leverage_result)
    except Exception as e:
        print(f"Error executing leverage trade: {e}")


# Run the tests
if __name__ == "__main__":
    pytest.main()
