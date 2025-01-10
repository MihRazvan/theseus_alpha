import example_utils
from hyperliquid.utils import constants
from datetime import datetime
import json

def format_money(value):
    """Format numeric values to readable strings with 4 decimal places"""
    try:
        return f"{float(value):,.4f}"
    except:
        return value

def analyze_account():
    try:
        # Setup connection
        address, info, exchange = example_utils.setup(constants.TESTNET_API_URL, skip_ws=True)
        print(f"\n🔍 Analyzing account: {address}\n")

        # Get account states
        perp_state = info.user_state(address)
        spot_state = info.spot_user_state(address)
        
        # 1. General Account Overview
        print("=== 📊 Account Overview ===")
        account_value = format_money(perp_state["marginSummary"]["accountValue"])
        print(f"Total Account Value: ${account_value} USDC")
        print(f"Withdrawable: ${format_money(perp_state['withdrawable'])} USDC")
        print(f"Total Margin Used: ${format_money(perp_state['marginSummary']['totalMarginUsed'])} USDC")
        
        # 2. Spot Positions
        print("\n=== 💰 Spot Balances ===")
        if spot_state["balances"]:
            for balance in spot_state["balances"]:
                print(f"{balance['coin']}:")
                print(f"  Total: {format_money(balance['total'])}")
                print(f"  In Orders: {format_money(balance['hold'])}")
                print(f"  Available: {format_money(float(balance['total']) - float(balance['hold']))}")
        else:
            print("No spot balances found")

        # 3. Perpetual Positions
        print("\n=== 📈 Perpetual Positions ===")
        if perp_state["assetPositions"]:
            for position in perp_state["assetPositions"]:
                pos = position["position"]
                print(f"\n{pos['coin']}:")
                print(f"  Size: {format_money(pos['szi'])} {pos['coin']}")
                print(f"  Entry Price: ${format_money(pos['entryPx'])}")
                print(f"  Position Value: ${format_money(pos['positionValue'])}")
                print(f"  Unrealized PnL: ${format_money(pos['unrealizedPnl'])}")
                print(f"  ROE: {format_money(pos['returnOnEquity'])}%")
                print(f"  Leverage: {pos['leverage']['value']}x")
        else:
            print("No perpetual positions found")

        # 4. Recent Trading Activity
        print("\n=== 🔄 Recent Trading Activity ===")
        recent_fills = info.user_fills(address)[:5]  # Get last 5 trades
        if recent_fills:
            for fill in recent_fills:
                timestamp = datetime.fromtimestamp(fill["time"]/1000).strftime('%Y-%m-%d %H:%M:%S')
                print(f"\nTrade at {timestamp}:")
                print(f"  Asset: {fill['coin']}")
                print(f"  Side: {fill['dir']}")
                print(f"  Size: {format_money(fill['sz'])}")
                print(f"  Price: ${format_money(fill['px'])}")
                print(f"  Fee: ${format_money(fill['fee'])}")
        else:
            print("No recent trades found")

        # 5. Open Orders
        print("\n=== 📝 Open Orders ===")
        open_orders = info.open_orders(address)
        if open_orders:
            for order in open_orders:
                print(f"\n{order['coin']}:")
                print(f"  Side: {'Buy' if order['side'] == 'B' else 'Sell'}")
                print(f"  Size: {format_money(order['sz'])}")
                print(f"  Price: ${format_money(order['limitPx'])}")
        else:
            print("No open orders found")

        return True

    except Exception as e:
        print("\n❌ Error analyzing account!")
        print("Error:", str(e))
        return False

if __name__ == "__main__":
    analyze_account()