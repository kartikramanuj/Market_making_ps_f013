# pnl_tracker

class PnLTracker:
    def __init__(self):
        self.realized_pnl = 0
        self.inventory = 0
        self.trades = []

    def record_trade(self, price, quantity, side):
        if side == 'buy':
            self.realized_pnl -= price * quantity
            self.inventory += quantity
        elif side == 'sell':
            self.realized_pnl += price * quantity
            self.inventory -= quantity
        self.trades.append((price, quantity, side))

    def get_summary(self):
        return {
            "Realized P&L": self.realized_pnl,
            "Inventory": self.inventory,
            "Total Trades": len(self.trades)
        }

    def get_cumulative_pnl_series(self):
        pnl_series = []
        cumulative = 0
        for price, quantity, side in self.trades:
            if side == 'buy':
                cumulative -= price * quantity
            elif side == 'sell':
                cumulative += price * quantity
            pnl_series.append(cumulative)
        return pnl_series
