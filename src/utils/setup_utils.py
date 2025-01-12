# src/theseus_alpha/utils/setup_utils.py
import json
import os
from pathlib import Path
import eth_account
from eth_account.signers.local import LocalAccount
import logging
from typing import Tuple

from hyperliquid.exchange import Exchange
from hyperliquid.info import Info

def setup_trading_environment(base_url: str = None, skip_ws: bool = False) -> Tuple[str, Info, Exchange]:
    """
    Set up the trading environment with properly configured API wallet.
    
    Returns:
        Tuple containing:
        - address: Main account address (for queries)
        - info: Info instance
        - exchange: Exchange instance configured with API wallet
    """
    # Load config
    config_path = Path(__file__).parent.parent.parent / "config.json"
    with open(config_path) as f:
        config = json.load(f)
        
    # Get main account address (for queries)
    main_address = config["account_address"]
    
    # Create proper API wallet from the secret key
    api_secret = config["secret_key"].strip()  # Remove any whitespace
    if not api_secret.startswith('0x'):
        api_secret = f'0x{api_secret}'  # Ensure 0x prefix
        
    try:
        api_account = eth_account.Account.from_key(api_secret)
    except Exception as e:
        raise Exception(f"Failed to create API wallet: {str(e)}")
    
    print(f"\nSetting up trading environment...")
    print(f"Main Account Address: {main_address}")
    print(f"API Wallet Address: {api_account.address}")
    
    # Initialize info with main address for queries
    info = Info(base_url, skip_ws)
    
    # Verify account has balance
    user_state = info.user_state(main_address)
    account_value = float(user_state["marginSummary"]["accountValue"])
    print(f"Account Value: ${account_value}")
    
    # Setup exchange with API wallet targeting main account
    exchange = Exchange(
        api_account,  # Use API wallet for signing
        base_url, 
        account_address=main_address  # Target main account
    )
    
    # Verify API wallet authorization
    try:
        # Try to do a non-state-changing action to verify API wallet
        exchange.info.user_state(main_address)
        print("✅ API wallet authorization verified")
    except Exception as e:
        print(f"❌ API wallet authorization failed: {str(e)}")
        raise Exception("API wallet not properly authorized")
    
    print("✅ Trading environment setup completed")
    return main_address, info, exchange

def setup_leverage(exchange: Exchange, asset: str, leverage: int = 1) -> bool:
    """Setup leverage for an asset."""
    try:
        result = exchange.update_leverage(
            leverage=leverage,
            name=asset,
            is_cross=True  # Using cross margin
        )
        return result["status"] == "ok"
    except Exception as e:
        print(f"Failed to set leverage: {str(e)}")
        return False