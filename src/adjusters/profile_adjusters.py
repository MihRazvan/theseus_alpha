from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod

@dataclass
class UserPreferences:
    risk_tolerance: str
    trading_style: str
    preferred_markets: List[str]
    time_horizon: str
    max_drawdown: float
    target_return: float
    custom_notes: str

class BaseProfileAdjuster(ABC):
    def __init__(self, profile):
        self.profile = profile
        self.preferences = None

    def get_user_input(self, prompt: str, options: Dict[str, str], default: str = None) -> str:
        print(f"\n{prompt}")
        for key, value in options.items():
            print(f"{key}. {value}")
        
        while True:
            choice = input(f"Select an option [{default}]: ").strip() if default else input("Select an option: ").strip()
            if not choice and default:
                return default
            if choice in options:
                return choice
            print("Invalid choice. Please try again.")

    def get_float_input(self, prompt: str, min_val: float, max_val: float, default: float = None) -> float:
        while True:
            if default is not None:
                value = input(f"{prompt} [{default}]: ").strip()
                if not value:
                    return default
            else:
                value = input(f"{prompt}: ").strip()
            
            try:
                float_val = float(value)
                if min_val <= float_val <= max_val:
                    return float_val
                print(f"Please enter a value between {min_val} and {max_val}")
            except ValueError:
                print("Please enter a valid number")

    def get_text_input(self, prompt: str, default: str = None) -> str:
        if default:
            value = input(f"{prompt} [{default}]: ").strip()
            return value if value else default
        return input(f"{prompt}: ").strip()

    @abstractmethod
    def adjust_profile(self) -> UserPreferences:
        pass

    def adjust_profile_with_preferences(self, preferences: Dict) -> UserPreferences:
        """Adjust profile using provided preferences."""
        return UserPreferences(
            risk_tolerance=preferences['risk_tolerance'],
            trading_style=preferences['trading_style'],
            preferred_markets=preferences['preferred_markets'],
            time_horizon=preferences['time_horizon'],
            max_drawdown=preferences['max_drawdown'],
            target_return=preferences['target_return'],
            custom_notes="Preferences set via user input"
        )

class SpotProfileAdjuster(BaseProfileAdjuster):
    def adjust_profile(self) -> UserPreferences:
        print("\n=== 📈 Spot Trading Profile Adjustment ===")
        print("Let's customize your spot trading preferences.")
        
        # Risk Tolerance
        risk_options = {
            "1": "Conservative (smaller positions, focus on established tokens)",
            "2": "Moderate (balanced approach)",
            "3": "Aggressive (larger positions, willing to trade newer tokens)"
        }
        detected_risk = "1" if self.profile.risk_tolerance == "conservative" else \
                       "2" if self.profile.risk_tolerance == "moderate" else "3"
        risk = self.get_user_input(
            f"Current Risk Profile: {self.profile.risk_tolerance.title()}\nDesired Risk Tolerance?",
            risk_options,
            detected_risk
        )
        
        # Trading Style
        style_options = {
            "1": "Value (long-term holding, fundamental analysis)",
            "2": "Swing (medium-term, technical + fundamental)",
            "3": "Active (short-term, technical analysis)"
        }
        detected_style = "1" if self.profile.trader_type == "hodler" else \
                        "2" if self.profile.trader_type == "swing_trader" else "3"
        style = self.get_user_input(
            f"Current Trading Style: {self.profile.trader_type.replace('_', ' ').title()}\nDesired Trading Style?",
            style_options,
            detected_style
        )
        
        # Market Preferences
        print("\nPreferred Markets (enter comma-separated symbols, e.g., 'BTC,ETH,USDT')")
        print(f"Current preferences: {', '.join(self.profile.trading_patterns.preferred_tokens or ['None'])}")
        markets = self.get_text_input("Enter preferred markets").upper().split(',')
        
        # Time Horizon
        horizon_options = {
            "1": "Short-term (days to weeks)",
            "2": "Medium-term (weeks to months)",
            "3": "Long-term (months to years)"
        }
        horizon = self.get_user_input("Preferred Time Horizon?", horizon_options)
        
        # Risk Parameters
        max_drawdown = self.get_float_input(
            "Maximum acceptable drawdown (%)", 
            1.0, 
            100.0, 
            20.0
        )
        
        target_return = self.get_float_input(
            "Target annual return (%)", 
            1.0, 
            1000.0, 
            50.0
        )
        
        # Additional Notes
        notes = self.get_text_input(
            "Any additional notes or preferences for your trading strategy?"
        )
        
        return UserPreferences(
            risk_tolerance=risk_options[risk].split()[0].lower(),
            trading_style=style_options[style].split()[0].lower(),
            preferred_markets=markets,
            time_horizon=horizon_options[horizon].split()[0].lower(),
            max_drawdown=max_drawdown,
            target_return=target_return,
            custom_notes=notes
        )

class PerpProfileAdjuster(BaseProfileAdjuster):
    def adjust_profile(self) -> UserPreferences:
        print("\n=== 📊 Perpetual Trading Profile Adjustment ===")
        print("Let's customize your perpetual trading preferences.")
        
        # Risk Tolerance (includes leverage consideration)
        risk_options = {
            "1": "Conservative (low leverage, tight stops)",
            "2": "Moderate (medium leverage, standard stops)",
            "3": "Aggressive (high leverage, wider stops)"
        }
        detected_risk = "1" if self.profile.risk_appetite == "conservative" else \
                       "2" if self.profile.risk_appetite == "moderate" else "3"
        risk = self.get_user_input(
            f"Current Risk Profile: {self.profile.risk_appetite.title()}\nDesired Risk Tolerance?",
            risk_options,
            detected_risk
        )
        
        # Trading Style
        style_options = {
            "1": "Scalping (very short-term, frequent trades)",
            "2": "Day Trading (intraday positions)",
            "3": "Swing (multi-day positions)",
            "4": "Position (longer-term trends)"
        }
        detected_style = "1" if self.profile.trader_type == "scalper" else \
                        "2" if self.profile.trader_type == "day_trader" else \
                        "3" if self.profile.trader_type == "swing_trader" else "4"
        style = self.get_user_input(
            f"Current Trading Style: {self.profile.trader_type.replace('_', ' ').title()}\nDesired Trading Style?",
            style_options,
            detected_style
        )
        
        # Market Preferences
        print("\nPreferred Markets (enter comma-separated symbols, e.g., 'BTC,ETH,SOL')")
        print(f"Current preferences: {', '.join(self.profile.trading_patterns.preferred_markets or ['None'])}")
        markets = self.get_text_input("Enter preferred markets").upper().split(',')
        
        # Time Horizon
        horizon_options = {
            "1": "Ultra-short (minutes to hours)",
            "2": "Intraday (hours to day)",
            "3": "Multi-day (days to weeks)"
        }
        horizon = self.get_user_input("Preferred Time Horizon?", horizon_options)
        
        # Risk Parameters
        max_drawdown = self.get_float_input(
            "Maximum acceptable drawdown (%)", 
            1.0, 
            100.0, 
            15.0
        )
        
        target_return = self.get_float_input(
            "Target annual return (%)", 
            1.0, 
            1000.0, 
            100.0
        )
        
        # Additional Notes
        notes = self.get_text_input(
            "Any additional notes or preferences for your trading strategy? (e.g., specific leverage limits, stop-loss preferences)"
        )
        
        return UserPreferences(
            risk_tolerance=risk_options[risk].split()[0].lower(),
            trading_style=style_options[style].split()[0].lower(),
            preferred_markets=markets,
            time_horizon=horizon_options[horizon].split()[0].lower(),
            max_drawdown=max_drawdown,
            target_return=target_return,
            custom_notes=notes
        )