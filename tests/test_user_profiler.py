# tests/test_user_profiler.py

import example_utils
from hyperliquid.utils import constants
from profiler import UserProfiler 

def test_user_profiling():
    try:
        # Setup connection
        address, info, exchange = example_utils.setup(constants.TESTNET_API_URL, skip_ws=True)
        
        # Create and run profiler
        profiler = UserProfiler(address, info, exchange)
        print(profiler.get_profile_summary())
        
        return True
        
    except Exception as e:
        print("❌ Error generating user profile!")
        print("Error:", str(e))
        return False

if __name__ == "__main__":
    test_user_profiling()