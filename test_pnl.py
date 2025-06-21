# test_pnl.py

from pnl_tracker import PnLTracker

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

if __name__ == "__main__":
    test_simple_buy_sell()
    test_multiple_trades()
