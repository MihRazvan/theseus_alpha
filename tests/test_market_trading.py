import logging
from pathlib import Path
import json
import time

from hyperliquid.utils import constants
from theseus_alpha.utils.setup_utils import setup_trading_environment, setup_leverage
from theseus_alpha.trading.utils import (
    normalize_price, 
    calculate_safe_size,
    validate_order,
    check_balance
)

def test_perp_trading():
    """Test perpetual trading with ETH-USD."""
    # Setup environment
    main_address, info, exchange = setup_trading_environment(
        constants.TESTNET_API_URL,
        skip_ws=True
    )
    
    print("\n=== Testing Perpetual Trading (ETH-USD) ===")
    
    try:
        # Check balance first
        balance, state = check_balance(info, main_address, "ETH", is_spot=False)
        print(f"\nAvailable Balance: ${balance}")
        
        # Set leverage first
        print("\nSetting up leverage...")
        leverage = 2
        if not setup_leverage(exchange, "ETH", leverage):
            print("❌ Failed to set leverage")
            return
        print("✅ Leverage set successfully")
        
        # Get metadata and context information first
        meta_ctxs = info.post("/info", {"type": "metaAndAssetCtxs"})
        print("\nFetching market data...")
        
        # Debug metadata
        universe = meta_ctxs[0].get('universe', [])
        eth_meta = next((asset for asset in universe if asset['name'] == 'ETH'), None)
        
        if not eth_meta:
            print("❌ ETH metadata not found")
            return
            
        eth_asset_idx = universe.index(eth_meta)
        eth_ctx = meta_ctxs[1][eth_asset_idx]
        
        # Get prices
        current_price = float(info.all_mids()["ETH"])
        oracle_price = float(eth_ctx['oraclePx'])
        mark_price = float(eth_ctx['markPx'])
        
        print(f"\nCurrent Price: ${current_price}")
        print(f"Oracle Price: ${oracle_price}")
        print(f"Mark Price: ${mark_price}")
        
        # Use oracle price
        normalized_price = oracle_price
        
        # Calculate size using a more conservative approach
        size, size_message = calculate_safe_size(
            info,
            "ETH",
            balance,
            normalized_price,
            leverage=leverage,
            safety_margin=0.50  # More conservative for testing
        )
        print(f"\nCalculated Size: {size_message}")
        
        # Validate the order
        is_valid, validation_message = validate_order(
            info,
            "ETH",
            True,  # Buy
            size,
            normalized_price,
            leverage=leverage
        )
        print(f"\nOrder Validation: {validation_message}")
        
        if not is_valid:
            print(f"❌ Order validation failed: {validation_message}")
            return
        
        print(f"\nPlacing limit order: Buy {size} ETH @ ${normalized_price}")
        
        order_result = exchange.order(
            "ETH",      # Asset
            True,       # Buy
            size,       # Amount
            normalized_price,  # Price
            {"limit": {"tif": "Gtc"}}  # Good-til-cancel
        )
        
        print("\nOrder Result:")
        print(json.dumps(order_result, indent=2))
        
        # # If order is placed, try to cancel it
        # if order_result["status"] == "ok":
        #     status = order_result["response"]["data"]["statuses"][0]
        #     if "resting" in status:
        #         time.sleep(1)  # Wait a bit
        #         print("\nCancelling test order...")
        #         cancel_result = exchange.cancel("ETH", status["resting"]["oid"])
        #         print("Cancel Result:")
        #         print(json.dumps(cancel_result, indent=2))
                
        print("✅ Perpetual trading test completed")
        
    except Exception as e:
        print(f"❌ Perpetual trading test failed: {str(e)}")
        print(f"Exception details: {type(e).__name__}")
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
        # Check USDC balance first
        balance, state = check_balance(info, main_address, "USDC", is_spot=True)
        if state and isinstance(state, list):
            print("\nSpot Balances:")
            for balance_info in state:
                if isinstance(balance_info, dict):
                    print(json.dumps(balance_info, indent=2))
                
        print(f"\nAvailable USDC Balance: ${balance}")

        
        if balance < 1:
            print(f"\nInsufficient USDC balance ({balance}). Skipping test.")
            return
            
        # Get and normalize price
        market_price = 0.46  # Fixed price for PURR/USDC
        normalized_price = normalize_price(info, "PURR", market_price, reference_type='mark')
        
        # Calculate safe size
        size, size_message = calculate_safe_size(
            info,
            "PURR",
            balance,
            normalized_price,
            leverage=1,  # Spot trading
            safety_margin=0.95
        )
        print(f"\nCalculated Size: {size_message}")
        
        # Validate the order
        is_valid, validation_message = validate_order(
            info,
            "PURR",
            True,  # Buy
            size,
            normalized_price
        )
        print(f"\nOrder Validation: {validation_message}")
        
        if not is_valid:
            print(f"❌ Order validation failed: {validation_message}")
            return
            
        print(f"\nPlacing test order: Buy {size} PURR @ ${normalized_price}")
        order_result = exchange.order(
            "PURR/USDC",  # Use proper spot pair format
            True,        # Buy
            size,       # Amount in PURR
            normalized_price,      # Price in USDC
            {"limit": {"tif": "Gtc"}}  # Good-til-cancel
        )
        
        print("\nOrder Result:")
        print(json.dumps(order_result, indent=2))
        
        # # Cancel if order is resting
        # if order_result["status"] == "ok":
        #     status = order_result["response"]["data"]["statuses"][0]
        #     if "resting" in status:
        #         time.sleep(1)  # Wait a bit
        #         cancel_result = exchange.cancel("PURR/USDC", status["resting"]["oid"])
        #         print("\nCancel Result:")
        #         print(json.dumps(cancel_result, indent=2))
                
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