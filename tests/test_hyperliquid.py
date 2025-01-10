import example_utils
from hyperliquid.utils import constants

def test_hyperliquid_connection():
    try:
        # Setup connection using example utils
        address, info, exchange = example_utils.setup(constants.TESTNET_API_URL, skip_ws=True)
        
        # Try to get user state
        user_state = info.user_state(address)
        
        print("✅ Hyperliquid Connection Successful!")
        print(f"Connected Address: {address}")
        print("Account Value:", user_state["marginSummary"]["accountValue"])
        return True
        
    except Exception as e:
        print("❌ Hyperliquid Connection Failed!")
        print("Error:", str(e))
        return False

if __name__ == "__main__":
    test_hyperliquid_connection()