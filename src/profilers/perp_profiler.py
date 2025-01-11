from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import statistics
from collections import defaultdict

@dataclass
class PerpRiskMetrics:
    avg_leverage: float = 0.0
    max_leverage: float = 0.0
    capital_utilization: float = 0.0  # How much of available margin is typically used
    position_concentration: float = 0.0  # How concentrated positions are
    liquidation_proximity: float = 0.0  # Average proximity to liquidation prices
    margin_usage_ratio: float = 0.0    # Used margin vs available margin

@dataclass
class PerpTradingPatterns:
    win_rate: float = 0.0
    avg_profit_loss_ratio: float = 0.0
    avg_holding_time: timedelta = timedelta(0)
    trade_frequency: str = ""
    preferred_markets: List[str] = None
    avg_position_size: float = 0.0
    size_consistency: float = 0.0
    directional_bias: str = ""  # "long_biased", "short_biased", "neutral"

@dataclass
class PerpTraderProfile:
    address: str
    risk_metrics: PerpRiskMetrics
    trading_patterns: PerpTradingPatterns
    trader_type: str  # "scalper", "day_trader", "swing_trader", "position_trader"
    risk_appetite: str  # "conservative", "moderate", "aggressive"
    experience_level: str  # "beginner", "intermediate", "advanced"
    last_updated: datetime

class PerpProfiler:
    def __init__(self, address: str, info, exchange):
        self.address = address
        self.info = info
        self.exchange = exchange
        self.current_state = None
        self.historical_trades = None
        self.risk_metrics = PerpRiskMetrics()
        self.trading_patterns = PerpTradingPatterns()

    def _fetch_data(self) -> None:
        """Fetch all necessary perpetual trading data."""
        try:
            # Get current account state
            self.current_state = self.info.user_state(self.address)
            
            # Get historical trades (60 days)
            start_time = int((datetime.now() - timedelta(days=60)).timestamp() * 1000)
            self.historical_trades = self.info.user_fills_by_time(
                self.address, 
                start_time=start_time
            )
        except Exception as e:
            raise Exception(f"Failed to fetch perp data: {str(e)}")

    def _analyze_risk_metrics(self) -> None:
        """Analyze risk-related metrics from current positions and history."""
        leverages = []
        liquidation_distances = []
        position_sizes = []
        
        # Analyze current positions
        for position in self.current_state.get("assetPositions", []):
            pos = position["position"]
            
            # Leverage analysis
            if "leverage" in pos:
                leverages.append(float(pos["leverage"]["value"]))
            
            # Position size analysis
            if "positionValue" in pos:
                position_sizes.append(float(pos["positionValue"]))
            
            # Liquidation proximity analysis
            if "liquidationPx" in pos and pos["liquidationPx"] and "entryPx" in pos:
                entry_price = float(pos["entryPx"])
                liq_price = float(pos["liquidationPx"])
                distance = abs(entry_price - liq_price) / entry_price
                liquidation_distances.append(distance)

        # Calculate risk metrics
        if leverages:
            self.risk_metrics.avg_leverage = statistics.mean(leverages)
            self.risk_metrics.max_leverage = max(leverages)
        
        if liquidation_distances:
            self.risk_metrics.liquidation_proximity = statistics.mean(liquidation_distances)

        # Calculate margin usage
        total_margin = float(self.current_state["marginSummary"]["totalMarginUsed"])
        available_margin = float(self.current_state["marginSummary"]["accountValue"])
        if available_margin > 0:
            self.risk_metrics.margin_usage_ratio = total_margin / available_margin

        # Calculate position concentration
        if position_sizes:
            total_position_value = sum(position_sizes)
            squares_sum = sum((size/total_position_value)**2 for size in position_sizes)
            self.risk_metrics.position_concentration = squares_sum

    def _analyze_trading_patterns(self) -> None:
        """Analyze trading patterns from historical data."""
        if not self.historical_trades:
            return

        # Initialize analysis variables
        profits = []
        losses = []
        trade_sizes = []
        market_directions = defaultdict(int)  # Count of long vs short per market
        trade_intervals = []
        last_trade_time = None
        market_volumes = defaultdict(float)

        for trade in self.historical_trades:
            # Analyze P&L
            pnl = float(trade.get("closedPnl", 0))
            if pnl > 0:
                profits.append(pnl)
            elif pnl < 0:
                losses.append(abs(pnl))

            # Analyze trade sizes
            size = float(trade["sz"]) * float(trade["px"])
            trade_sizes.append(size)

            # Analyze market direction preference
            market = trade["coin"]
            direction = 1 if trade["dir"].startswith("Long") else -1
            market_directions[market] += direction
            
            # Analyze trading intervals
            trade_time = datetime.fromtimestamp(trade["time"]/1000)
            if last_trade_time:
                interval = trade_time - last_trade_time
                trade_intervals.append(interval)
            last_trade_time = trade_time

            # Track volume per market
            market_volumes[market] += size

        # Calculate win rate
        total_trades = len(profits) + len(losses)
        if total_trades > 0:
            self.trading_patterns.win_rate = len(profits) / total_trades

        # Calculate profit/loss ratio
        if profits and losses:
            avg_profit = statistics.mean(profits)
            avg_loss = statistics.mean(losses)
            if avg_loss > 0:
                self.trading_patterns.avg_profit_loss_ratio = avg_profit / avg_loss

        # Calculate average holding time
        if trade_intervals:
            # Convert timedeltas to seconds, calculate mean, then convert back to timedelta
            interval_seconds = [interval.total_seconds() for interval in trade_intervals]
            avg_seconds = statistics.mean(interval_seconds) if interval_seconds else 0
            self.trading_patterns.avg_holding_time = timedelta(seconds=avg_seconds)

        # Determine trading frequency
        trades_per_day = total_trades / 60  # 60-day window
        if trades_per_day >= 5:
            self.trading_patterns.trade_frequency = "high"
        elif trades_per_day >= 1:
            self.trading_patterns.trade_frequency = "medium"
        else:
            self.trading_patterns.trade_frequency = "low"

        # Calculate preferred markets
        sorted_markets = sorted(market_volumes.items(), key=lambda x: x[1], reverse=True)
        self.trading_patterns.preferred_markets = [market for market, _ in sorted_markets[:3]]

        # Calculate position size metrics
        if trade_sizes:
            self.trading_patterns.avg_position_size = statistics.mean(trade_sizes)
            std_size = statistics.stdev(trade_sizes) if len(trade_sizes) > 1 else 0
            self.trading_patterns.size_consistency = std_size / self.trading_patterns.avg_position_size

        # Determine directional bias
        total_direction = sum(market_directions.values())
        if total_direction > total_trades * 0.2:
            self.trading_patterns.directional_bias = "long_biased"
        elif total_direction < -total_trades * 0.2:
            self.trading_patterns.directional_bias = "short_biased"
        else:
            self.trading_patterns.directional_bias = "neutral"

    def _determine_trader_type(self) -> str:
        """Determine trader type based on patterns."""
        avg_hold_hours = self.trading_patterns.avg_holding_time.total_seconds() / 3600
        
        if avg_hold_hours < 1 and self.trading_patterns.trade_frequency == "high":
            return "scalper"
        elif avg_hold_hours < 24 and self.trading_patterns.trade_frequency in ["high", "medium"]:
            return "day_trader"
        elif avg_hold_hours < 168:  # 1 week
            return "swing_trader"
        else:
            return "position_trader"

    def _determine_risk_appetite(self) -> str:
        """Determine risk appetite based on multiple factors."""
        risk_score = 0
        
        # Leverage contribution (0-3 points)
        if self.risk_metrics.max_leverage >= 10:
            risk_score += 3
        elif self.risk_metrics.max_leverage >= 5:
            risk_score += 2
        elif self.risk_metrics.max_leverage >= 2:
            risk_score += 1

        # Margin usage contribution (0-2 points)
        if self.risk_metrics.margin_usage_ratio >= 0.7:
            risk_score += 2
        elif self.risk_metrics.margin_usage_ratio >= 0.4:
            risk_score += 1

        # Position concentration contribution (0-2 points)
        if self.risk_metrics.position_concentration >= 0.7:
            risk_score += 2
        elif self.risk_metrics.position_concentration >= 0.4:
            risk_score += 1

        # Trading frequency contribution (0-1 point)
        if self.trading_patterns.trade_frequency == "high":
            risk_score += 1

        if risk_score >= 6:
            return "aggressive"
        elif risk_score >= 3:
            return "moderate"
        else:
            return "conservative"

    def _determine_experience_level(self) -> str:
        """Determine trader experience level."""
        points = 0
        
        # Win rate contribution
        if self.trading_patterns.win_rate >= 0.6:
            points += 3
        elif self.trading_patterns.win_rate >= 0.5:
            points += 2
        elif self.trading_patterns.win_rate >= 0.4:
            points += 1

        # Trade frequency contribution
        if self.trading_patterns.trade_frequency == "high":
            points += 2
        elif self.trading_patterns.trade_frequency == "medium":
            points += 1

        # P/L ratio contribution
        if self.trading_patterns.avg_profit_loss_ratio >= 2:
            points += 3
        elif self.trading_patterns.avg_profit_loss_ratio >= 1.5:
            points += 2
        elif self.trading_patterns.avg_profit_loss_ratio >= 1:
            points += 1

        if points >= 6:
            return "advanced"
        elif points >= 3:
            return "intermediate"
        else:
            return "beginner"

    def generate_profile(self) -> PerpTraderProfile:
        """Generate complete perpetual trading profile."""
        self._fetch_data()
        self._analyze_risk_metrics()
        self._analyze_trading_patterns()
        
        trader_type = self._determine_trader_type()
        risk_appetite = self._determine_risk_appetite()
        experience_level = self._determine_experience_level()
        
        return PerpTraderProfile(
            address=self.address,
            risk_metrics=self.risk_metrics,
            trading_patterns=self.trading_patterns,
            trader_type=trader_type,
            risk_appetite=risk_appetite,
            experience_level=experience_level,
            last_updated=datetime.now()
        )

    def get_profile_summary(self) -> str:
        """Get a human-readable summary of the perpetual trading profile."""
        profile = self.generate_profile()
        
        summary = [
            f"=== 👤 Perpetual Trading Profile for {profile.address[:6]}...{profile.address[-4:]} ===\n",
            f"Trader Type: {profile.trader_type.replace('_', ' ').title()}",
            f"Risk Appetite: {profile.risk_appetite.title()}",
            f"Experience Level: {profile.experience_level.title()}\n",
            
            "Risk Metrics:",
            f"- Average Leverage: {profile.risk_metrics.avg_leverage:.1f}x",
            f"- Maximum Leverage: {profile.risk_metrics.max_leverage:.1f}x",
            f"- Margin Usage: {profile.risk_metrics.margin_usage_ratio*100:.1f}%",
            f"- Position Concentration: {profile.risk_metrics.position_concentration:.2f}\n",
            
            "Trading Patterns:",
            f"- Win Rate: {profile.trading_patterns.win_rate*100:.1f}%",
            f"- Profit/Loss Ratio: {profile.trading_patterns.avg_profit_loss_ratio:.2f}",
            f"- Trading Frequency: {profile.trading_patterns.trade_frequency.title()}",
            f"- Directional Bias: {profile.trading_patterns.directional_bias.replace('_', ' ').title()}",
            f"- Preferred Markets: {', '.join(profile.trading_patterns.preferred_markets or ['N/A'])}",
            f"- Average Position Size: ${profile.trading_patterns.avg_position_size:.2f}",
            f"- Average Holding Time: {profile.trading_patterns.avg_holding_time.total_seconds()/3600:.1f} hours"
        ]
        
        return "\n".join(summary)