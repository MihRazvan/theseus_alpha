# tests/test_market_trading.py
import logging
from pathlib import Path
import json
import time

from hyperliquid.utils import constants
from theseus_alpha.utils.setup_utils import setup_trading_environment, setup_leverage

def test_perp_trading():
    """Test perpetual trading with ETH-USD."""
    # Setup environment
    main_address, info, exchange = setup_trading_environment(
        constants.TESTNET_API_URL,
        skip_ws=True
    )
    
    print("\n=== Testing Perpetual Trading (ETH-USD) ===")
    
    try:
        # Set leverage first
        print("\nSetting up leverage...")
        if not setup_leverage(exchange, "ETH", 1):
            print("❌ Failed to set leverage")
            return
        print("✅ Leverage set successfully")
        
        # Get current price
        mids = info.all_mids()
        eth_price = float(mids.get('ETH', 0))
        print(f"\nCurrent ETH Price: ${eth_price}")
        
        # Constants
        min_trade_value = 10.0  # Minimum value in USD
        min_trade_size_eth = 0.01  # Minimum size for ETH
        size_precision = 0.001  # Precision step

        # Calculate size
        eth_price = float(mids.get('ETH', 0))
        size = max(round(min_trade_value / eth_price, 6), min_trade_size_eth)

        # Adjust for precision
        size = round(size // size_precision * size_precision, 6)

        print(f"\nCalculated trade size: {size} ETH (for at least ${min_trade_value})")

        # Example tick size (adjust based on your exchange's requirements)
        tick_size = 0.01  # Minimum price increment

        # Calculate limit price and align it to the tick size
        limit_price = round((eth_price * 0.99) // tick_size * tick_size, 2)

        print(f"\nLimit price aligned to tick size: ${limit_price}")

        
        order_result = exchange.order(
            "ETH",      # Asset
            True,       # Buy
            size,       # Amount
            limit_price,  # Price
            {"limit": {"tif": "Gtc"}}  # Good-til-cancel
        )
        
        print("\nOrder Result:")
        print(json.dumps(order_result, indent=2))
        
        # If order is placed, try to cancel it
        if order_result["status"] == "ok":
            status = order_result["response"]["data"]["statuses"][0]
            if "resting" in status:
                time.sleep(1)  # Wait a bit
                print("\nCancelling test order...")
                cancel_result = exchange.cancel("ETH", status["resting"]["oid"])
                print("Cancel Result:")
                print(json.dumps(cancel_result, indent=2))
                
        print("✅ Perpetual trading test completed")
        
    except Exception as e:
        print(f"❌ Perpetual trading test failed: {str(e)}")
        raise

def test_spot_trading():
    """Test spot trading with PURR/USDC."""
    # Setup environment
    main_address, info, exchange = setup_trading_environment(
        constants.TESTNET_API_URL,
        skip_ws=True
    )
    
    print("\n=== Testing Spot Trading (PURR/USDC) ===")
    
    try:
        # Get current spot state
        spot_state = info.spot_user_state(main_address)
        print("\nSpot Balances:")
        for balance in spot_state.get("balances", []):
            print(json.dumps(balance, indent=2))
            
        # Place a small PURR order
        size = 30.0  
        price = 0.5  # Test price
        
        # Place test order
        print(f"\nPlacing test order: Buy {size} PURR @ ${price}")
        order_result = exchange.order(
            "PURR/USDC",  # Use proper spot pair format
            True,        # Buy
            size,       # Amount in PURR
            price,      # Price in USDC
            {"limit": {"tif": "Gtc"}}  # Good-til-cancel
        )
        
        print("\nOrder Result:")
        print(json.dumps(order_result, indent=2))
        
        # Cancel if order is resting
        if order_result["status"] == "ok":
            status = order_result["response"]["data"]["statuses"][0]
            if "resting" in status:
                time.sleep(1)  # Wait a bit
                cancel_result = exchange.cancel("PURR/USDC", status["resting"]["oid"])
                print("\nCancel Result:")
                print(json.dumps(cancel_result, indent=2))
                
        print("✅ Spot trading test completed")
        
    except Exception as e:
        print(f"❌ Spot trading test failed: {str(e)}")
        raise

def main():
    """Run both spot and perp trading tests."""
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Test perp trading first
        test_perp_trading()
        
        # Wait between tests
        time.sleep(2)
        
        # Test spot trading
        test_spot_trading()
        
        print("\n✅ All trading tests completed successfully")
        
    except Exception as e:
        print(f"\n❌ Main test failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()