# tests/test_real_trading.py
import logging
from pathlib import Path
import json
import time
from datetime import datetime

from hyperliquid.utils import constants
from theseus_alpha.utils.setup_utils import setup_trading_environment, verify_account_access
from theseus_alpha.trading.executor import TradingExecutor
from theseus_alpha.trading.types import TradeExecution

def verify_trade_safety(info, address: str, trade_size_usd: float = 15.0) -> bool:
    """Verify it's safe to execute a test trade."""
    try:
        user_state = info.user_state(address)
        available_balance = float(user_state.get('withdrawable', '0'))
        
        print("\nSafety Check:")
        print(f"Available Balance: ${available_balance}")
        print(f"Required Balance: ${trade_size_usd * 2}")  # 2x buffer
        
        if available_balance < trade_size_usd * 2:
            print("❌ Insufficient balance for safe testing")
            return False
            
        # Check existing positions
        positions = user_state.get('assetPositions', [])
        print(f"Current Open Positions: {len(positions)}")
        
        return True
        
    except Exception as e:
        print(f"Error in safety check: {str(e)}")
        return False

def test_real_trading():
    """Test actual trading with minimal test trades."""
    try:
        # Setup trading environment
        main_address, info, exchange = setup_trading_environment(
            constants.TESTNET_API_URL,
            skip_ws=True
        )
        
        print("\n=== Real Trading Test ===")
        
        # Verify API access
        if not verify_account_access(main_address, info, exchange):
            print("❌ Failed to verify API access")
            return
            
        # Verify trade safety
        if not verify_trade_safety(info, main_address):
            print("❌ Failed safety checks")
            return
            
        print("\n✅ Setup and safety checks passed")
        
        # Get current market state
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
                    "reasoning": ["Test trade with minimal size"]
                }
            ]
        }
        
        # Save test recommendations
        test_file = "test_trade.json"
        with open(test_file, 'w') as f:
            json.dump(test_recommendations, f)
            
        try:
            # Create executor with API wallet
            executor = TradingExecutor(main_address, info, exchange)
            
            # Record initial state
            initial_state = info.user_state(main_address)
            print(f"\nInitial Account Value: ${initial_state['marginSummary']['accountValue']}")
            
            # Execute trade
            print("\nExecuting test trade...")
            executions = executor.execute_recommendations(test_file)
            
            # Wait for settlement
            time.sleep(2)
            
            # Verify executions
            print("\nVerifying execution:")
            for execution in executions:
                print(f"\n{execution.asset} Trade:")
                print(f"Success: {execution.success}")
                if execution.error:
                    print(f"Error: {execution.error}")
                if execution.order_id:
                    print(f"Order ID: {execution.order_id}")
                    
                    # Check order status
                    order_status = info.query_order_by_oid(main_address, execution.order_id)
                    print(f"Order Status: {order_status.get('status', 'unknown')}")
                
                # Validate execution
                is_valid = executor.validate_execution(execution)
                print(f"Validation: {'✅ Valid' if is_valid else '❌ Invalid'}")
            
            # Check final state
            final_state = info.user_state(main_address)
            print(f"\nFinal Account Value: ${final_state['marginSummary']['accountValue']}")
            
            # Calculate and show P&L
            pnl = float(final_state['marginSummary']['accountValue']) - float(initial_state['marginSummary']['accountValue'])
            print(f"Trade P&L: ${pnl:,.2f}")
            
        finally:
            # Cleanup
            if Path(test_file).exists():
                Path(test_file).unlink()
        
        print("\n✅ Real trading test completed")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        raise

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_real_trading()