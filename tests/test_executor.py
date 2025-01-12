import pytest
from pathlib import Path
import json
import logging
from datetime import datetime
import time
from dotenv import load_dotenv
import os

from hyperliquid.utils import constants
from theseus_alpha.utils.example_utils import setup
from theseus_alpha.trading.executor import TradingExecutor, TradeExecution

# Load environment variables
load_dotenv(Path(__file__).parent.parent / '.env')

def verify_trade_safety(address: str, info, trade_size_usd: float = 15.0) -> bool:
    """Verify it's safe to execute test trades."""
    try:
        user_state = info.user_state(address)
        available_balance = float(user_state.get('withdrawable', '0'))
        
        # Safety checks
        if available_balance < trade_size_usd * 2:  # Need 2x buffer
            print(f"❌ Insufficient balance. Need ${trade_size_usd * 2}, have ${available_balance}")
            return False
            
        if float(user_state['marginSummary']['accountValue']) < trade_size_usd * 4:
            print("❌ Total account value too low for safe testing")
            return False
            
        # Check existing positions
        positions = user_state.get('assetPositions', [])
        if len(positions) > 5:  # Arbitrary limit for testing
            print("❌ Too many open positions for safe testing")
            return False
            
        return True
        
    except Exception as e:
        print(f"Error in safety check: {str(e)}")
        return False

def test_real_trading():
    """Test actual trading with minimal test trades."""
    address, info, exchange = setup(constants.TESTNET_API_URL, skip_ws=True)
    
    print("\n=== Real Trading Test ===")
    print(f"Connected Address: {address}")
    
    # Safety verification
    is_safe = verify_trade_safety(address, info)
    if not is_safe:
        print("❌ Safety checks failed - skipping real trades")
        return
    
    print("✅ Safety checks passed")
    
    # Get current market prices
    mids = info.all_mids()
    eth_price = float(mids.get('ETH', 0))
    print(f"\nCurrent ETH Price: ${eth_price}")
    
    # Calculate exact size for $15 trade
    eth_size = round(15.0 / eth_price, 6)
    print(f"Test trade size: {eth_size} ETH (${15.0})")
    
    # Create test recommendation
    test_recommendations = {
        "spot_recommendations": [
            {
                "asset": "ETH",
                "action": "buy",
                "size": eth_size,
                "size_usd": 15.0,
                "reasoning": ["Test trade"]
            }
        ]
    }
    
    # Save recommendations
    test_file = "test_trading.json"
    with open(test_file, 'w') as f:
        json.dump(test_recommendations, f)
    
    try:
        # Create executor
        executor = TradingExecutor(address, info, exchange)
        
        # Record initial state
        initial_state = info.user_state(address)
        print("\nInitial State:")
        print(f"Account Value: ${initial_state['marginSummary']['accountValue']}")
        
        # Execute trade
        print("\nExecuting test trade...")
        executions = executor.execute_recommendations(test_file)
        
        # Wait for execution
        time.sleep(2)  # Wait for trade to settle
        
        # Verify execution
        print("\nVerifying execution:")
        for execution in executions:
            print(f"\n{execution.asset} Trade:")
            print(f"Success: {execution.success}")
            if execution.error:
                print(f"Error: {execution.error}")
            if execution.order_id:
                print(f"Order ID: {execution.order_id}")
                
                # Check order status
                order_status = info.query_order_by_oid(address, execution.order_id)
                print(f"Order Status: {order_status.get('status', 'unknown')}")
            
            # Validate execution
            is_valid = executor.validate_execution(execution)
            print(f"Validation: {'✅ Valid' if is_valid else '❌ Invalid'}")
        
        # Check final state
        final_state = info.user_state(address)
        print("\nFinal State:")
        print(f"Account Value: ${final_state['marginSummary']['accountValue']}")
        
    finally:
        # Cleanup
        if Path(test_file).exists():
            Path(test_file).unlink()
            
    print("\n✅ Real trading test completed")

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    try:
        test_real_trading()
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        raise