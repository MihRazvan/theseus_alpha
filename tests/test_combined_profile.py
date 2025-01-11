# tests/test_combined_profile.py

import example_utils
from hyperliquid.utils import constants
from spot_profiler import SpotProfiler
from perp_profiler import PerpProfiler
from profile_adjusters import SpotProfileAdjuster, PerpProfileAdjuster

def test_combined_profiles():
    try:
        # Setup connection
        address, info, exchange = example_utils.setup(constants.TESTNET_API_URL, skip_ws=True)
        
        print("\n=== Welcome to Theseus Alpha Trading System ===")
        print("\nAnalyzing your complete trading profile...\n")

        # Generate both profiles first
        spot_profiler = SpotProfiler(address, info, exchange)
        perp_profiler = PerpProfiler(address, info, exchange)
        
        spot_profile = spot_profiler.generate_profile()
        perp_profile = perp_profiler.generate_profile()
        
        # Show complete analysis
        print("=== Your Current Trading Profiles ===")
        print("\n=== 📈 Spot Trading Profile ===")
        print(spot_profiler.get_profile_summary())
        
        print("\n=== 📊 Perpetual Trading Profile ===")
        print(perp_profiler.get_profile_summary())
        
        # Now ask about preferences
        print("\n=== Trading Preferences ===")
        print("Based on your profiles, would you like the agent to:")
        print("1. Focus on Spot Trading Only")
        print("2. Focus on Perpetual Trading Only")
        print("3. Trade Both Markets (Recommended for your profile)")
        
        choice = input("\nSelect your preference (1/2/3): ")
        
        spot_preferences = None
        perp_preferences = None
        
        if choice == "1":
            adjuster = SpotProfileAdjuster(spot_profile)
            spot_preferences = adjuster.adjust_profile()
        elif choice == "2":
            adjuster = PerpProfileAdjuster(perp_profile)
            perp_preferences = adjuster.adjust_profile()
        elif choice == "3":
            print("\nLet's configure both trading strategies...")
            
            print("\n=== Spot Trading Configuration ===")
            spot_adjuster = SpotProfileAdjuster(spot_profile)
            spot_preferences = spot_adjuster.adjust_profile()
            
            print("\n=== Perpetual Trading Configuration ===")
            perp_adjuster = PerpProfileAdjuster(perp_profile)
            perp_preferences = perp_adjuster.adjust_profile()
        else:
            print("Invalid choice!")
            return False, None, None
        
        # Final Summary
        print("\n=== Final Trading Strategy Summary ===")
        if spot_preferences:
            print("\n📈 Spot Trading Strategy:")
            print(f"- Focus: {spot_preferences.trading_style} trading")
            print(f"- Risk Level: {spot_preferences.risk_tolerance}")
            print(f"- Markets: {', '.join(spot_preferences.preferred_markets)}")
            print(f"- Time Horizon: {spot_preferences.time_horizon}")
            print(f"- Target Annual Return: {spot_preferences.target_return}%")
            
        if perp_preferences:
            print("\n📊 Perpetual Trading Strategy:")
            print(f"- Focus: {perp_preferences.trading_style} trading")
            print(f"- Risk Level: {perp_preferences.risk_tolerance}")
            print(f"- Markets: {', '.join(perp_preferences.preferred_markets)}")
            print(f"- Time Horizon: {perp_preferences.time_horizon}")
            print(f"- Target Annual Return: {perp_preferences.target_return}%")
        
        return True, spot_preferences, perp_preferences
        
    except Exception as e:
        print("❌ Error analyzing profiles!")
        print("Error:", str(e))
        return False, None, None

if __name__ == "__main__":
    success, spot_prefs, perp_prefs = test_combined_profiles()