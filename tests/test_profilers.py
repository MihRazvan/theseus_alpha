# tests/test_profilers.py

import example_utils
from hyperliquid.utils import constants
from spot_profiler import SpotProfiler
from perp_profiler import PerpProfiler

def test_profiles():
    try:
        # Setup connection
        address, info, exchange = example_utils.setup(constants.TESTNET_API_URL, skip_ws=True)
        
        print("\n=== Testing Spot Profile ===")
        spot_profiler = SpotProfiler(address, info, exchange)
        print(spot_profiler.get_profile_summary())
        
        print("\n=== Testing Perpetual Profile ===")
        perp_profiler = PerpProfiler(address, info, exchange)
        print(perp_profiler.get_profile_summary())
        
        return True
        
    except Exception as e:
        print("❌ Error generating profiles!")
        print("Error:", str(e))
        return False

if __name__ == "__main__":
    test_profiles()