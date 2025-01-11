from dotenv import load_dotenv
from pathlib import Path
import json
import logging
from datetime import datetime
from openai import OpenAI

from hyperliquid.utils import constants
from theseus_alpha.utils.example_utils import setup
from theseus_alpha.profilers.spot_profiler import SpotProfiler
from theseus_alpha.profilers.perp_profiler import PerpProfiler
from theseus_alpha.adjusters.profile_adjusters import SpotProfileAdjuster, PerpProfileAdjuster
from theseus_alpha.cli.advisor import LLMTradingAdvisor

def main():
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

    # Load environment variables
    load_dotenv(Path(__file__).parent / '.env')
    
    print("\n=== 🚀 Starting Theseus Alpha Trading System ===\n")
    
    try:
        # Step 1: Setup Connection
        print("Connecting to Hyperliquid...")
        address, info, exchange = setup(constants.TESTNET_API_URL, skip_ws=True)
        print(f"✅ Connected to account: {address}\n")
        
        # Step 2: Generate Profiles
        print("Analyzing trading profiles...")
        spot_profiler = SpotProfiler(address, info, exchange)
        perp_profiler = PerpProfiler(address, info, exchange)
        
        spot_profile = spot_profiler.generate_profile()
        perp_profile = perp_profiler.generate_profile()
        
        print("\n=== 📊 Current Trading Profile ===")
        print(f"Spot Trading:")
        print(f"- Trader Type: {spot_profile.trader_type}")
        print(f"- Risk Tolerance: {spot_profile.risk_tolerance}")
        print(f"- Experience Level: {spot_profile.experience_level}")
        
        print(f"\nPerpetual Trading:")
        print(f"- Trader Type: {perp_profile.trader_type}")
        print(f"- Risk Appetite: {perp_profile.risk_appetite}")
        print(f"- Experience Level: {perp_profile.experience_level}")
        
        # Step 3: Adjust Profiles
        print("\n=== 🎯 Profile Adjustment ===")
        print("Let's customize your trading preferences...")
        
        spot_adjuster = SpotProfileAdjuster(spot_profile)
        perp_adjuster = PerpProfileAdjuster(perp_profile)
        
        spot_preferences = spot_adjuster.adjust_profile()
        perp_preferences = perp_adjuster.adjust_profile()
        
        # Step 4: Generate Trading Advice
        print("\n=== 🤖 Generating Trading Advice ===")
        openai_client = OpenAI()
        advisor = LLMTradingAdvisor(openai_client=openai_client)
        
        advice = advisor.generate_trading_advice(
            spot_profile, perp_profile,
            spot_preferences, perp_preferences
        )
        
        # Save output with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"trading_advice_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(advice, f, indent=2)
        
        print("\n=== 📈 Trading Recommendations Generated ===")
        print("Detailed advice has been saved to:", filename)
        
        # Print summary
        print("\nKey Recommendations Summary:")
        for rec in advice['spot_recommendations']:
            print(f"- Spot {rec['asset']}: {rec['action'].upper()} ${rec['size_usd']:,.2f}")
        
        for rec in advice['perp_recommendations']:
            print(f"- Perp {rec['asset']}: {rec['direction'].upper()} ${rec['size_usd']:,.2f} ({rec['leverage']}x)")
        
        print(f"\nRisk Assessment: {advice['overall_strategy']['risk_assessment']}")
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        print("\n❌ Error occurred during execution. Check the logs for details.")
        return
    
    print("\n✅ Analysis completed successfully!")

if __name__ == "__main__":
    main()