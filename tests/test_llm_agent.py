import pytest
from typing import Dict, List, Optional
from openai import OpenAI
import json
from dotenv import load_dotenv
from pathlib import Path
import os
from hyperliquid.utils import constants

# Load the environment variables from .env file
load_dotenv(Path(__file__).parent.parent / '.env')
from theseus_alpha.utils.example_utils import setup
from theseus_alpha.profilers.spot_profiler import SpotProfiler
from theseus_alpha.profilers.perp_profiler import PerpProfiler
from theseus_alpha.adjusters.profile_adjusters import SpotProfileAdjuster, PerpProfileAdjuster
from theseus_alpha.cli.advisor import LLMTradingAdvisor

def test_full_trading_flow():
    """Test the complete flow from profile generation to LLM advice."""
    
    # Step 1: Setup connection and get profiles
    address, info, exchange = setup(constants.TESTNET_API_URL, skip_ws=True)
    assert address == "0x0a6A5Ba22da4e199bB5d8Cc04a84976C5930d049"  # Verify correct account
    
    print("\n=== Initial Setup ===")
    print(f"Connected to address: {address}")
    
    # Step 2: Generate profiles
    spot_profiler = SpotProfiler(address, info, exchange)
    perp_profiler = PerpProfiler(address, info, exchange)
    
    spot_profile = spot_profiler.generate_profile()
    perp_profile = perp_profiler.generate_profile()
    
    # Print profile summaries for verification
    print("\n=== Generated Profiles ===")
    print(f"Spot Profile - Trader Type: {spot_profile.trader_type}")
    print(f"Spot Profile - Risk Tolerance: {spot_profile.risk_tolerance}")
    print(f"Perp Profile - Trader Type: {perp_profile.trader_type}")
    print(f"Perp Profile - Risk Appetite: {perp_profile.risk_appetite}")
    
    assert spot_profile is not None
    assert perp_profile is not None
    
    # Step 3: Adjust profiles
    spot_adjuster = SpotProfileAdjuster(spot_profile)
    perp_adjuster = PerpProfileAdjuster(perp_profile)
    
    # Mock the input methods for both adjusters
    def mock_get_user_input(prompt: str, options: dict, default: str = None) -> str:
        if "Risk" in prompt:
            return "2"  # Moderate
        elif "Trading Style" in prompt:
            return "2"  # Swing trading
        elif "Time Horizon" in prompt:
            return "2"  # Medium-term
        return "2"  # Default response

    def mock_get_text_input(prompt: str, default: str = None) -> str:
        if "preferred markets" in prompt.lower():
            return "BTC,ETH,USDT"
        elif "additional notes" in prompt.lower():
            return "Test preferences"
        return "Test input"

    def mock_get_float_input(prompt: str, min_val: float, max_val: float, default: float = None) -> float:
        if "drawdown" in prompt.lower():
            return 20.0
        elif "return" in prompt.lower():
            return 50.0
        return min_val

    # Apply the mock methods to both adjusters
    spot_adjuster.get_user_input = mock_get_user_input
    spot_adjuster.get_text_input = mock_get_text_input
    spot_adjuster.get_float_input = mock_get_float_input
    
    perp_adjuster.get_user_input = mock_get_user_input
    perp_adjuster.get_text_input = mock_get_text_input
    perp_adjuster.get_float_input = mock_get_float_input
    
    print("\n=== Adjusting Profiles ===")
    spot_preferences = spot_adjuster.adjust_profile()
    perp_preferences = perp_adjuster.adjust_profile()
    
    print("\n=== Adjusted Preferences ===")
    print(f"Spot Preferences - Trading Style: {spot_preferences.trading_style}")
    print(f"Spot Preferences - Risk Tolerance: {spot_preferences.risk_tolerance}")
    print(f"Perp Preferences - Trading Style: {perp_preferences.trading_style}")
    print(f"Perp Preferences - Risk Tolerance: {perp_preferences.risk_tolerance}")
    
    assert spot_preferences is not None
    assert perp_preferences is not None
    
    # Step 4: Get LLM Trading Advice
    # Initialize OpenAI client
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("\n⚠️  OpenAI API key not found in .env file")
        print("Please ensure OPENAI_API_KEY is set in your .env file")
        return
        
    try:
        openai_client = OpenAI(api_key=api_key)
    except Exception as e:
        print(f"\n❌ Error initializing OpenAI client: {str(e)}")
        return
        
    advisor = LLMTradingAdvisor(openai_client=openai_client)
    advice = advisor.generate_trading_advice(
        spot_profile, perp_profile,
        spot_preferences, perp_preferences
    )
    
    print("\n=== LLM Trading Advice ===")
    print(json.dumps(advice, indent=2))
    
    # Verify advice structure
    assert 'spot_recommendations' in advice
    assert 'perp_recommendations' in advice
    assert 'overall_strategy' in advice
    
    # Verify recommendations content
    assert isinstance(advice['spot_recommendations'], list)
    assert isinstance(advice['perp_recommendations'], list)
    assert 'risk_assessment' in advice['overall_strategy']
    
    # Save output for manual verification
    with open('test_trading_advice.json', 'w') as f:
        json.dump(advice, f, indent=2)
    
    print("\n✅ Test completed successfully!")
    print("Trading advice saved to: test_trading_advice.json")

if __name__ == "__main__":
    test_full_trading_flow()