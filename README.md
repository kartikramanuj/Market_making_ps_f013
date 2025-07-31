# Market_making_ps_f013
# Market Making System

A comprehensive Python-based market making and order book system designed for algorithmic trading, backtesting, and educational purposes. This system implements a complete order matching engine with real-time P&L tracking, market simulation, and live market data integration.

##  Features

- **Complete Order Book Implementation**: Fast order matching with price-time priority
- **Market Making Strategies**: Automated bid/ask placement with risk management
- **Real-time P&L Tracking**: FIFO-based profit and loss calculation
- **Market Simulation**: Generate realistic trading scenarios with configurable parameters
- **Live Market Data**: Integration with Binance WebSocket for real-time price feeds
- **Visualization Tools**: Charts for P&L analysis and trading performance
- **Risk Management**: Inventory limits and position monitoring

## System Architecture

### Core Components

```
├── OrderBook.py           # Main order book with matching engine
├── ordertree.py          # Red-black tree for price levels
├── orderlist.py          # Doubly-linked list for same-price orders
├── order.py              # Individual order representation
├── pnl_tracker.py        # P&L calculation and tracking
├── simulation.py         # Market simulation engine
├── market_making_strategy.py  # Basic market making implementation
├── visualization.py      # Plotting and analysis tools
├── test_pnl.py          # Unit tests and interactive testing
└── showcase.py          # Live Binance integration demo
```

### Key Classes

- **OrderBook**: Central matching engine that processes orders and executes trades
- **OrderTree**: Red-black tree storing orders by price level for fast lookups
- **OrderList**: Manages orders at the same price with time priority
- **PnLTracker**: Tracks realized/unrealized P&L using FIFO accounting
- **Simulator**: Generates market conditions and random trading activity
- **MarketMaker**: Implements basic market making strategy with risk controls

## Installation

### Prerequisites

```bash
pip install sortedcontainers matplotlib websockets
```

### Dependencies

- **sortedcontainers**: For efficient sorted data structures
- **matplotlib**: For visualization and charting
- **websockets**: For real-time market data (optional)
- **decimal**: For precise financial calculations (built-in)

##  Quick Start

### 1. Basic Order Book Usage

```python
from OrderBook import OrderBook

# Create order book
book = OrderBook(symbol='BTC/USD')

# Place limit orders
book.process_order({
    'type': 'limit',
    'side': 'bid',
    'price': 50000,
    'quantity': 1.5
})

book.process_order({
    'type': 'limit', 
    'side': 'ask',
    'price': 50100,
    'quantity': 2.0
})

# Place market order (will match against existing orders)
trades, remaining = book.process_order({
    'type': 'market',
    'side': 'bid',
    'quantity': 1.0
})

print(f"Executed {len(trades)} trades")
print(book)  # Display current order book state
```

### 2. P&L Tracking

```python
from pnl_tracker import PnLTracker

tracker = PnLTracker()

# Record trades
tracker.record_trade(100.0, 10, 'buy')   # Buy 10 shares at $100
tracker.record_trade(105.0, 5, 'sell')   # Sell 5 shares at $105
tracker.record_trade(110.0, 5, 'sell')   # Sell remaining 5 at $110

# Get P&L summary
summary = tracker.get_summary()
print(f"Realized P&L: ${summary['Realized P&L']}")
print(f"Current Inventory: {summary['Current Inventory']}")
```

### 3. Market Simulation
#### Run simulation (for realistic market conditions through the random orders)
```bash
python simulation.py
```
#### For monitoring
```bash
python simulation.py --duration 30 --monitor
```

```python
from simulation import Simulator, Config

# Configure simulation parameters
config = Config(
    duration=60,        # Run for 60 seconds
    order_rate=2.0,     # 2 orders per second
    base_price=100.0,   # Starting price
    volatility=0.02,    # 2% volatility
    spread=0.01,        # 1% bid-ask spread
    market_ratio=0.3    # 30% market orders
)

# Create and run simulation
sim = Simulator(config)
sim.start()

# Monitor in real-time
def monitor_trades(event, data):
    if event == 'trade':
        for trade in data['trades']:
            print(f"Trade: {trade['quantity']} @ ${trade['price']}")

sim.add_callback(monitor_trades)
```

## Market Making Strategy
```bash
python market_making_strategy.py
```

### Basic Implementation

```python
from market_making_strategy import MarketMaker

# Initialize market maker
mm = MarketMaker(
    initial_cash=10000,
    symbol='BTC/USD',
    max_inventory=10,
    bid_spread=0.05,    # $0.05 below mid
    ask_spread=0.05     # $0.05 above mid
)

# Place orders around current market price
market_price = 50000
mm.place_order(market_price)

# Monitor performance
cash, inventory, trades = mm.track_performance()
print(f"Cash: ${cash}, Inventory: {inventory}, Trades: {trades}")
```

### Risk Management Features

- **Inventory Limits**: Automatic position size controls
- **Spread Management**: Dynamic bid-ask spread adjustment
- **Liquidation Logic**: Emergency position unwinding
- **Cash Management**: Sufficient capital checks

## Live Market Integration

### Binance WebSocket Integration

```python
# Run the showcase script for live Binance data
python showcase.py
```

This connects to Binance's WebSocket feed and:
- Receives real-time order book updates
- Populates your local order book
- Compares live market data with your internal book
- Demonstrates real-world integration patterns

## Testing

### Run Unit Tests
```python
python test_pnl.py
```


### Interactive Testing Mode

The test suite includes an interactive mode where you can manually enter orders:

```
Enter order: limit bid 99.5 2
Enter order: market ask 0 1
Enter order: book  # Show current order book
Enter order: pnl   # Show P&L summary
```

## Troubleshooting

### Common Issues with test_pnl.py

When running `test_pnl.py`, you may encounter scenarios where volatility and other outputs show as 0. This typically occurs due to:

#### 1. **Timing Issues**
- The simulation runs too quickly, not allowing sufficient time for market maker orders to be placed
- Orders may be processed faster than the market price can update
- Solution: Increase the `delay` parameter in simulation or add `time.sleep()` between operations

#### 2. **Insufficient Market Maker Activity**
- Market maker orders aren't being placed frequently enough
- The `order_rate` parameter may be too low for meaningful price discovery
- Market maker refresh interval (5 seconds) may be too long for short simulations

#### 3. **Low Volatility Settings**
- Base volatility of 0.02 (2%) may be too conservative for short test runs
- Price movements are too small to generate meaningful P&L changes
- Random walk component may not have enough time to accumulate

#### 4. **Order Book Depth Issues**
- Not enough orders in the book to create realistic trading conditions
- Market maker depth setting may be insufficient
- Orders getting matched immediately without building book depth



### Expected Behavior vs. Zero Outputs

**Normal Output:**
```
Realized P&L: $15.50
Current Inventory: 2.5
Volatility: 3.2%
Total Trades: 8
```

**Zero Output Issues:**
```
Realized P&L: $0.00
Current Inventory: 0.0
Volatility: 0.0%
Total Trades: 0
```

If you see zero outputs, try:
1. **Extend simulation time**: Use `duration=300` (5 minutes)
2. **Increase order frequency**: Set `order_rate=10.0`
3. **Boost volatility**: Use `volatility=0.1` (10%)
4. **Add manual delays**: Include `time.sleep(1)` in test loops
5. **Check order execution**: Enable `verbose=True` in `process_order()`

### Debug Mode

Enable detailed logging to diagnose issues:

```python
# In test_pnl.py, add debug output
def debug_market_state(book, tracker):
    print(f"Book state - Bids: {len(book.bids)}, Asks: {len(book.asks)}")
    print(f"Best bid: {book.get_best_bid()}, Best ask: {book.get_best_ask()}")
    print(f"Tracker - Trades: {tracker.total_trades}, P&L: {tracker.realized_pnl}")
    print(f"Tape length: {len(book.tape)}")
```

##  Visualization

### Generate Trading Charts
```bash
python visualization.py
```


```python
from visualization import generate_plots

# Creates three plots:
# 1. Cumulative P&L over time
# 2. Bid-ask spread analysis  
# 3. Inventory levels
generate_plots()
```

### Custom Price Charts

```python
from visualization import create_price_chart

price_history = [100, 101, 99, 102, 98, 103]
create_price_chart(price_history)
```

## Configuration Options

### Simulation Parameters

- **duration**: Simulation runtime in seconds
- **order_rate**: Orders per second frequency
- **base_price**: Starting asset price
- **volatility**: Price movement volatility (0.02 = 2%)
- **spread**: Bid-ask spread as fraction of price
- **market_ratio**: Percentage of market vs limit orders
- **trend**: Directional bias (-1 to 1)
- **depth**: Number of price levels for market making
- **min_size/max_size**: Order quantity ranges

### Order Book Settings

- **symbol**: Trading pair identifier
- **tick_size**: Minimum price increment
- **precision**: Decimal precision for calculations

## Educational Use Cases

This system is excellent for learning:

- **Order Book Mechanics**: How exchanges match orders
- **Market Making**: Providing liquidity for profit
- **Risk Management**: Position and inventory control
- **P&L Calculation**: FIFO accounting methods
- **Market Microstructure**: Bid-ask spreads and price discovery
- **Algorithmic Trading**: Automated strategy development

## Risk Warnings

This system is for educational and research purposes. When adapting for live trading:

- **Test thoroughly** with paper trading first
- **Implement proper risk controls** and position limits
- **Monitor latency and execution** in live markets
- **Understand regulatory requirements** for your jurisdiction
- **Use proper error handling** and logging
- **Implement circuit breakers** for abnormal market conditions

## Contributing

Contributions welcome! Areas for improvement:

- Additional order types (stop-loss, iceberg, etc.)
- More sophisticated market making strategies
- Enhanced risk management features
- Performance optimizations
- Additional market data sources
- Backtesting framework enhancements


## Related Resources

- [Market Microstructure Theory](https://en.wikipedia.org/wiki/Market_microstructure)
- [Order Book Dynamics](https://en.wikipedia.org/wiki/Order_book)
- [Market Making Strategies](https://en.wikipedia.org/wiki/Market_maker)
- [Algorithmic Trading](https://en.wikipedia.org/wiki/Algorithmic_trading)

---
## Credits

This project was developed by:

- Kartik Ramanuj (Project Lead , Strategy & Risk Management  )
- Dharvi Ladani (P&L & Simulation Engine , Visualization & testing)

For questions or contributions, feel free to contact us or open an issue.

**Happy Trading! **
