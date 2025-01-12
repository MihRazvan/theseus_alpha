# tests/test_api_setup.py
import logging
from hyperliquid.utils import constants
from theseus_alpha.utils.setup_utils import setup_trading_environment, verify_account_access

def test_api_setup():
    """Test API wallet setup and permissions."""
    try:
        # Setup environment
        main_address, info, exchange = setup_trading_environment(
            constants.TESTNET_API_URL,
            skip_ws=True
        )
        
        print("\n=== Testing API Wallet Setup ===")
        
        # Verify access
        if not verify_account_access(main_address, info, exchange):
            print("❌ Failed to verify account access")
            return
            
        print("✅ Account access verified")
        
        # Test a simple query
        print("\nTesting market data access...")
        mids = info.all_mids()
        eth_price = float(mids.get('ETH', 0))
        print(f"Current ETH Price: ${eth_price}")
        
        # Calculate minimum trade size
        eth_size = round(15.0 / eth_price, 6)
        print(f"\nMinimum trade size for $15:")
        print(f"ETH: {eth_size} ETH")
        
        print("\n✅ API wallet setup test completed successfully")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        raise

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_api_setup()