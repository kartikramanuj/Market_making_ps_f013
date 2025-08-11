from pnl_tracker import PnLTracker
from OrderBook import OrderBook
from decimal import Decimal  # Import Decimal for consistent type handling
import time  # For adding delays in manual test



def test_simple_buy_sell():
    """Test basic buy then sell scenario"""
    print("=== Testing Simple Buy/Sell ===")
    tracker = PnLTracker()
    
    # Buy 1 share at $100
    tracker.record_trade(100, 1, 'buy')  # Should cost $100
    
    # Sell 1 share at $110  
    tracker.record_trade(110, 1, 'sell')  # Should get $110
    
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
    
    print("✓ test_multiple_trades PASSED!")
    print()


def test_quote_from_orderbook():
    """Test getting quotes from the order book"""
    print("=== Testing OrderBook Quotes ===")
    ob = OrderBook()
    
    # Add some bid orders (buy orders) - Use Decimal for prices
    ob.process_order({'price': Decimal('99'), 'quantity': 1, 'side': 'bid', 'type': 'limit'})
    ob.process_order({'price': Decimal('98'), 'quantity': 2, 'side': 'bid', 'type': 'limit'})
    
    # Add some ask orders (sell orders) - Use Decimal for prices
    ob.process_order({'price': Decimal('101'), 'quantity': 1, 'side': 'ask', 'type': 'limit'})
    ob.process_order({'price': Decimal('102'), 'quantity': 1, 'side': 'ask', 'type': 'limit'})
    
    # Get the best prices
    best_bid = ob.get_best_bid()
    best_ask = ob.get_best_ask()
    
    print(f"Best Bid Price: ${best_bid}")
    print(f"Best Ask Price: ${best_ask}")
    
    # Check the results - Compare with float as get_best_bid/ask return float
    assert best_bid == 99.0, f"Expected best bid of 99, got {best_bid}"
    assert best_ask == 101.0, f"Expected best ask of 101, got {best_ask}"
    
    print("✓ test_quote_from_orderbook PASSED!")
    print()


def manual_order_test():
    """Interactive manual testing - FIXED VERSION with proper Decimal handling"""
    print("=== Manual Order Entry Mode  ===")
    print("This version properly handles Decimal/float type conversions and partial fills!")
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
                print(f"Total Bids: {book.bids.num_orders}, Total Asks: {book.asks.num_orders}")  # Use num_orders
                
                # Show some order book depth
                print("\n--- Order Book Depth ---")
                if book.bids.depth > 0:
                    print("Top Bids:")
                    # Sort by price (Decimal) and take top 3
                    bid_prices = sorted(book.bids.price_map.keys(), reverse=True)[:3]
                    for price in bid_prices:
                        volume = book.bids.price_map[price].volume
                        print(f"  ${float(price):.2f}: {float(volume):.2f} shares")  # Convert to float for display
                
                if book.asks.depth > 0:
                    print("Top Asks:")
                    # Sort by price (Decimal) and take top 3
                    ask_prices = sorted(book.asks.price_map.keys())[:3]
                    for price in ask_prices:
                        volume = book.asks.price_map[price].volume
                        print(f"  ${float(price):.2f}: {float(volume):.2f} shares")  # Convert to float for display
                print("------------------------")
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
            
            # FIXED: Convert to Decimal for price, quantity can be float
            try:
                price_val = Decimal(price_str) if order_type == 'limit' else Decimal('0')  # Price only relevant for limit
                quantity_val = float(qty_str)
            except (ValueError, TypeError) as e:
                print(f"ERROR: Invalid number format - {e}")
                continue
            
            # Create the order dictionary with proper types
            order = {
                "type": order_type,
                "side": side,
                "price": price_val,  # Use Decimal for price
                "quantity": quantity_val  # Quantity can be float, OrderBook will handle
            }
            
            print(f"Processing order: {order}")
            
            # Process the order through the order book
            trades, remaining_order = book.process_order(order, from_data=False, verbose=True)
            
            # Record any trades in the P&L tracker
            for trade in trades:
                print(f"DEBUG - Trade details: {trade}")
                
                # Figure out what side we were on
                our_side = trade.get('our_side', 'unknown')
                if our_side == 'bid':  # If our order was a bid, we bought
                    our_side = 'buy'
                elif our_side == 'ask':  # If our order was an ask, we sold
                    our_side = 'sell'
                
                if our_side in ['buy', 'sell']:
                    # Convert Decimal price/quantity from trade back to float for PnLTracker
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
                
            time.sleep(0.1)  # Add a small delay for readability in manual mode
                
        except Exception as e:
            print(f"ERROR: {e}")
            print("Please try again with correct format")
            import traceback
            traceback.print_exc()  # Print full traceback for debugging
    
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


def demo_working_scenario():
    """Demonstrate a working trading scenario"""
    print("=== Demo: Working Trading Scenario ===")
    print("This shows how the system should work when everything is set up correctly")
    print()
    
    tracker = PnLTracker()
    book = OrderBook()
    
    # Step 1: Add some initial liquidity
    print("Step 1: Adding initial market maker orders...")
    orders_to_place = [
        {'type': 'limit', 'side': 'bid', 'price': Decimal('99.50'), 'quantity': 5, 'order_id': 101, 'trade_id': 'mm_101','timestamp': int(time.time()) },
        {'type': 'limit', 'side': 'bid', 'price': Decimal('99.00'), 'quantity': 3, 'order_id': 102, 'trade_id': 'mm_102','timestamp': int(time.time()) },
        {'type': 'limit', 'side': 'ask', 'price': Decimal('100.50'), 'quantity': 5, 'order_id': 201, 'trade_id': 'mm_201','timestamp': int(time.time()) },
        {'type': 'limit', 'side': 'ask', 'price': Decimal('101.00'), 'quantity': 3, 'order_id': 202, 'trade_id': 'mm_202','timestamp': int(time.time()) },
    ]
    
    for order in orders_to_place:
        # Pass from_data=True to prevent OrderBook from generating new order_ids
        book.process_order(order, from_data=True, verbose=False) 
        print(f"  Added: {order['side']} {order['quantity']} @ ${order['price']}")
    
    print(f"\nOrder book state:")
    print(f"Best Bid: ${book.get_best_bid()}, Best Ask: ${book.get_best_ask()}")
    if book.get_best_bid() and book.get_best_ask():
        print(f"Spread: ${float(book.get_best_ask()) - float(book.get_best_bid()):.2f}")
    
    # Step 2: Execute some trades
    print("\nStep 2: Executing trades...")
    
    # Buy at market (should hit the ask)
    # This order will have a new trade_id generated by OrderBook
    market_buy = {'type': 'market', 'side': 'bid', 'quantity': 2} 
    trades, _ = book.process_order(market_buy, verbose=True)
    
    for trade in trades:
        tracker.record_trade(float(trade['price']), float(trade['quantity']), 'buy')
    
    # Sell at market (should hit the bid)  
    market_sell = {'type': 'market', 'side': 'ask', 'quantity': 1}
    trades, _ = book.process_order(market_sell, verbose=True)
    
    for trade in trades:
        tracker.record_trade(float(trade['price']), float(trade['quantity']), 'sell')
    
    # Demonstrate partial fill scenario
    print("\nStep 3: Demonstrating partial fill...")
    # Add a new bid order that will partially fill an existing ask
    book.process_order({'price': Decimal('100.50'), 'quantity': 3, 'side': 'bid', 'type': 'limit', 'order_id': 301, 'trade_id': 'test_301','timestamp': int(time.time()) }, from_data=True, verbose=True)
    
    # This should consume 3 from the 100.50 ask (which had 5, now 2 remaining)
    
    print("\nFinal Order Book State after partial fill:")
    print(book)

    # Show final results
    print(f"\nFinal Results:")
    summary = tracker.get_summary()
    for key, value in summary.items():
        if isinstance(value, float):
            print(f"  {key}: ${value:.2f}")
        else:
            print(f"  {key}: {value}")
    
    print("✓ Demo completed successfully!")
    print()


if __name__ == "__main__":
    print("Starting  P&L and OrderBook Tests...")
    print("="*50)
    
    # Run the automated tests first
    print("Running automated unit tests...")
    test_simple_buy_sell()
    test_multiple_trades()
    test_quote_from_orderbook()
    
    print("All automated tests PASSED!")
    print()
    
    # Run the demo
    demo_working_scenario()
    
    # Ask if user wants to do manual testing
    choice = input("Do you want to run the manual order test? (yes/no): ").strip().lower()
    if choice in ['yes', 'y', 'yeah', 'sure']:
        manual_order_test()
    else:
        print("Okay, maybe next time!")
    
    print("\nThanks for testing!")

    


