# visualization.py
import matplotlib.pyplot as plt
from pnl_tracker import PnLTracker

def create_sample_data():
    """Create some sample trading data for demonstration"""
    # These are just example trades - in real life this would come from actual trading
    sample_trades = [
        {"price": 100, "quantity": 2, "side": "buy"},
        {"price": 103, "quantity": 1, "side": "sell"},
        {"price": 105, "quantity": 1, "side": "sell"},
        {"price": 99, "quantity": 1, "side": "buy"},
        {"price": 102, "quantity": 1, "side": "sell"},
        {"price": 98, "quantity": 2, "side": "buy"}
    ]
    return sample_trades

def simulate_spread_data():
    """Simulate bid-ask spread over time"""
    # This is fake data - in reality you'd get this from order book
    spread_over_time = [2.0, 1.8, 1.5, 1.6, 1.4, 1.7, 1.3, 1.5]
    return spread_over_time

def generate_plots():
    """Generate all the plots and show them"""
    print("Creating trading visualizations...")
    
    # Get sample data
    trades = create_sample_data()
    spread_data = simulate_spread_data()
    
    # Process trades through P&L tracker
    inventory_over_time = []
    pnl_over_time = []
    tracker = PnLTracker()
    
    print("Processing sample trades...")
    for i, trade in enumerate(trades):
        print(f"Trade {i+1}: {trade}")
        tracker.record_trade(trade["price"], trade["quantity"], trade["side"])
        inventory_over_time.append(tracker.inventory)
        pnl_over_time.append(tracker.realized_pnl)
    
    # Create the plots - I'm making 3 subplots side by side
    plt.figure(figsize=(15, 5))
    
    # Plot 1: Cumulative P&L over time
    plt.subplot(1, 3, 1)
    plt.plot(range(len(pnl_over_time)), pnl_over_time, marker='o', color='green', linewidth=2)
    plt.title("Cumulative P&L Over Time")
    plt.xlabel("Trade Number")
    plt.ylabel("P&L ($)")
    plt.grid(True, alpha=0.3)
    plt.axhline(y=0, color='black', linestyle='--', alpha=0.5)  # Zero line
    
    # Plot 2: Bid-Ask Spread over time
    plt.subplot(1, 3, 2)
    plt.plot(range(len(spread_data)), spread_data, marker='s', color='orange', linewidth=2)
    plt.title("Bid-Ask Spread Over Time")
    plt.xlabel("Time Period")
    plt.ylabel("Spread ($)")
    plt.grid(True, alpha=0.3)
    
    # Plot 3: Inventory over time
    plt.subplot(1, 3, 3)
    plt.plot(range(len(inventory_over_time)), inventory_over_time, marker='^', color='blue', linewidth=2)
    plt.title("Inventory Over Time")
    plt.xlabel("Trade Number")
    plt.ylabel("Inventory (Shares)")
    plt.grid(True, alpha=0.3)
    plt.axhline(y=0, color='black', linestyle='--', alpha=0.5)  # Zero line
    
    # Make the layout look nice
    plt.tight_layout()
    
    # Show the plots
    print("Displaying plots...")
    plt.show()
    
    # Print final summary
    final_summary = tracker.get_summary()
    print("\n" + "="*40)
    print("FINAL TRADING SUMMARY")
    print("="*40)
    for key, value in final_summary.items():
        if isinstance(value, float):
            print(f"{key}: ${value:.2f}")
        else:
            print(f"{key}: {value}")
    print("="*40)

def create_price_chart(price_history):
    """Create a simple price chart from price history data"""
    plt.figure(figsize=(12, 6))
    plt.plot(price_history, linewidth=2, color='purple')
    plt.title("Price Movement Over Time")
    plt.xlabel("Time")
    plt.ylabel("Price ($)")
    plt.grid(True, alpha=0.3)
    plt.show()

if __name__ == "__main__":
    print("Starting visualization demo...")
    generate_plots()
    print("Visualization demo completed!")
