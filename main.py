import logging
import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict

from openai import OpenAI
from hyperliquid.utils import constants
from theseus_alpha.utils.example_utils import setup
from theseus_alpha.profilers.spot_profiler import SpotProfiler
from theseus_alpha.profilers.perp_profiler import PerpProfiler
from theseus_alpha.adjusters.profile_adjusters import SpotProfileAdjuster, PerpProfileAdjuster
from theseus_alpha.cli.advisor import LLMTradingAdvisor
from theseus_alpha.trading.executor import TradingExecutor

# Constants
MIN_ORDER_SIZE_USD = 10
MAX_ORDER_SIZE_USD = 150
TRADE_DELAY = 2  # Seconds between trades

def print_header(msg: str):
    """Print a styled header."""
    print("\n" + "=" * 50)
    print(f"🔮 {msg}")
    print("=" * 50 + "\n")

def print_section(msg: str):
    """Print a styled section header."""
    print(f"\n📍 {msg}\n{'-' * 50}")

def execute_spot_trades(advice: Dict, address: str, info, exchange):
    """Execute spot trades based on the advice."""
    executor = TradingExecutor(address, info, exchange)

    trades = advice.get("spot_recommendations", [])
    if not trades:
        print("\n📢 No spot trades to execute.")
        return

    print_section("Executing Spot Trades")
    for i, trade in enumerate(trades, 1):
        print(f"\n🔄 Processing Trade {i}/{len(trades)}")

        execution = executor._execute_spot_trade(trade)

        # Display the trade result
        print("\n" + "=" * 50)
        print("Trade Details:")
        print(f"Asset: {trade['asset']}")
        print(f"Action: {'Buy' if trade['action'] == 'buy' else 'Sell'}")
        print(f"Size: ${trade.get('size_usd', 'N/A')}")
        print(f"Status: {'✅ SUCCESS' if execution.success else '❌ FAILED'}")
        if execution.error:
            print(f"Error: {execution.error}")
        print("=" * 50)

        # Wait before the next trade
        if i < len(trades):
            print(f"\n⏳ Waiting {TRADE_DELAY}s before next trade...")
            time.sleep(TRADE_DELAY)

def execute_perp_trades(advice: Dict, address: str, info, exchange):
    """Execute perpetual trades based on the advice."""
    executor = TradingExecutor(address, info, exchange)

    trades = advice.get("perp_recommendations", [])
    if not trades:
        print("\n📢 No perpetual trades to execute.")
        return

    print_section("Executing Perpetual Trades")
    for i, trade in enumerate(trades, 1):
        print(f"\n🔄 Processing Trade {i}/{len(trades)}")

        execution = executor._execute_perp_trade(trade)

        # Display the trade result
        print("\n" + "=" * 50)
        print("Trade Details:")
        print(f"Asset: {trade['asset']}")
        print(f"Direction: {'Long' if trade['direction'] == 'long' else 'Short'}")
        print(f"Size: ${trade.get('size_usd', 'N/A')}")
        print(f"Leverage: {trade.get('leverage', 'N/A')}x")
        print(f"Status: {'✅ SUCCESS' if execution.success else '❌ FAILED'}")
        if execution.error:
            print(f"Error: {execution.error}")
        print("=" * 50)

        # Wait before the next trade
        if i < len(trades):
            print(f"\n⏳ Waiting {TRADE_DELAY}s before next trade...")
            time.sleep(TRADE_DELAY)

def main():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    try:
        print_header("Welcome to Theseus Alpha Trading System")
        print("🕒 Current time:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        # Initialize OpenAI client
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if not openai_api_key:
            raise ValueError("❌ OPENAI_API_KEY environment variable not set")
        
        openai_client = OpenAI(api_key=openai_api_key)

        # Setup connection to HyperLiquid
        print_section("Connecting to HyperLiquid")
        address, info, exchange = setup(constants.TESTNET_API_URL, skip_ws=True)
        print(f"🔗 Connected to address: {address}")

        # Generate both profiles
        print_section("Generating Trading Profiles")
        spot_profiler = SpotProfiler(address, info, exchange)
        perp_profiler = PerpProfiler(address, info, exchange)

        spot_profile = spot_profiler.generate_profile()
        perp_profile = perp_profiler.generate_profile()

        # Display profiles
        print_section("Current Trading Profiles")
        print("\n=== 📈 Spot Trading Profile ===")
        print(spot_profiler.get_profile_summary())

        print("\n=== 📊 Perpetual Trading Profile ===")
        print(perp_profiler.get_profile_summary())

        # Ask user for preference
        print_section("Trading Preferences")
        print("Based on your profiles, would you like to:")
        print("1. Focus on Spot Trading Only")
        print("2. Focus on Perpetual Trading Only")
        print("3. Trade Both Markets")

        choice = input("\nSelect your preference (1/2/3): ").strip()

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
            return

        # Generate trading advice
        print_section("Getting Trading Advice")
        advisor = LLMTradingAdvisor(openai_client=openai_client)
        advice = advisor.generate_trading_advice(
            spot_profile=spot_profile if spot_preferences else None,
            perp_profile=perp_profile if perp_preferences else None,
            spot_preferences=spot_preferences,
            perp_preferences=perp_preferences
        )

        # Save advice for review
        advice_file = "trading_advice.json"
        Path(advice_file).write_text(json.dumps(advice, indent=2))
        print(f"📝 Trading advice saved to {advice_file}")

        # Execute spot trades if selected
        if spot_preferences:
            execute_spot_trades(advice, address, info, exchange)

        # Execute perpetual trades if selected
        if perp_preferences:
            execute_perp_trades(advice, address, info, exchange)

        print_header("Trading Session Complete")

    except Exception as e:
        logger.error(f"❌ Error in trading system: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()
