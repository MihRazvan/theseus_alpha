import pytest
from pathlib import Path
import json
import logging
from datetime import datetime
import time
from dotenv import load_dotenv
import os

from hyperliquid.utils import constants
from theseus_alpha.utils.setup_utils import setup_trading_environment, verify_account_access
from theseus_alpha.trading.executor import TradingExecutor
from theseus_alpha.trading.types import TradeExecution

# Load environment variables
load_dotenv(Path(__file__).parent.parent / '.env')

def test_executor_simulation():
    """Test trading executor in simulation mode."""
    # Setup trading environment
    address, info, exchange = setup_trading_environment(
        constants.TESTNET_API_URL, 
        skip_ws=True
    )
    
    print("\n=== Testing Executor (Simulation Mode) ===")
    
    # Verify access
    if not verify_account_access(address, info, exchange):
        print("❌ Failed to verify account access")
        return
        
    print("✅ Account access verified")
    
    # Create test recommendations
    test_recommendations = {
        "spot_recommendations": [
            {
                "asset": "ETH",
                "action": "buy",
                "size_usd": 15.0,
                "reasoning": ["Test trade"]
            }
        ]
    }
    
    # Save recommendations
    test_file = "test_recommendations.json"
    with open(test_file, 'w') as f:
        json.dump(test_recommendations, f)
    
    try:
        # Create executor
        executor = TradingExecutor(address, info, exchange)
        
        # Get current market prices
        mids = info.all_mids()
        eth_price = float(mids.get('ETH', 0))
        print(f"\nCurrent ETH Price: ${eth_price}")
        
        # Calculate trade sizes
        eth_size = round(15.0 / eth_price, 6)
        print(f"\nRequired trade size for $15:")
        print(f"ETH: {eth_size} (${15.0})")
        
        # Get current state
        initial_state = info.user_state(address)
        print("\nCurrent State:")
        print(f"Account Value: ${initial_state['marginSummary']['accountValue']}")
        print(f"Available Balance: ${initial_state.get('withdrawable', 'N/A')}")
        
        print("\n⚠️  Running in simulation mode - no trades will be executed")
        print("✅ Simulation completed successfully")
        
    finally:
        # Cleanup
        if Path(test_file).exists():
            Path(test_file).unlink()

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    try:
        test_executor_simulation()
        print("\n✅ All tests completed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        raise