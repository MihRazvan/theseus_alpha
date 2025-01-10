from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import statistics
from collections import defaultdict

@dataclass
class TradeMetrics:
    total_volume: float = 0.0
    avg_leverage: float = 0.0
    max_leverage: float = 0.0
    avg_position_size: float = 0.0
    max_position_size: float = 0.0
    win_rate: float = 0.0
    avg_holding_time: timedelta = timedelta(0)
    preferred_tokens: List[str] = None
    trade_frequency: str = ""  # "high", "medium", "low"
    risk_profile: str = ""     # "aggressive", "moderate", "conservative"
    favorite_trade_times: List[str] = None
    typical_position_count: int = 0

@dataclass
class UserProfile:
    address: str
    metrics: TradeMetrics
    trading_style: str  # "day_trader", "swing_trader", "position_trader"
    experience_level: str  # "beginner", "intermediate", "advanced"
    last_updated: datetime

class UserProfiler:
    def __init__(self, address: str, info, exchange):
        """Initialize the user profiler with Hyperliquid connection."""
        self.address = address
        self.info = info
        self.exchange = exchange
        self.current_state = None
        self.historical_trades = None
        self.metrics = TradeMetrics()

    def _fetch_data(self) -> None:
        """Fetch all necessary data for analysis."""
        try:
            # Get current account state
            self.current_state = self.info.user_state(self.address)
            
            # Get historical trades (last 30 days)
            start_time = int((datetime.now() - timedelta(days=30)).timestamp() * 1000)
            self.historical_trades = self.info.user_fills_by_time(
                self.address, 
                start_time=start_time
            )
        except Exception as e:
            raise Exception(f"Failed to fetch user data: {str(e)}")

    def _analyze_leverage_patterns(self) -> None:
        """Analyze historical leverage usage."""
        leverages = []
        for position in self.current_state.get("assetPositions", []):
            if "position" in position and "leverage" in position["position"]:
                leverages.append(float(position["position"]["leverage"]["value"]))
        
        if leverages:
            self.metrics.avg_leverage = statistics.mean(leverages)
            self.metrics.max_leverage = max(leverages)

    def _analyze_preferred_tokens(self) -> None:
        """Identify most frequently traded tokens."""
        token_volumes = defaultdict(float)
        for trade in self.historical_trades:
            token = trade["coin"]
            size = float(trade["sz"])
            price = float(trade["px"])
            token_volumes[token] += size * price

        # Sort tokens by volume and get top 3
        sorted_tokens = sorted(token_volumes.items(), key=lambda x: x[1], reverse=True)
        self.metrics.preferred_tokens = [token for token, _ in sorted_tokens[:3]]

    def _analyze_trade_frequency(self) -> None:
        """Determine trading frequency pattern."""
        if not self.historical_trades:
            self.metrics.trade_frequency = "low"
            return

        trades_per_day = len(self.historical_trades) / 30  # Using 30 days window
        
        if trades_per_day >= 5:
            self.metrics.trade_frequency = "high"
        elif trades_per_day >= 1:
            self.metrics.trade_frequency = "medium"
        else:
            self.metrics.trade_frequency = "low"

    def _analyze_risk_profile(self) -> None:
        """Determine risk profile based on leverage and position sizes."""
        if self.metrics.max_leverage >= 10:
            self.metrics.risk_profile = "aggressive"
        elif self.metrics.max_leverage >= 5:
            self.metrics.risk_profile = "moderate"
        else:
            self.metrics.risk_profile = "conservative"

    def _analyze_trading_times(self) -> None:
        """Analyze preferred trading times."""
        hour_counts = defaultdict(int)
        for trade in self.historical_trades:
            trade_time = datetime.fromtimestamp(trade["time"]/1000)
            hour = trade_time.hour
            hour_counts[hour] += 1

        # Get top 3 most active hours
        sorted_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)
        self.metrics.favorite_trade_times = [
            f"{hour:02d}:00" for hour, _ in sorted_hours[:3]
        ]

    def _calculate_win_rate(self) -> None:
        """Calculate win rate from closed positions."""
        if not self.historical_trades:
            self.metrics.win_rate = 0
            return

        profitable_trades = sum(
            1 for trade in self.historical_trades 
            if float(trade.get("closedPnl", 0)) > 0
        )
        self.metrics.win_rate = profitable_trades / len(self.historical_trades)

    def _determine_trading_style(self) -> str:
        """Determine overall trading style."""
        if self.metrics.trade_frequency == "high":
            return "day_trader"
        elif self.metrics.trade_frequency == "medium":
            return "swing_trader"
        else:
            return "position_trader"

    def _determine_experience_level(self) -> str:
        """Determine trader experience level."""
        # Points system for experience
        points = 0
        
        # Volume based points (0-3)
        if self.metrics.total_volume > 100000:
            points += 3
        elif self.metrics.total_volume > 10000:
            points += 2
        elif self.metrics.total_volume > 1000:
            points += 1

        # Win rate based points (0-3)
        if self.metrics.win_rate > 0.6:
            points += 3
        elif self.metrics.win_rate > 0.5:
            points += 2
        elif self.metrics.win_rate > 0.4:
            points += 1

        # Trade frequency based points (0-2)
        if self.metrics.trade_frequency == "high":
            points += 2
        elif self.metrics.trade_frequency == "medium":
            points += 1

        # Determine level based on points
        if points >= 6:
            return "advanced"
        elif points >= 3:
            return "intermediate"
        else:
            return "beginner"

    def generate_profile(self) -> UserProfile:
        """Generate complete user profile."""
        self._fetch_data()
        
        # Run all analysis
        self._analyze_leverage_patterns()
        self._analyze_preferred_tokens()
        self._analyze_trade_frequency()
        self._analyze_risk_profile()
        self._analyze_trading_times()
        self._calculate_win_rate()

        # Determine overall characteristics
        trading_style = self._determine_trading_style()
        experience_level = self._determine_experience_level()

        # Create and return profile
        return UserProfile(
            address=self.address,
            metrics=self.metrics,
            trading_style=trading_style,
            experience_level=experience_level,
            last_updated=datetime.now()
        )

    def get_profile_summary(self) -> str:
        """Get a human-readable summary of the user profile."""
        profile = self.generate_profile()
        
        summary = [
            f"=== 👤 Trader Profile for {profile.address[:6]}...{profile.address[-4:]} ===\n",
            f"Experience Level: {profile.experience_level.title()}",
            f"Trading Style: {profile.trading_style.replace('_', ' ').title()}",
            f"Risk Profile: {profile.metrics.risk_profile.title()}",
            f"\nTrading Patterns:",
            f"- Average Leverage: {profile.metrics.avg_leverage:.1f}x",
            f"- Win Rate: {profile.metrics.win_rate*100:.1f}%",
            f"- Trading Frequency: {profile.metrics.trade_frequency.title()}",
            f"\nPreferred Tokens: {', '.join(profile.metrics.preferred_tokens or ['N/A'])}",
            f"Favorite Trading Hours: {', '.join(profile.metrics.favorite_trade_times or ['N/A'])}",
        ]
        
        return "\n".join(summary)