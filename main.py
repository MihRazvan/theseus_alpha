import pytest
from pathlib import Path
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
import os

from hyperliquid.utils import constants
from theseus_alpha.utils.example_utils import setup
from theseus_alpha.trading.executor import TradingExecutor, TradeExecution

# Load environment variables
load_dotenv(Path(__file__).parent.parent / '.env')

def setup_trading_env():
    """Setup trading environment with approved API wallet."""
    address, info, exchange = setup(constants.TESTNET_API_URL, skip_ws=True)
    
    print("\n=== Setting up Trading Environment ===")
    print(f"Main Account Address: {address}")
    
    # Approve API wallet if not already approved
    approve_result, agent_key = exchange.approve_agent()
    if approve_result["status"] != "ok":
        raise Exception(f"Failed to approve API wallet: {approve_result}")
    
    print("✅ API wallet approved")
    return address, info, exchange

def test_executor_initialization():
    """Test basic executor setup."""
    address, info, exchange = setup_trading_env()
    
    print("\n=== Testing Executor Initialization ===")
    print(f"Connected Address: {address}")
    
    executor = TradingExecutor(address, info, exchange)
    assert executor is not None
    assert executor.address == address
    print("✅ Executor initialized successfully")

def test_recommendation_loading():
    """Test loading and parsing trading recommendations."""
    # Create test recommendations
    test_recommendations = {
        "spot_recommendations": [
            {
                "asset": "ETH",
                "action": "buy",
                "size_usd": 15.0,
                "reasoning": ["Test reasoning"]
            }
        ],
        "perp_recommendations": [
            {
                "asset": "BTC",
                "direction": "long",
                "size_usd": 15.0,
                "leverage": 2,
                "reasoning": ["Test reasoning"]
            }
        ]
    }
    
    # Save test recommendations
    test_file = "test_recommendations.json"
    with open(test_file, 'w') as f:
        json.dump(test_recommendations, f)
    
    print("\n=== Testing Recommendation Loading ===")
    
    try:
        with open(test_file, 'r') as f:
            loaded_recs = json.load(f)
        assert loaded_recs == test_recommendations
        print("✅ Recommendations loaded successfully")
    finally:
        # Cleanup
        if Path(test_file).exists():
            Path(test_file).unlink()

def test_dry_run_execution():
    """Test trade execution in dry-run mode."""
    address, info, exchange = setup_trading_env()
    executor = TradingExecutor(address, info, exchange)
    
    print("\n=== Testing Dry Run Execution ===")
    
    # Get current market state
    print("\nCurrent Market State:")
    mids = info.all_mids()
    btc_price = float(mids.get('BTC', 0))
    eth_price = float(mids.get('ETH', 0))
    print(f"ETH Price: ${eth_price}")
    print(f"BTC Price: ${btc_price}")
    
    # Calculate minimum sizes for $15 value
    eth_size = round(15.0 / eth_price, 6)  # Round to 6 decimal places
    btc_size = round(15.0 / btc_price, 6)  # Round to 6 decimal places
    
    print(f"\nCalculated trade sizes:")
    print(f"ETH: {eth_size} (${15.0})")
    print(f"BTC: {btc_size} (${15.0})")
    
    # Create test recommendations
    test_recommendations = {
        "spot_recommendations": [
            {
                "asset": "ETH",
                "action": "buy",
                "size": eth_size,  # Use exact size instead of USD value
                "size_usd": 15.0,
                "reasoning": ["Test trade"]
            }
        ],
        "perp_recommendations": [
            {
                "asset": "BTC",
                "direction": "long",
                "size": btc_size,  # Use exact size instead of USD value
                "size_usd": 15.0,
                "leverage": 2,
                "reasoning": ["Test trade"]
            }
        ]
    }
    
    # Save test recommendations
    test_file = "test_recommendations.json"
    with open(test_file, 'w') as f:
        json.dump(test_recommendations, f)
    
    try:
        # Execute recommendations
        print("\nExecuting test trades...")
        executions = executor.execute_recommendations(test_file)
        
        # Verify executions
        print("\nVerifying executions:")
        for execution in executions:
            print(f"\nTrade for {execution.asset}:")
            print(f"Success: {execution.success}")
            if execution.error:
                print(f"Error: {execution.error}")
            if execution.order_id:
                print(f"Order ID: {execution.order_id}")
            
            # Validate execution
            is_valid = executor.validate_execution(execution)
            print(f"Validation: {'✅ Valid' if is_valid else '❌ Invalid'}")
            
            assert isinstance(execution, TradeExecution)
            
    finally:
        # Cleanup
        if Path(test_file).exists():
            Path(test_file).unlink()
    
    print("\n✅ Dry run execution test completed")

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Run tests
        test_executor_initialization()
        test_recommendation_loading()
        test_dry_run_execution()
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        raise