# test_pnl.py

from pnl_tracker import PnLTracker
from OrderBook import OrderBook

def test_simple_buy_sell():
    tracker = PnLTracker()
    tracker.record_trade(100, 1, 'buy')  # -100
    tracker.record_trade(110, 1, 'sell') # +110
    summary = tracker.get_summary()
    assert summary["Realized P&L"] == 10
    assert summary["Inventory"] == 0
    assert summary["Total Trades"] == 2
    print("test_simple_buy_sell passed")

def test_multiple_trades():
    tracker = PnLTracker()
    tracker.record_trade(200, 2, 'buy')   # -400
    tracker.record_trade(210, 1, 'sell')  # +210
    tracker.record_trade(220, 1, 'sell')  # +220
    summary = tracker.get_summary()
    assert summary["Realized P&L"] == 30
    assert summary["Inventory"] == 0
    print("test_multiple_trades passed")

def test_quote_from_orderbook():
    ob = OrderBook()

    # Add buy orders
    ob.process_order({'price': 99, 'quantity': 1, 'side': 'buy'})
    ob.process_order({'price': 98, 'quantity': 2, 'side': 'buy'})

    # Add sell orders
    ob.process_order({'price': 101, 'quantity': 1, 'side': 'sell'})
    ob.process_order({'price': 102, 'quantity': 1, 'side': 'sell'})

    # Get best bid/ask
    best_bid = ob.get_best_bid()
    best_ask = ob.get_best_ask()

    assert best_bid == 99
    assert best_ask == 101

    print("test_quote_from_orderbook passed")

if __name__ == "__main__":
    test_simple_buy_sell()
    test_multiple_trades()
    test_quote_from_orderbook()
