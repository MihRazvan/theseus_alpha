# tests/test_profile_adjustment.py

import example_utils
from hyperliquid.utils import constants
from spot_profiler import SpotProfiler
from perp_profiler import PerpProfiler
from profile_adjusters import SpotProfileAdjuster, PerpProfileAdjuster

def test_profile_adjustment():
    try:
        # Setup connection
        address, info, exchange = example_utils.setup(constants.TESTNET_API_URL, skip_ws=True)
        
        # Ask user which type of trading they want to focus on
        print("\n=== Welcome to Theseus Alpha Trading System ===")
        print("1. Spot Trading")
        print("2. Perpetual Trading")
        choice = input("Which type of trading would you like to focus on? (1/2): ")
        
        if choice == "1":
            # Generate and adjust spot profile
            spot_profiler = SpotProfiler(address, info, exchange)
            spot_profile = spot_profiler.generate_profile()
            
            print("\n=== Current Spot Profile ===")
            print(spot_profiler.get_profile_summary())
            
            adjuster = SpotProfileAdjuster(spot_profile)
            preferences = adjuster.adjust_profile()
            
            print("\n=== Adjusted Preferences ===")
            print(f"Risk Tolerance: {preferences.risk_tolerance}")
            print(f"Trading Style: {preferences.trading_style}")
            print(f"Preferred Markets: {', '.join(preferences.preferred_markets)}")
            print(f"Time Horizon: {preferences.time_horizon}")
            print(f"Max Drawdown: {preferences.max_drawdown}%")
            print(f"Target Return: {preferences.target_return}%")
            print(f"Additional Notes: {preferences.custom_notes}")
            
        elif choice == "2":
            # Generate and adjust perpetual profile
            perp_profiler = PerpProfiler(address, info, exchange)
            perp_profile = perp_profiler.generate_profile()
            
            print("\n=== Current Perpetual Profile ===")
            print(perp_profiler.get_profile_summary())
            
            adjuster = PerpProfileAdjuster(perp_profile)
            preferences = adjuster.adjust_profile()
            
            print("\n=== Adjusted Preferences ===")
            print(f"Risk Tolerance: {preferences.risk_tolerance}")
            print(f"Trading Style: {preferences.trading_style}")
            print(f"Preferred Markets: {', '.join(preferences.preferred_markets)}")
            print(f"Time Horizon: {preferences.time_horizon}")
            print(f"Max Drawdown: {preferences.max_drawdown}%")
            print(f"Target Return: {preferences.target_return}%")
            print(f"Additional Notes: {preferences.custom_notes}")
        
        else:
            print("Invalid choice!")
            return False
        
        return True
        
    except Exception as e:
        print("❌ Error adjusting profile!")
        print("Error:", str(e))
        return False

if __name__ == "__main__":
    test_profile_adjustment()