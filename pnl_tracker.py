from typing import Dict, List, Tuple, Optional
import time

class PnLTracker:
    """
    This class tracks my profit and loss from trading.
    It uses FIFO (First In, First Out) accounting to calculate realized P&L.
    It automatically handles long and short positions!
    """
    
    def __init__(self):
        # These lists store my positions
        self.long_positions: List[Tuple[float, float]] = []   # Long positions: (price, quantity)
        self.short_positions: List[Tuple[float, float]] = []  # Short positions: (price, quantity)
        
        # P&L tracking
        self.realized_pnl: float = 0.0  # Money I've actually made/lost
        self.cash_flow: float = 0.0     # Net cash in/out
        self.inventory: float = 0.0     # Current position (positive = long, negative = short)
        self.total_trades: int = 0      # Count of all trades

    def record_trade(self, price: float, quantity: float, side: str):
        """
        Record a trade and update P&L calculations
        This is where the magic happens!
        """
        # Ensure price and quantity are floats for PnLTracker's internal calculations
        price = float(price)
        quantity = float(quantity)

        print(f"Recording trade: {side.upper()} {quantity:.2f} shares @ ${price:.2f}")
        self.total_trades += 1
        
        if side.lower() == 'buy':
            # I'm buying shares
            self.inventory += quantity
            self.cash_flow -= price * quantity  # Cash goes out
            
            # First, check if I'm covering any short positions
            remaining_quantity = quantity
            while remaining_quantity > 0.00001 and self.short_positions: # Use a small epsilon for float comparison
                short_price, short_qty = self.short_positions[0]  # Get oldest short position
                matched_qty = min(remaining_quantity, short_qty)
                
                # Calculate P&L for covering short: (short_price - buy_price) * quantity
                pnl_from_this_match = (short_price - price) * matched_qty
                self.realized_pnl += pnl_from_this_match
                
                print(f"   -> Covering short position: {matched_qty:.2f} @ ${short_price:.2f} with buy @ ${price:.2f}")
                print(f"   -> P&L from this: ${pnl_from_this_match:.2f}")
                
                # Update or remove the short position
                if abs(matched_qty - short_qty) < 0.00001: # Use epsilon for float comparison
                    self.short_positions.pop(0)  # Remove this short position completely
                else:
                    self.short_positions[0] = (short_price, short_qty - matched_qty)
                
                remaining_quantity -= matched_qty
            
            # If there's still quantity left, add it as a new long position
            if remaining_quantity > 0.00001: # Use epsilon
                self.long_positions.append((price, remaining_quantity))
                print(f"   -> Added new long position: {remaining_quantity:.2f} @ ${price:.2f}")
            
            print(f"   -> Cash outflow: ${price * quantity:.2f} (total cash flow: ${self.cash_flow:.2f})")
            print(f"   -> Inventory change: +{quantity:.2f} = {self.inventory:.2f}")
            
        elif side.lower() == 'sell':
            # I'm selling shares
            self.inventory -= quantity
            self.cash_flow += price * quantity  # Cash comes in
            
            # First, check if I'm closing any long positions
            remaining_quantity = quantity
            while remaining_quantity > 0.00001 and self.long_positions: # Use epsilon
                long_price, long_qty = self.long_positions[0]  # Get oldest long position
                matched_qty = min(remaining_quantity, long_qty)
                
                # Calculate P&L for closing long: (sell_price - long_price) * quantity
                pnl_from_this_match = (price - long_price) * matched_qty
                self.realized_pnl += pnl_from_this_match
                
                print(f"   -> Closing long position: {matched_qty:.2f} @ ${long_price:.2f} with sell @ ${price:.2f}")
                print(f"   -> P&L from this: ${pnl_from_this_match:.2f}")
                
                # Update or remove the long position
                if abs(matched_qty - long_qty) < 0.00001: # Use epsilon
                    self.long_positions.pop(0)  # Remove this long position completely
                else:
                    self.long_positions[0] = (long_price, long_qty - matched_qty)
                
                remaining_quantity -= matched_qty
            
            # If there's still quantity left, add it as a new short position
            if remaining_quantity > 0.00001: # Use epsilon
                self.short_positions.append((price, remaining_quantity))
                print(f"   -> Added new short position: {remaining_quantity:.2f} @ ${price:.2f}")
            
            print(f"   -> Cash inflow: ${price * quantity:.2f} (total cash flow: ${self.cash_flow:.2f})")
            print(f"   -> Inventory change: -{quantity:.2f} = {self.inventory:.2f}")
        
        # Print current state for debugging
        print(f"   -> Current long positions: {self.long_positions}")
        print(f"   -> Current short positions: {self.short_positions}")
        print(f"   -> Total realized P&L: ${self.realized_pnl:.2f}")
        print()  # Empty line for readability

    def get_summary(self) -> Dict:
        """
        Get a summary of all the trading statistics
        This is useful for reporting and analysis
        """
        return {
            "Total Trades": self.total_trades,
            "Current Inventory": self.inventory,
            "Net Cash Flow": self.cash_flow,
            "Realized P&L": self.realized_pnl,
            "Open Long Positions": len(self.long_positions),
            "Open Short Positions": len(self.short_positions)
        }

    def get_unrealized_pnl(self, current_price: float) -> float:
        """
        Calculate unrealized P&L based on current market price
        This shows how much money I would make/lose if I closed all positions now
        """
        unrealized = 0.0
        
        # Calculate unrealized P&L for long positions
        for long_price, long_qty in self.long_positions:
            unrealized += (current_price - long_price) * long_qty
        
        # Calculate unrealized P&L for short positions
        for short_price, short_qty in self.short_positions:
            unrealized += (short_price - current_price) * short_qty
        
        return unrealized

    def get_total_pnl(self, current_price: float) -> float:
        """
        Get total P&L (realized + unrealized)
        """
        return self.realized_pnl + self.get_unrealized_pnl(current_price)

