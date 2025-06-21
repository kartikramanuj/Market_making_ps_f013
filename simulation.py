# simulation.py

from pnl_tracker import PnLTracker

# Simulated trade data (sample)
trades = [
    {"price": 100, "quantity": 2, "side": "buy"},
    {"price": 103, "quantity": 1, "side": "sell"},
    {"price": 105, "quantity": 1, "side": "sell"},
    {"price": 99, "quantity": 1, "side": "buy"}
]

tracker = PnLTracker()

for trade in trades:
    tracker.record_trade(trade["price"], trade["quantity"], trade["side"])

summary = tracker.get_summary()
print("Simulation Summary:")
print(f"Total Trades: {summary['Total Trades']}")
print(f"Inventory: {summary['Inventory']}")
print(f"Realized P&L: ₹{summary['Realized P&L']}")
