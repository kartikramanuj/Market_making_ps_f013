from pnl_tracker import PnLTracker
from OrderBook import OrderBook

def test_simple_buy_sell():
    """Test basic buy then sell scenario"""
    print("=== Testing Simple Buy/Sell ===")
    tracker = PnLTracker()
    
    # Buy 1 share at $100
    tracker.record_trade(100, 1, 'buy')  # Should cost $100
    
    # Sell 1 share at $110  
    tracker.record_trade(110, 1, 'sell') # Should get $110
    
    summary = tracker.get_summary()
    print(f"Final summary: {summary}")
    
    # Check the results
    assert summary["Realized P&L"] == 10, f"Expected P&L of 10, got {summary['Realized P&L']}"
    assert summary["Current Inventory"] == 0, f"Expected inventory of 0, got {summary['Current Inventory']}"
    assert summary["Total Trades"] == 2, f"Expected 2 trades, got {summary['Total Trades']}"
    
    print("✓ test_simple_buy_sell PASSED!")
    print()

def test_multiple_trades():
    """Test multiple trades scenario"""
    print("=== Testing Multiple Trades ===")
    tracker = PnLTracker()
    
    # Buy 2 shares at $200 each
    tracker.record_trade(200, 2, 'buy')   # Cost: $400
    
    # Sell 1 share at $210
    tracker.record_trade(210, 1, 'sell')  # Get: $210, P&L: +$10
    
    # Sell another 1 share at $220
    tracker.record_trade(220, 1, 'sell')  # Get: $220, P&L: +$20
    
    summary = tracker.get_summary()
    print(f"Final summary: {summary}")
    
    # Check the results
    assert summary["Realized P&L"] == 30, f"Expected P&L of 30, got {summary['Realized P&L']}"
    assert summary["Current Inventory"] == 0, f"Expected inventory of 0, got {summary['Current Inventory']}"
    
    print("test_multiple_trades PASSED!")
    print()

def test_quote_from_orderbook():
    """Test getting quotes from the order book"""
    print("=== Testing OrderBook Quotes ===")
    ob = OrderBook()
    
    # Add some bid orders (buy orders)
    ob.process_order({'price': 99, 'quantity': 1, 'side': 'bid', 'type': 'limit'})
    ob.process_order({'price': 98, 'quantity': 2, 'side': 'bid', 'type': 'limit'})
    
    # Add some ask orders (sell orders)
    ob.process_order({'price': 101, 'quantity': 1, 'side': 'ask', 'type': 'limit'})
    ob.process_order({'price': 102, 'quantity': 1, 'side': 'ask', 'type': 'limit'})
    
    # Get the best prices
    best_bid = ob.get_best_bid()
    best_ask = ob.get_best_ask()
    
    print(f"Best Bid Price: ${best_bid}")
    print(f"Best Ask Price: ${best_ask}")
    
    # Check the results
    assert best_bid == 99, f"Expected best bid of 99, got {best_bid}"
    assert best_ask == 101, f"Expected best ask of 101, got {best_ask}"
    
    print("✓ test_quote_from_orderbook PASSED!")
    print()

def manual_order_test():
    """Interactive manual testing - this is where the fun happens!"""
    print("=== Manual Order Entry Mode ===")
    print("This is pretty cool - you can enter orders manually and see what happens!")
    print()
    print("Format: type side price quantity")
    print("Examples:")
    print("  limit bid 99.5 2    (place buy limit order)")
    print("  market ask 0 1      (place sell market order)")
    print()
    print("Special commands:")
    print("  'book' - show current order book")
    print("  'pnl' - show P&L summary")
    print("  'exit' or 'quit' - stop testing")
    print()
    
    tracker = PnLTracker()
    book = OrderBook()
    
    while True:
        try:
            user_input = input("Enter order: ").strip()
            
            # Handle special commands
            if user_input.lower() in ["exit", "quit"]:
                break
            elif user_input.lower() == "book":
                print(f"Best Bid: ${book.get_best_bid()}")
                print(f"Best Ask: ${book.get_best_ask()}")
                print(f"Total Bids: {len(book.bids)}, Total Asks: {len(book.asks)}")
                print(f"Total Trades Executed: {len(book.tape)}")
                continue
            elif user_input.lower() == "pnl":
                summary = tracker.get_summary()
                print(f"P&L Summary: {summary}")
                continue
            
            # Parse the order input
            parts = user_input.split()
            if len(parts) != 4:
                print("ERROR: Invalid input format. Use: type side price quantity")
                continue
            
            order_type, side, price_str, qty_str = parts
            
            # Create the order dictionary
            order = {
                "type": order_type,
                "side": side,
                "price": float(price_str),
                "quantity": float(qty_str)
            }
            
            print(f"Processing order: {order}")
            
            # Process the order through the order book
            trades, remaining_order = book.process_order(order, from_data=False, verbose=True)
            
            # Record any trades in the P&L tracker
            for trade in trades:
                print(f"DEBUG - Trade details: {trade}")
                
                # Figure out what side we were on
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
                print(f"SUCCESS: Executed {len(trades)} trade(s)")
                summary = tracker.get_summary()
                print(f"Updated P&L - Cash Flow: ${summary['Net Cash Flow']:.2f}, Realized P&L: ${summary['Realized P&L']:.2f}")
            else:
                print("Order added to book (no immediate execution)")
                
        except Exception as e:
            print(f"ERROR: {e}")
            print("Please try again with correct format")
    
    # Show final summary
    final_summary = tracker.get_summary()
    print("\n" + "="*50)
    print("FINAL MANUAL TEST SUMMARY")
    print("="*50)
    print(f"Total Trades Executed: {final_summary['Total Trades']}")
    print(f"Current Inventory: {final_summary['Current Inventory']}")
    print(f"Net Cash Flow: ${final_summary['Net Cash Flow']:.2f}")
    print(f"Realized P&L: ${final_summary['Realized P&L']:.2f}")
    print("="*50)

if __name__ == "__main__":
    print("Starting P&L and OrderBook Tests...")
    print("="*50)
    
    # Run the automated tests first
    print("Running automated unit tests...")
    test_simple_buy_sell()
    test_multiple_trades()
    test_quote_from_orderbook()
    
    print("All automated tests PASSED! ")
    print()
    
    # Ask if user wants to do manual testing
    choice = input("Do you want to run the manual order test? It's pretty fun! (yes/no): ").strip().lower()
    if choice in ['yes', 'y', 'yeah', 'sure']:
        manual_order_test()
    else:
        print("Okay, maybe next time!")
    
    print("\nThanks for testing! ")
    
