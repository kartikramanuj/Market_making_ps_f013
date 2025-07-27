from pnl_tracker import PnLTracker
from OrderBook import OrderBook

def test_simple_buy_sell():
    tracker = PnLTracker()
    tracker.record_trade(100, 1, 'buy')  # -100
    tracker.record_trade(110, 1, 'sell') # +110
    summary = tracker.get_summary()
    
    print(f" Summary: {summary}")
    assert summary["Realized P&L"] == 10
    assert summary["Inventory"] == 0
    assert summary["Total Trades"] == 2
    print(" test_simple_buy_sell passed")

def test_multiple_trades():
    tracker = PnLTracker()
    tracker.record_trade(200, 2, 'buy')   # -400
    tracker.record_trade(210, 1, 'sell')  # +210
    tracker.record_trade(220, 1, 'sell')  # +220
    summary = tracker.get_summary()
    
    print(f"Summary: {summary}")
    assert summary["Realized P&L"] == 30
    assert summary["Inventory"] == 0
    print("test_multiple_trades passed")

def test_quote_from_orderbook():
    ob = OrderBook()
    ob.process_order({'price': 99, 'quantity': 1, 'side': 'bid', 'type': 'limit'})
    ob.process_order({'price': 98, 'quantity': 2, 'side': 'bid', 'type': 'limit'})
    ob.process_order({'price': 101, 'quantity': 1, 'side': 'ask', 'type': 'limit'})
    ob.process_order({'price': 102, 'quantity': 1, 'side': 'ask', 'type': 'limit'})
    
    best_bid = ob.get_best_bid()
    best_ask = ob.get_best_ask()
    
    print(f"Best Bid: ${best_bid}, Best Ask: ${best_ask}")
    assert best_bid == 99
    assert best_ask == 101
    print("test_quote_from_orderbook passed")

def manual_order_test():
    """FIXED manual order test - this was your main issue"""
    tracker = PnLTracker()
    book = OrderBook()
    
    print("\n--- Manual Order Entry Mode ---")
    print("Format: type side price quantity (e.g. limit bid 99.5 2 or market ask 0 1)")
    print("Commands: 'book' (show book), 'pnl' (show P&L), 'exit' (quit)")
    print("Type 'exit' or 'quit' to stop.\n")
    
    while True:
        try:
            raw = input("Enter order: ").strip()
            if raw.lower() in ["exit", "quit"]:
                break
            elif raw.lower() == "book":
                print(f"Best Bid: ${book.get_best_bid()}, Best Ask: ${book.get_best_ask()}")
                print(f"Bids: {len(book.bids)}, Asks: {len(book.asks)}, Trades: {len(book.trades)}")
                continue
            elif raw.lower() == "pnl":
                summary = tracker.get_summary()
                print(f" P&L Summary: {summary}")
                continue
            
            parts = raw.split()
            if len(parts) != 4:
                print("Invalid input. Format: type side price quantity")
                continue
            
            order_type, side, price, qty = parts
            order = {
                "type": order_type,
                "side": side,
                "price": float(price),
                "quantity": float(qty)
            }
            
            # FIXED: Process order and handle trades properly
            trades, remaining = book.process_order(order, from_data=False, verbose=True)
            
            # FIXED: Record trades in P&L tracker
            for trade in trades:
                print("DEBUG TRADE:", trade)

                # Use the 'our_side' field to determine what we did
                our_side = trade.get('our_side', 'unknown')
                if our_side == 'bid':
                   our_side = 'buy'
                elif our_side == 'ask':
                  our_side = 'sell'
                if our_side in ['buy', 'sell']:
                    tracker.record_trade(
                        float(trade['price']),
                        float(trade['quantity']),
                        our_side
                    )
            
            # Show results
            if trades:
                print(f"Executed {len(trades)} trades")
                summary = tracker.get_summary()
                print(f"Updated P&L: Cash Flow=${summary['Cash Flow']:.2f}, Realized P&L=${summary['Realized P&L']:.2f}")
            else:
                print("Order added to book (no execution)")
                
        except Exception as e:
            print(f"Error: {e}")
    
    # Final summary
    summary = tracker.get_summary()
    print("\n Final Manual Test Summary:")
    print(f"Total Trades: {summary['Total Trades']}")
    print(f"Inventory   : {summary['Inventory']}")
    print(f"Cash Flow   : ${summary['Cash Flow']:.2f}")
    print(f"Realized P&L: ${summary['Realized P&L']:.2f}")

if __name__ == "__main__":
    # Run automated unit tests
    print(" Running automated tests...")
    test_simple_buy_sell()
    test_multiple_trades()
    test_quote_from_orderbook()
    
    print("\n All automated tests passed!")
    
    # Ask user if they want to run manual testing
    choice = input("\nRun manual order test? (yes/no): ").strip().lower()
    if choice in ['yes', 'y']:
        manual_order_test()
