
from typing import Dict, List, Tuple, Optional
import time

class PnLTracker:
    def __init__(self):
        self.positions: List[Tuple[float, float]] = []  # List of (price, quantity)
        self.realized_pnl: float = 0.0
        self.cash_flow: float = 0.0
        self.inventory: float = 0.0
        self.total_trades: int = 0

    def record_trade(self, price: float, quantity: float, side: str):
        print(f"Recording: {side.upper()} {quantity} @ ${price:.2f}")
        self.total_trades += 1

        if side.lower() == 'buy':
            self.positions.append((price, quantity))
            self.inventory += quantity
            self.cash_flow -= price * quantity
            print(f"   Cash out: ${price * quantity:.2f} (total: ${self.cash_flow:.2f})")
            print(f"   Inventory: +{quantity} = {self.inventory}")
        elif side.lower() == 'sell':
            self.cash_flow += price * quantity
            self.inventory -= quantity
            remaining = quantity

            while remaining > 0 and self.positions:
                entry_price, entry_qty = self.positions[0]
                matched_qty = min(remaining, entry_qty)
                pnl = (price - entry_price) * matched_qty
                self.realized_pnl += pnl

                if matched_qty == entry_qty:
                    self.positions.pop(0)
                else:
                    self.positions[0] = (entry_price, entry_qty - matched_qty)

                remaining -= matched_qty

            print(f"   Cash in: ${price * quantity:.2f} (total: ${self.cash_flow:.2f})")
            print(f"   Realized P&L: ${self.realized_pnl:.2f}")
            print(f"   Inventory: -{quantity} = {self.inventory}")

    def get_summary(self) -> Dict:
        return {
            "Total Trades": self.total_trades,
            "Inventory": self.inventory,
            "Cash Flow": self.cash_flow,
            "Realized P&L": self.realized_pnl
        }

