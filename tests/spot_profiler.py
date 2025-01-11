from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import statistics
from collections import defaultdict

@dataclass
class SpotRiskMetrics:
    stablecoin_ratio: float = 0.0  # Percentage of portfolio in stablecoins
    large_cap_ratio: float = 0.0   # Percentage in BTC/ETH
    asset_diversity: int = 0        # Number of different assets held
    avg_position_size: float = 0.0  # Average size of positions relative to portfolio
    portfolio_concentration: float = 0.0  # How concentrated in top holdings

@dataclass
class SpotTradingPatterns:
    avg_hold_time: timedelta = timedelta(0)
    trade_frequency: str = ""  # high/medium/low
    entry_timing_score: float = 0.0  # Score based on entry timing vs market
    size_consistency: float = 0.0    # Variance in trade sizes
    preferred_tokens: List[str] = None
    typical_trade_value: float = 0.0

@dataclass
class SpotTraderProfile:
    address: str
    risk_metrics: SpotRiskMetrics
    trading_patterns: SpotTradingPatterns
    trader_type: str  # "hodler", "active_trader", "swing_trader"
    risk_tolerance: str  # "conservative", "moderate", "aggressive"
    experience_level: str  # "beginner", "intermediate", "advanced"
    last_updated: datetime

class SpotProfiler:
    def __init__(self, address: str, info, exchange):
        self.address = address
        self.info = info
        self.exchange = exchange
        self.spot_state = None
        self.historical_trades = None
        self.risk_metrics = SpotRiskMetrics()
        self.trading_patterns = SpotTradingPatterns()
        
        # Constants for classification
        self.STABLECOIN_TOKENS = ["USDC", "USDT", "DAI"]
        self.LARGE_CAP_TOKENS = ["BTC", "ETH"]
        
    def _fetch_data(self) -> None:
        """Fetch all necessary spot trading data."""
        try:
            # Get current spot balances
            self.spot_state = self.info.spot_user_state(self.address)
            
            # Get historical spot trades (90 days)
            start_time = int((datetime.now() - timedelta(days=90)).timestamp() * 1000)
            self.historical_trades = self.info.user_fills_by_time(
                self.address, 
                start_time=start_time
            )
        except Exception as e:
            raise Exception(f"Failed to fetch spot data: {str(e)}")

    def _analyze_portfolio_composition(self) -> None:
        """Analyze current portfolio composition and risk metrics."""
        total_value = 0
        stablecoin_value = 0
        large_cap_value = 0
        token_values = defaultdict(float)

        for balance in self.spot_state.get("balances", []):
            token = balance["coin"]
            value = float(balance["total"])
            token_values[token] = value
            total_value += value

            if token in self.STABLECOIN_TOKENS:
                stablecoin_value += value
            elif token in self.LARGE_CAP_TOKENS:
                large_cap_value += value

        if total_value > 0:
            self.risk_metrics.stablecoin_ratio = stablecoin_value / total_value
            self.risk_metrics.large_cap_ratio = large_cap_value / total_value
            
        # Calculate portfolio concentration (Herfindahl-Hirschman Index)
        if token_values:
            squares_sum = sum((v/total_value)**2 for v in token_values.values())
            self.risk_metrics.portfolio_concentration = squares_sum
            self.risk_metrics.asset_diversity = len(token_values)

    def _analyze_trading_behavior(self) -> None:
        """Analyze trading patterns and behavior."""
        if not self.historical_trades:
            return

        # Analyze trade sizes
        trade_sizes = []
        trade_times = []
        token_volumes = defaultdict(float)

        for trade in self.historical_trades:
            size = float(trade["sz"])
            price = float(trade["px"])
            value = size * price
            trade_sizes.append(value)
            trade_times.append(trade["time"])
            token_volumes[trade["coin"]] += value

        # Calculate trade size consistency
        if trade_sizes:
            mean_size = statistics.mean(trade_sizes)
            std_size = statistics.stdev(trade_sizes) if len(trade_sizes) > 1 else 0
            self.trading_patterns.size_consistency = std_size / mean_size if mean_size > 0 else 0
            self.trading_patterns.typical_trade_value = mean_size

        # Calculate trading frequency
        if trade_times:
            trades_per_day = len(trade_times) / 90  # 90 days window
            if trades_per_day >= 3:
                self.trading_patterns.trade_frequency = "high"
            elif trades_per_day >= 0.5:
                self.trading_patterns.trade_frequency = "medium"
            else:
                self.trading_patterns.trade_frequency = "low"

        # Find preferred tokens
        sorted_tokens = sorted(token_volumes.items(), key=lambda x: x[1], reverse=True)
        self.trading_patterns.preferred_tokens = [token for token, _ in sorted_tokens[:3]]

    def _determine_trader_type(self) -> str:
        """Determine the type of trader based on patterns."""
        if self.trading_patterns.trade_frequency == "low" and self.risk_metrics.stablecoin_ratio < 0.3:
            return "hodler"
        elif self.trading_patterns.trade_frequency == "high":
            return "active_trader"
        else:
            return "swing_trader"

    def _determine_risk_tolerance(self) -> str:
        """Determine risk tolerance based on portfolio composition."""
        risk_score = 0
        
        # Higher score means more risky behavior
        risk_score += (1 - self.risk_metrics.stablecoin_ratio) * 3  # 0-3 points
        risk_score += (1 - self.risk_metrics.large_cap_ratio) * 2   # 0-2 points
        risk_score += self.risk_metrics.portfolio_concentration * 2  # 0-2 points
        
        if self.trading_patterns.trade_frequency == "high":
            risk_score += 1
        
        if risk_score > 5:
            return "aggressive"
        elif risk_score > 3:
            return "moderate"
        else:
            return "conservative"

    def generate_profile(self) -> SpotTraderProfile:
        """Generate complete spot trading profile."""
        self._fetch_data()
        self._analyze_portfolio_composition()
        self._analyze_trading_behavior()
        
        trader_type = self._determine_trader_type()
        risk_tolerance = self._determine_risk_tolerance()
        
        return SpotTraderProfile(
            address=self.address,
            risk_metrics=self.risk_metrics,
            trading_patterns=self.trading_patterns,
            trader_type=trader_type,
            risk_tolerance=risk_tolerance,
            experience_level=self._determine_experience_level(),
            last_updated=datetime.now()
        )

    def _determine_experience_level(self) -> str:
        """Determine trader experience level."""
        points = 0
        
        # Portfolio diversity points
        if self.risk_metrics.asset_diversity >= 5:
            points += 2
        elif self.risk_metrics.asset_diversity >= 3:
            points += 1

        # Trading frequency points
        if self.trading_patterns.trade_frequency == "high":
            points += 2
        elif self.trading_patterns.trade_frequency == "medium":
            points += 1

        # Portfolio size points (you might want to adjust these thresholds)
        total_value = sum(float(b["total"]) for b in self.spot_state.get("balances", []))
        if total_value > 10000:
            points += 3
        elif total_value > 1000:
            points += 2
        elif total_value > 100:
            points += 1

        if points >= 5:
            return "advanced"
        elif points >= 3:
            return "intermediate"
        else:
            return "beginner"

    def get_profile_summary(self) -> str:
        """Get a human-readable summary of the spot trading profile."""
        profile = self.generate_profile()
        
        summary = [
            f"=== 👤 Spot Trading Profile for {profile.address[:6]}...{profile.address[-4:]} ===\n",
            f"Trader Type: {profile.trader_type.replace('_', ' ').title()}",
            f"Risk Tolerance: {profile.risk_tolerance.title()}",
            f"Experience Level: {profile.experience_level.title()}\n",
            
            "Portfolio Composition:",
            f"- Stablecoin Ratio: {profile.risk_metrics.stablecoin_ratio*100:.1f}%",
            f"- Large Cap Ratio: {profile.risk_metrics.large_cap_ratio*100:.1f}%",
            f"- Number of Assets: {profile.risk_metrics.asset_diversity}",
            f"- Portfolio Concentration: {profile.risk_metrics.portfolio_concentration:.2f}\n",
            
            "Trading Patterns:",
            f"- Trading Frequency: {profile.trading_patterns.trade_frequency.title()}",
            f"- Trade Size Consistency: {profile.trading_patterns.size_consistency:.2f}",
            f"- Typical Trade Value: ${profile.trading_patterns.typical_trade_value:.2f}",
            f"- Preferred Tokens: {', '.join(profile.trading_patterns.preferred_tokens or ['N/A'])}"
        ]
        
        return "\n".join(summary)