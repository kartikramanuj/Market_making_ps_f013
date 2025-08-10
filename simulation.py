import time
import random
import threading
import argparse
import json
from dataclasses import dataclass
from OrderBook import OrderBook

@dataclass
class Config:
    duration: int = 60
    order_rate: float = 2.0
    base_price: float = 100.0
    volatility: float = 0.02
    spread: float = 0.01
    market_ratio: float = 0.3
    trend: float = 0.0
    depth: int = 5
    min_size: float = 1.0
    max_size: float = 10.0

class Simulator:
    def __init__(self, config: Config):
        self.cfg = config
        self.book = OrderBook()
        self.price = config.base_price
        self.history = [self.price]
        self.running = False
        self.thread = None
        self.callbacks = []
        self.order_counter = 0
        self.order_id_counter = 0

    def add_callback(self, fn):
        self.callbacks.append(fn)

    def _notify(self, event: str, data: dict):
        for fn in self.callbacks:
            try: 
                fn(event, data)
            except: 
                pass

    def _market_maker(self):
        """Place market maker orders around current price"""
        half_spread = self.cfg.spread * self.price / 2
        
        for i in range(self.cfg.depth):
            offset = half_spread * (1 + i * 0.5)
            qty = round(random.uniform(self.cfg.min_size, self.cfg.max_size), 4)
            
            # Place bid order
            bid_price = round(self.price - offset, 4)
            self.order_counter += 1
            bid_order = {
                'order_id': f"mm_bid_{i}_{self.order_counter}",
                'type': 'limit',
                'side': 'bid',
                'quantity': qty,
                'order_id': self.order_id_counter,
                'price': bid_price
            }
            
            try:
                trades, _ = self.book.process_order(bid_order, verbose=False)
                if trades:
                    self._process_trades(trades)
                    self._notify("trade", {"trades": trades})
            except Exception as e:
                print(f"Market maker bid order failed: {e}")
            
            # Place ask order
            ask_price = round(self.price + offset, 4)
            self.order_counter += 1
            ask_order = {
                'order_id': f"mm_ask_{i}_{self.order_counter}",
                'type': 'limit',
                'side': 'ask',
                'quantity': qty,
                'order_id': self.order_id_counter,
                'price': ask_price
            }
            
            try:
                trades, _ = self.book.process_order(ask_order, verbose=False)
                if trades:
                    self._process_trades(trades)
                    self._notify("trade", {"trades": trades})
            except Exception as e:
                print(f"Market maker ask order failed: {e}")
    def _random_order(self):
        """Generate random market participant order"""
        is_mkt = random.random() < self.cfg.market_ratio
        side = 'bid' if random.random() < (0.5 + self.cfg.trend * 0.3) else 'ask'
        qty = round(random.uniform(self.cfg.min_size, self.cfg.max_size), 4)
        self.order_id_counter += 1
        order = {
            'order_id': f"random_{side}_{self.order_id_counter}",
            'type': 'market' if is_mkt else 'limit',
            'side': side,
            'quantity': qty
        }

        if not is_mkt:
            shift = random.uniform(0, self.cfg.volatility * self.price)
            price = self.price - shift if side == 'bid' else self.price + shift
            order['price'] = round(max(0.01, price), 4)

        return order

    def _update_price(self):
        """Update price based on recent trades"""
        if hasattr(self.book, 'tape') and self.book.tape:
            recent = list(self.book.tape)[-10:]
            if recent:
                vol = sum(float(t.get('quantity', 0)) for t in recent)
                if vol > 0:
                    vwap = sum(float(t.get('price', 0)) * float(t.get('quantity', 0)) for t in recent) / vol
                    self.price = 0.9 * self.price + 0.1 * vwap
        
        # Add random walk
        self.price += random.gauss(0, self.cfg.volatility * self.price * 0.1)
        self.price = max(0.01, self.price)
        self.history.append(self.price)
        
        if len(self.history) > 1000:
            self.history = self.history[-1000:]

    def _get_best_bid(self):
        """Safely get best bid price"""
        try:
            bid = self.book.get_best_bid()
            return float(bid) if bid is not None else None
        except:
            return None

    def _get_best_ask(self):
        """Safely get best ask price"""
        try:
            ask = self.book.get_best_ask()
            return float(ask) if ask is not None else None
        except:
            return None

    def _loop(self):
        """Main simulation loop"""
        start = time.time()
        next_order = start
        next_mm = start + 5  # Market maker refresh every 5 seconds
        
        # Initial market making
        print("Placing initial market maker orders...")
        self._market_maker()

        while self.running and (time.time() - start < self.cfg.duration):
            now = time.time()
            
            # Generate random orders
            if now >= next_order:
                order = self._random_order()
                try:
                    trades, _ = self.book.process_order(order, verbose=False)
                    if trades: 
                        self._notify("trade", {"trades": trades})
                    self._update_price()
                    self._notify("order", {"order": order})
                except Exception as e:
                    pass  # Silently handle order failures
                
                next_order = now + random.expovariate(self.cfg.order_rate)
            
            # Refresh market maker orders
            if now >= next_mm:
                try:
                    # Count total orders in book
                    total_orders = len(self.book.bids) + len(self.book.asks)
                    if total_orders < 20:
                        self._market_maker()
                except:
                    self._market_maker()
                next_mm = now + 5
            
            # Send market data update
            self._notify("market_data", {
                "price": self.price,
                "best_bid": self._get_best_bid(),
                "best_ask": self._get_best_ask(),
                "timestamp": now
            })
            
            time.sleep(0.1)
        
        print("Simulation completed.")

    def start(self):
        """Start simulation in separate thread"""
        if self.running: 
            return
        self.running = True
        self.thread = threading.Thread(target=self._loop)
        self.thread.start()

    def stop(self):
        
        self.running = False
        if self.thread: 
            self.thread.join()

    def stats(self) -> dict:
        """Get simulation statistics"""
        changes = [(self.history[i] - self.history[i-1]) / self.history[i-1] 
                  for i in range(1, len(self.history))]
        
        total_trades = len(self.book.tape) if hasattr(self.book, 'tape') else 0
        total_volume = sum(float(t.get('quantity', 0)) for t in self.book.tape) if hasattr(self.book, 'tape') else 0.0
        
        return {
            "price": {
                "start": self.cfg.base_price,
                "end": self.price,
                "change": (self.price - self.cfg.base_price) / self.cfg.base_price,
                "min": min(self.history),
                "max": max(self.history),
                "realized_vol": sum(abs(c) for c in changes) / len(changes) if changes else 0
            },
            "trades": {
                "count": total_trades,
                "volume": total_volume,
                "avg_size": total_volume / total_trades if total_trades > 0 else 0
            }
        }

def main():
    """Standalone simulation runner"""
    p = argparse.ArgumentParser(description="Market Simulation")
    p.add_argument('--duration', type=int, default=60)
    p.add_argument('--order-rate', type=float, default=2.0)
    p.add_argument('--base-price', type=float, default=118190.0)
    p.add_argument('--volatility', type=float, default=0.02)
    p.add_argument('--spread', type=float, default=0.01)
    p.add_argument('--market-ratio', type=float, default=0.3)
    p.add_argument('--trend', type=float, default=0.0)
    p.add_argument('--depth', type=int, default=5)
    p.add_argument('--min-size', type=float, default=1.0)
    p.add_argument('--max-size', type=float, default=10.0)
    p.add_argument('--monitor', action='store_true')
    p.add_argument('--export', type=str)
    
    args = p.parse_args()
    
    cfg = Config(
        duration=args.duration, order_rate=args.order_rate, base_price=args.base_price,
        volatility=args.volatility, spread=args.spread, market_ratio=args.market_ratio,
        trend=args.trend, depth=args.depth, min_size=args.min_size, max_size=args.max_size
    )
    
    sim = Simulator(cfg)
    
    if args.monitor:
        def cb(evt, data):
            if evt == 'trade':
                for t in data['trades']:
                    print(f"TRADE: {t.get('quantity', 0):.2f} @ ${t.get('price', 0):.2f}")
            elif evt == 'market_data':
                md = data
                bid = f"${md['best_bid']:.2f}" if md['best_bid'] else "N/A"
                ask = f"${md['best_ask']:.2f}" if md['best_ask'] else "N/A"
                print(f"MARKET: ${md['price']:.2f} | Bid: {bid}, Ask: {ask}")
        sim.add_callback(cb)
    
    sim.start()
    sim.thread.join()
    
    stats = sim.stats()
    print(f"\n{'='*40}")
    print("SIMULATION RESULTS")
    print(f"{'='*40}")
    print(f"Price: ${stats['price']['start']:.2f} → ${stats['price']['end']:.2f} ({stats['price']['change']:.2%})")
    print(f"Range: ${stats['price']['min']:.2f} - ${stats['price']['max']:.2f}")
    print(f"Volatility: {stats['price']['realized_vol']:.2%}")
    print(f"Trades: {stats['trades']['count']} (Vol: {stats['trades']['volume']:.2f})")
    print(f"Avg Trade: {stats['trades']['avg_size']:.2f}")
    
    if args.export:
        with open(args.export, 'w') as f:
            json.dump(stats, f, indent=2)

if __name__ == '__main__':
    main()


