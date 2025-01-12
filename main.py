import logging
import os
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

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
    print("\n" + "="*50)
    print(f"🔮 {msg}")
    print("="*50 + "\n")

def print_section(msg: str):
    """Print a styled section header."""
    print(f"\n📍 {msg}\n{'-'*50}")

def print_trade_result(trade: Dict, success: bool, order_id: Optional[str], error: Optional[str]):
    """Print trade result with styling."""
    print("\n" + "="*50)
    print("Trade Details:")
    print(f"Asset: {trade['asset']}")
    print(f"Action: {trade['action'].upper()}")
    print(f"Size: ${trade.get('size_usd', 'N/A')}")
    print(f"Status: {'✅ SUCCESS' if success else '❌ FAILED'}")
    
    if trade.get('reasoning'):
        print("\nReasoning:")
        for reason in trade['reasoning']:
            print(f"• {reason}")
    
    if error:
        print(f"\nError: {error}")
    print("="*50)

def normalize_trade_size(size_usd: float) -> float:
    """Normalize trade size to be within limits."""
    if size_usd < MIN_ORDER_SIZE_USD:
        return MIN_ORDER_SIZE_USD
    elif size_usd > MAX_ORDER_SIZE_USD:
        return MAX_ORDER_SIZE_USD
    return size_usd

def prepare_trades(advice: Dict) -> List[Dict]:
    """Prepare trades with proper asset IDs and sizes."""
    trades = []
    
    # Process perpetual recommendations
    for rec in advice.get('perp_recommendations', []):
        trades.append({
            'asset': rec['asset'],
            'action': 'buy' if rec.get('direction') == 'long' else 'sell',
            'size_usd': normalize_trade_size(rec.get('size_usd', 10)),
            'leverage': rec.get('leverage', 1),  # Default to 1x if not specified
            'reasoning': rec.get('reasoning', [])
        })
    
    # Spot trades commented out for now
    # for rec in advice.get('spot_recommendations', []):
    #     if rec['asset'] == 'PURR/USDC':
    #         trades.append({
    #             'asset': 'PURR/USDC',
    #             'action': rec['action'],
    #             'size_usd': normalize_trade_size(rec.get('size_usd', 10)),
    #             'reasoning': rec.get('reasoning', [])
    #         })
    
    return trades

def get_user_preferences():
    """Get user preferences through terminal input."""
    preferences = {}
    
    print("\n=== Trading Preferences ===")
    
    # Risk tolerance
    print("\n📊 Risk Tolerance:")
    print("1. Conservative (smaller positions, focus on established tokens)")
    print("2. Moderate (balanced approach)")
    print("3. Aggressive (larger positions, willing to trade newer tokens)")
    risk = input("Select your risk tolerance (1-3): ").strip()
    preferences['risk_tolerance'] = ["conservative", "moderate", "aggressive"][int(risk)-1]
    
    # Trading style
    print("\n📈 Trading Style:")
    print("1. Value (long-term holding)")
    print("2. Swing (medium-term)")
    print("3. Active (short-term)")
    style = input("Select your trading style (1-3): ").strip()
    preferences['trading_style'] = ["value", "swing", "active"][int(style)-1]
    
    # Markets
    print("\n🏦 Preferred Markets:")
    markets = input("Enter markets (comma-separated, e.g. PURR/USDC): ").strip()
    preferences['preferred_markets'] = [m.strip() for m in markets.split(",")]
    
    # Time horizon
    print("\n⏱️ Time Horizon:")
    print("1. Short-term (days to weeks)")
    print("2. Medium-term (weeks to months)")
    print("3. Long-term (months to years)")
    horizon = input("Select your time horizon (1-3): ").strip()
    preferences['time_horizon'] = ["short", "medium", "long"][int(horizon)-1]
    
    # Risk parameters
    print("\n🎯 Risk Parameters:")
    max_drawdown = float(input("Maximum acceptable drawdown % (e.g. 10): ").strip())
    target_return = float(input("Target annual return % (e.g. 50): ").strip())
    preferences['max_drawdown'] = max_drawdown
    preferences['target_return'] = target_return
    
    return preferences

def main():
    # Setup logging
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
        
        # Generate profiles
        print_section("Generating Trading Profiles")
        spot_profiler = SpotProfiler(address, info, exchange)
        perp_profiler = PerpProfiler(address, info, exchange)
        
        spot_profile = spot_profiler.generate_profile()
        perp_profile = perp_profiler.generate_profile()
        
        # Print profile summaries
        print_section("Current Trading Profiles")
        print(spot_profiler.get_profile_summary())
        print("\n" + perp_profiler.get_profile_summary())
        
        # Get user preferences
        print_section("Profile Customization")
        preferences = get_user_preferences()
        
        # Create adjusters with user preferences
        spot_adjuster = SpotProfileAdjuster(spot_profile)
        perp_adjuster = PerpProfileAdjuster(perp_profile)
        
        # Apply preferences to profiles
        spot_preferences = spot_adjuster.adjust_profile_with_preferences(preferences)
        perp_preferences = perp_adjuster.adjust_profile_with_preferences(preferences)
        
        # Get trading advice
        print_section("Getting Trading Advice")
        advisor = LLMTradingAdvisor(openai_client=openai_client)
        advice = advisor.generate_trading_advice(
            spot_profile,
            perp_profile,
            spot_preferences,
            perp_preferences
        )
        
        # Save advice for review
        advice_file = "trading_advice.json"
        Path(advice_file).write_text(json.dumps(advice, indent=2))
        print(f"📝 Trading advice saved to {advice_file}")
        
        # Prepare trades
        trades = prepare_trades(advice)
        
        if not trades:
            print("\n📢 No valid trades to execute")
            return
            
        # Initialize executor
        executor = TradingExecutor(address, info, exchange)
        
        # Execute trades with delay
        print_section("Executing Trades")
        for i, trade in enumerate(trades, 1):
            print(f"\n🔄 Processing Trade {i}/{len(trades)}")
            
            # Execute trade
            execution = executor._execute_spot_trade(trade)
            
            # Print result
            print_trade_result(trade, execution.success, execution.order_id, execution.error)
            
            # Wait before next trade
            if i < len(trades):
                print(f"\n⏳ Waiting {TRADE_DELAY}s before next trade...")
                time.sleep(TRADE_DELAY)

        print_header("Trading Session Complete")

    except Exception as e:
        logger.error(f"❌ Error in trading system: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()