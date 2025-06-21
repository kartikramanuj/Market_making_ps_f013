# visualization.py

import matplotlib.pyplot as plt
from pnl_tracker import PnLTracker

# Simulated trade data (sample)
trades = [
    {"price": 100, "quantity": 2, "side": "buy"},
    {"price": 103, "quantity": 1, "side": "sell"},
    {"price": 105, "quantity": 1, "side": "sell"},
    {"price": 99, "quantity": 1, "side": "buy"}
]

# Spread over time (sample)
spread_series = [2.0, 1.8, 1.5, 1.6]

# Inventory over time
inventory_series = []
tracker = PnLTracker()

for trade in trades:
    tracker.record_trade(trade["price"], trade["quantity"], trade["side"])
    inventory_series.append(tracker.inventory)

# Plot cumulative P&L
cumulative_pnl = tracker.get_cumulative_pnl_series()
plt.figure(figsize=(12, 4))

plt.subplot(1, 3, 1)
plt.plot(cumulative_pnl, marker='o')
plt.title("Cumulative P&L")
plt.xlabel("Trade Index")
plt.ylabel("P&L (₹)")
plt.grid(True)

# Plot spread
plt.subplot(1, 3, 2)
plt.plot(spread_series, marker='s', color='orange')
plt.title("Bid-Ask Spread Over Time")
plt.xlabel("Time Step")
plt.ylabel("Spread")
plt.grid(True)

# Plot inventory
plt.subplot(1, 3, 3)
plt.plot(inventory_series, marker='^', color='green')
plt.title("Inventory Over Time")
plt.xlabel("Trade Index")
plt.ylabel("Inventory")
plt.grid(True)

plt.tight_layout()
plt.show()
