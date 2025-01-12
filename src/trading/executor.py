# src/theseus_alpha/trading/executor.py
from typing import Dict, List, Optional
import logging
import json
from datetime import datetime

from hyperliquid.info import Info
from hyperliquid.exchange import Exchange
from theseus_alpha.trading.types import TradeExecution

class TradingExecutor:
    def __init__(self, address: str, info: Info, exchange: Exchange):
        """
        Initialize the trading executor.
        """
        self.address = address
        self.info = info
        self.exchange = exchange
        self.logger = logging.getLogger(__name__)
        self.TEST_TRADE_SIZE = 15.0  # Test trade size in USD

    def execute_recommendations(self, recommendations_file: str, is_test: bool = True) -> List[TradeExecution]:
        """Execute trading recommendations from a JSON file."""
        try:
            # Load recommendations
            with open(recommendations_file, 'r') as f:
                recommendations = json.load(f)
            
            executions = []
            
            # Execute spot recommendations
            for rec in recommendations.get('spot_recommendations', []):
                if rec['action'] == 'hold':
                    continue
                    
                # Override size if in test mode
                if is_test:
                    rec['size_usd'] = self.TEST_TRADE_SIZE
                    
                execution = self._execute_spot_trade(rec)
                executions.append(execution)
            
            # Execute perpetual recommendations
            for rec in recommendations.get('perp_recommendations', []):
                # Override size if in test mode
                if is_test:
                    rec['size_usd'] = self.TEST_TRADE_SIZE
                    
                execution = self._execute_perp_trade(rec)
                executions.append(execution)
            
            return executions
            
        except Exception as e:
            self.logger.error(f"Error executing recommendations: {str(e)}")
            return []

    def _execute_spot_trade(self, recommendation: Dict) -> TradeExecution:
        """Execute a spot trade."""
        try:
            asset = recommendation['asset']
            size = recommendation['size_usd']
            is_buy = recommendation['action'] == 'buy'
            
            # Get current market price
            market_price = float(self.info.all_mids()[asset])
            
            # Get size (either pre-calculated or convert from USD)
            trade_size = recommendation.get('size') or round(size/market_price, 6)
            
            # Place the order
            response = self.exchange.order(
                name=asset,
                is_buy=is_buy,
                sz=trade_size,
                limit_px=market_price,
                order_type={"limit": {"tif": "Ioc"}}  # Immediate-or-cancel for market-like execution
            )
            
            if response['status'] == 'ok':
                order_id = response['response']['data']['statuses'][0].get('resting', {}).get('oid')
                return TradeExecution(
                    asset=asset,
                    success=True,
                    order_id=order_id,
                    error=None,
                    timestamp=datetime.now()
                )
            else:
                return TradeExecution(
                    asset=asset,
                    success=False,
                    order_id=None,
                    error=str(response),
                    timestamp=datetime.now()
                )
                
        except Exception as e:
            return TradeExecution(
                asset=recommendation['asset'],
                success=False,
                order_id=None,
                error=str(e),
                timestamp=datetime.now()
            )

    def _execute_perp_trade(self, recommendation: Dict) -> TradeExecution:
        """Execute a perpetual trade."""
        try:
            asset = recommendation['asset']
            size = recommendation['size_usd']
            is_long = recommendation['direction'] == 'long'
            leverage = recommendation['leverage']
            
            # Update leverage first
            self.exchange.update_leverage(
                leverage=leverage,
                name=asset,
                is_cross=True  # Using cross margin
            )
            
            # Get current market price
            market_price = float(self.info.all_mids()[asset])
            
            # Get size (either pre-calculated or convert from USD)
            trade_size = recommendation.get('size') or round(size/market_price, 6)
            
            # Place the order
            response = self.exchange.order(
                name=asset,
                is_buy=is_long,
                sz=trade_size,
                limit_px=market_price,
                order_type={"limit": {"tif": "Ioc"}}  # Immediate-or-cancel for market-like execution
            )
            
            if response['status'] == 'ok':
                order_id = response['response']['data']['statuses'][0].get('resting', {}).get('oid')
                return TradeExecution(
                    asset=asset,
                    success=True,
                    order_id=order_id,
                    error=None,
                    timestamp=datetime.now()
                )
            else:
                return TradeExecution(
                    asset=asset,
                    success=False,
                    order_id=None,
                    error=str(response),
                    timestamp=datetime.now()
                )
                
        except Exception as e:
            return TradeExecution(
                asset=recommendation['asset'],
                success=False,
                order_id=None,
                error=str(e),
                timestamp=datetime.now()
            )

    def validate_execution(self, execution: TradeExecution) -> bool:
        """Validate that a trade was executed correctly."""
        try:
            if not execution.success or not execution.order_id:
                return False
                
            # Check order status
            order_status = self.info.query_order_by_oid(
                self.address, 
                execution.order_id
            )
            
            return order_status.get('status') == 'filled'
            
        except Exception as e:
            self.logger.error(f"Error validating execution: {str(e)}")
            return False