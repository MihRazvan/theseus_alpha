import logging
from pathlib import Path
import click
from openai import OpenAI
import json
from typing import Dict, Optional, Tuple

from hyperliquid.utils import constants
from theseus_alpha.utils.example_utils import setup
from theseus_alpha.profilers.spot_profiler import SpotProfiler
from theseus_alpha.profilers.perp_profiler import PerpProfiler
from theseus_alpha.adjusters.profile_adjusters import SpotProfileAdjuster, PerpProfileAdjuster

class LLMTradingAdvisor:
    def __init__(self, openai_client: Optional[OpenAI] = None):
        """Initialize the LLM trading advisor."""
        self.client = openai_client or OpenAI()
        self.logger = logging.getLogger(__name__)

    def generate_trading_advice(self, spot_profile, perp_profile, spot_preferences, perp_preferences) -> Dict:
        """Generate trading advice based on user profiles and preferences."""
        
        system_prompt = self._create_system_prompt()
        user_prompt = self._create_user_prompt(
            spot_profile, perp_profile, 
            spot_preferences, perp_preferences
        )

        try:
            response = self.client.chat.completions.create(
                model="gpt-4-0125-preview",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            self.logger.error(f"Error generating trading advice: {str(e)}")
            return {}

    def _create_system_prompt(self) -> str:
        """Create system prompt for the LLM."""
        return """You are an expert crypto trading advisor analyzing user profiles and preferences to provide 
        personalized trading recommendations. Focus on:

        1. Risk Management: Align recommendations with user's risk tolerance and preferences
        2. Portfolio Balance: Consider both spot and perpetual positions
        3. Market Analysis: Use current market conditions and user's trading patterns
        4. Clear Reasoning: Provide detailed explanations for each recommendation

        Provide advice in the following JSON format:
        {
            "spot_recommendations": [
                {
                    "asset": "token symbol",
                    "action": "buy/sell/hold",
                    "size_usd": float,
                    "reasoning": ["list of reasons"]
                }
            ],
            "perp_recommendations": [
                {
                    "asset": "token symbol",
                    "direction": "long/short",
                    "size_usd": float,
                    "leverage": int,
                    "reasoning": ["list of reasons"]
                }
            ],
            "overall_strategy": {
                "risk_assessment": "string",
                "portfolio_balance": "string",
                "key_considerations": ["list of points"]
            }
        }"""

    def _create_user_prompt(self, spot_profile, perp_profile, spot_preferences, perp_preferences) -> str:
        """Create user prompt with profile and preference information."""
        return f"""Please analyze these user profiles and preferences to provide trading recommendations:

        Spot Trading Profile:
        - Trader Type: {spot_profile.trader_type}
        - Risk Tolerance: {spot_profile.risk_tolerance}
        - Experience Level: {spot_profile.experience_level}
        - Asset Diversity: {spot_profile.risk_metrics.asset_diversity}
        - Portfolio Concentration: {spot_profile.risk_metrics.portfolio_concentration}

        Spot Preferences:
        - Risk Tolerance: {spot_preferences.risk_tolerance}
        - Trading Style: {spot_preferences.trading_style}
        - Preferred Markets: {', '.join(spot_preferences.preferred_markets)}
        - Time Horizon: {spot_preferences.time_horizon}
        - Target Return: {spot_preferences.target_return}%

        Perpetual Trading Profile:
        - Trader Type: {perp_profile.trader_type}
        - Risk Appetite: {perp_profile.risk_appetite}
        - Experience Level: {perp_profile.experience_level}
        - Average Leverage: {perp_profile.risk_metrics.avg_leverage}
        - Win Rate: {perp_profile.trading_patterns.win_rate}

        Perpetual Preferences:
        - Risk Tolerance: {perp_preferences.risk_tolerance}
        - Trading Style: {perp_preferences.trading_style}
        - Preferred Markets: {', '.join(perp_preferences.preferred_markets)}
        - Time Horizon: {perp_preferences.time_horizon}
        - Target Return: {perp_preferences.target_return}%

        Please provide comprehensive trading recommendations considering both spot and perpetual markets,
        ensuring alignment with the user's risk tolerance and preferences."""

def get_profiles() -> Tuple[bool, object, object]:
    """Get user profiles using existing profilers."""
    try:
        address, info, exchange = setup(constants.TESTNET_API_URL, skip_ws=True)
        
        # Generate profiles
        spot_profiler = SpotProfiler(address, info, exchange)
        perp_profiler = PerpProfiler(address, info, exchange)
        
        spot_profile = spot_profiler.generate_profile()
        perp_profile = perp_profiler.generate_profile()
        
        return True, spot_profile, perp_profile
    except Exception as e:
        logging.error(f"Error getting profiles: {str(e)}")
        return False, None, None

def adjust_profiles(spot_profile, perp_profile) -> Tuple[bool, object, object]:
    """Adjust profiles using existing adjusters."""
    try:
        spot_adjuster = SpotProfileAdjuster(spot_profile)
        perp_adjuster = PerpProfileAdjuster(perp_profile)
        
        spot_preferences = spot_adjuster.adjust_profile()
        perp_preferences = perp_adjuster.adjust_profile()
        
        return True, spot_preferences, perp_preferences
    except Exception as e:
        logging.error(f"Error adjusting profiles: {str(e)}")
        return False, None, None

@click.group()
def cli():
    """Theseus Alpha Trading Assistant CLI"""
    pass

@cli.command()
@click.option('--output', '-o', type=click.Path(), help='Output file for trading advice')
def analyze(output):
    """Analyze user profile and generate trading advice."""
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    click.echo("🔍 Analyzing trading profiles...")
    
    # Get profiles
    success, spot_profile, perp_profile = get_profiles()
    if not success:
        click.echo("❌ Failed to retrieve trading profiles")
        return
    
    click.echo("✅ Retrieved trading profiles")
    click.echo("\n📊 Current Profile Summary:")
    click.echo(f"Spot Trader Type: {spot_profile.trader_type}")
    click.echo(f"Perp Trader Type: {perp_profile.trader_type}")
    
    # Adjust profiles
    success, spot_preferences, perp_preferences = adjust_profiles(spot_profile, perp_profile)
    if not success:
        click.echo("❌ Failed to adjust profiles")
        return
    
    click.echo("✅ Adjusted trading profiles")
    
    # Generate trading advice
    advisor = LLMTradingAdvisor()
    advice = advisor.generate_trading_advice(
        spot_profile, perp_profile,
        spot_preferences, perp_preferences
    )
    
    if not advice:
        click.echo("❌ Failed to generate trading advice")
        return
    
    # Output results
    click.echo("\n📈 Trading Recommendations:")
    click.echo(json.dumps(advice, indent=2))
    
    if output:
        output_path = Path(output)
        output_path.write_text(json.dumps(advice, indent=2))
        click.echo(f"\n💾 Saved trading advice to {output}")

if __name__ == '__main__':
    cli()