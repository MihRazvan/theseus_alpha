from typing import Dict, Tuple, Optional
from decimal import Decimal, ROUND_DOWN
import logging

from hyperliquid.info import Info

logger = logging.getLogger(__name__)

def normalize_price(
    info: Info, 
    asset: str, 
    price: float, 
    reference_type: str = 'oracle'
) -> float:
    """
    Normalize price based on reference price (oracle or mark).
    """
    try:
        # For spot trading (PURR/USDC)
        if asset == "PURR":
            return round(price, 4)  # PURR uses 4 decimal places

        # For perpetuals
        meta_ctxs = info.post("/info", {"type": "metaAndAssetCtxs"})
        asset_idx = None
        
        # Find asset index in meta data
        for idx, ctx in enumerate(meta_ctxs[1]):
            if ctx.get('coin') == asset:
                asset_idx = idx
                break
                
        if asset_idx is None:
            logger.warning(f"Asset {asset} not found in metadata")
            return round(price, 2)
            
        asset_ctx = meta_ctxs[1][asset_idx]
        reference_price = float(asset_ctx['oraclePx'] if reference_type == 'oracle' else asset_ctx['markPx'])
        
        # For perps, we want to be slightly less aggressive than the oracle
        if reference_type == 'oracle':
            # Use oracle price directly for buys, slightly below for sells
            normalized = reference_price
        else:
            # Round to 5 significant figures and 2 decimal places
            normalized = float(f"{price:.5g}")
            normalized = round(normalized, 2)
        
        return normalized
        
    except Exception as e:
        logger.error(f"Error normalizing price for {asset}: {str(e)}")
        return round(price, 2)

def calculate_safe_size(
    info: Info,
    asset: str,
    available_balance: float,
    price: float,
    leverage: int = 1,
    safety_margin: float = 0.95
) -> Tuple[float, str]:
    """
    Calculate safe order size based on available balance and leverage.
    
    Returns:
        Tuple of (size, message)
    """
    try:
        meta = info.meta()
        asset_meta = next(asset_info for asset_info in meta["universe"] 
                         if asset_info["name"] == asset)
        sz_decimals = asset_meta["szDecimals"]
        
        # Calculate maximum size based on balance and leverage
        max_notional = available_balance * leverage * safety_margin
        raw_size = max_notional / price
        
        # Round to proper decimal places
        size = round(float(Decimal(str(raw_size)).quantize(
            Decimal(f'0.{"0" * sz_decimals}'),
            rounding=ROUND_DOWN
        )), sz_decimals)
        
        message = f"Size {size} {asset} (${size * price:.2f})"
        return size, message
    except Exception as e:
        logger.error(f"Error calculating size: {str(e)}")
        return 0.0, str(e)

def validate_order(
    info: Info,
    asset: str,
    is_buy: bool,
    size: float,
    price: float,
    leverage: int = 1
) -> Tuple[bool, str]:
    """
    Validate order parameters before submission.
    """
    try:
        # Check minimum notional value ($10)
        notional = size * price
        if notional < 10:
            return False, f"Order value ${notional:.2f} below minimum $10"
            
        # Check maximum leverage
        meta = info.meta()
        asset_meta = next(asset_info for asset_info in meta["universe"] 
                         if asset_info["name"] == asset)
        max_leverage = asset_meta.get("maxLeverage", 50)
        
        if leverage > max_leverage:
            return False, f"Leverage {leverage}x exceeds maximum {max_leverage}x"
            
        # Validate price tick size
        normalized_price = normalize_price(info, asset, price)
        if abs(normalized_price - price) > 0.01:
            return False, f"Price ${price} invalid, normalized to ${normalized_price}"
            
        return True, "Order validation passed"
    except Exception as e:
        logger.error(f"Error validating order: {str(e)}")
        return False, str(e)

def check_balance(
    info: Info,
    address: str,
    asset: str,
    is_spot: bool = False
) -> Tuple[float, Optional[Dict]]:
    """
    Check available balance for trading.
    """
    try:
        if is_spot:
            spot_state = info.spot_user_state(address)
            for balance in spot_state.get("balances", []):
                if balance["coin"] == asset:
                    return float(balance["total"]), balance
            return 0.0, None
        else:
            user_state = info.user_state(address)
            return float(user_state["withdrawable"]), user_state
    except Exception as e:
        logger.error(f"Error checking balance: {str(e)}")
        return 0.0, None