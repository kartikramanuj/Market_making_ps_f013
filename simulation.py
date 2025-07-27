from pnl_tracker import PnLTracker
from OrderBook import OrderBook
import threading



# Initialize your PnL tracker and order book
tracker = PnLTracker()
book = OrderBook()

# Simulated orders (limit and market)
orders = [
    {"type": "limit", "side": "bid", "price": 100, "quantity": 2},
    {"type": "limit", "side": "ask", "price": 103, "quantity": 2},
    {"type": "limit", "side": "ask", "price": 105, "quantity": 1},
    {"type": "market", "side": "bid", "quantity": 1}
]

# Function to handle and record trades
def handle_order(order):
    trades, _ = book.process_order(order, from_data=False, verbose=True)
    for trade in trades:
        if 'party2' in trade:
            side = trade['party2'][1]
            trade_side = "buy" if side == "bid" else "sell"
            tracker.record_trade(
                float(trade['price']),
                float(trade['quantity']),
                trade_side
            )

# Process predefined simulated orders
for order in orders:
    handle_order(order)

# CLI for manual order placement
def place_order_cli():
    print("\n--- Manual Order Entry ---")
    print("Format: type side price quantity")
    print("Example: limit bid 99.5 2 OR market ask 0 1")
    print("Type 'quit' or 'exit' to end session.\n")
    
    while True:
        try:
            raw = input("Enter order: ").strip()
            if raw.lower() in ["quit", "exit"]:
                break

            parts = raw.split()
            if len(parts) != 4:
                print(" Invalid format. Try: limit bid 99.5 2")
                continue

            order_type, side, price, qty = parts
            if order_type not in ["limit", "market"] or side not in ["bid", "ask"]:
                print(" Invalid order type or side.")
                continue

            order = {
                "type": order_type,
                "side": side,
                "price": float(price),
                "quantity": float(qty)
            }

            handle_order(order)

        except Exception as e:
            print(f" Error: {e}")

    # Print summary when session ends
    summary = tracker.get_summary()
    print("\n Trading Session Summary:")
    print(f"Total Trades   : {summary['Total Trades']}")
    print(f"Inventory      : {summary['Inventory']}")
    print(f"Realized P&L   : ${summary['Realized P&L']:.2f}")

# Start manual entry loop
place_order_cli()
