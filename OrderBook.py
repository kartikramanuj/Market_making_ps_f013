import sys
from collections import deque
from decimal import Decimal, getcontext # Import Decimal
from ordertree import OrderTree
from io import StringIO
import time
# Set global decimal precision (important for crypto)
getcontext().prec = 10


class OrderBook:
    def __init__(self, symbol='BTC/USD', tick_size=Decimal('0.01')): # Use Decimal for tick_size
        self.symbol = symbol
        self.tick_size = tick_size

        self.bids = OrderTree()
        self.asks = OrderTree()
        self.tape = deque(maxlen=None)  # recent trades
        self.time = 0
        self.next_order_id = 0

    # ---- Order Book Core Time Handling ----
    def update_time(self):
        self.time += 1

    # ---- Processing Orders ----
    def process_order(self, quote, from_data=False, verbose=False):
        order_type = quote['type']
        order_in_book = None
        if from_data:
            self.time = quote['timestamp']
        else:
            self.update_time()
            quote['timestamp'] = self.time

        if quote['quantity'] <= 0:
            sys.exit('process_order() given order of quantity <= 0')

        if not from_data:
            self.next_order_id += 1
            quote['trade_id'] = self.next_order_id
            # Ensure order_id is also set for the quote if it's a new order
            if 'order_id' not in quote:
                quote['order_id'] = self.next_order_id


        if order_type == 'market':
            trades = self._process_market_order(quote, verbose)
        elif order_type == 'limit':
            # Ensure price is Decimal when it enters the OrderBook
            if not isinstance(quote['price'], Decimal):
                quote['price'] = Decimal(str(quote['price'])) # Convert to string first to avoid float precision issues
            trades, order_in_book = self._process_limit_order(quote, from_data, verbose)
        else:
            sys.exit("order_type must be 'market' or 'limit'")
        return trades, order_in_book

    def _process_market_order(self, quote, verbose):
        trades = []
        quantity_to_trade = quote['quantity']
        side = quote['side']
        if side == 'bid':
            while quantity_to_trade > 0 and self.asks:
                best_asks = self.asks.min_price_list()
                quantity_to_trade, new_trades = self._process_order_list('ask', best_asks, quantity_to_trade, quote, verbose)
                trades += new_trades
        elif side == 'ask':
            while quantity_to_trade > 0 and self.bids:
                best_bids = self.bids.max_price_list()
                quantity_to_trade, new_trades = self._process_order_list('bid', best_bids, quantity_to_trade, quote, verbose)
                trades += new_trades
        else:
            sys.exit('process_market_order() received neither "bid" nor "ask"')
        return trades

    def _process_limit_order(self, quote, from_data, verbose):
        order_in_book = None
        trades = []
        quantity_to_trade = quote['quantity']
        side = quote['side']
        price = quote['price'] # Price is already Decimal from process_order

        if side == 'bid':
            while self.asks and price >= self.asks.min_price() and quantity_to_trade > 0:
                best_asks = self.asks.min_price_list()
                quantity_to_trade, new_trades = self._process_order_list('ask', best_asks, quantity_to_trade, quote, verbose)
                trades += new_trades
            if quantity_to_trade > 0:
                if not from_data:
                    # order_id is already set in process_order for new orders
                    pass 
                quote['quantity'] = quantity_to_trade
                self.bids.insert_order(quote)
                order_in_book = quote

        elif side == 'ask':
            while self.bids and price <= self.bids.max_price() and quantity_to_trade > 0:
                best_bids = self.bids.max_price_list()
                quantity_to_trade, new_trades = self._process_order_list('bid', best_bids, quantity_to_trade, quote, verbose)
                trades += new_trades
            if quantity_to_trade > 0:
                if not from_data:
                    # order_id is already set in process_order for new orders
                    pass
                quote['quantity'] = quantity_to_trade
                self.asks.insert_order(quote)
                order_in_book = quote
        else:
            sys.exit('process_limit_order() given neither "bid" nor "ask"')
        return trades, order_in_book

    # ---- Matching Engine ----
    def _process_order_list(self, side, order_list, quantity_to_trade, quote, verbose):
     trades = []

     # Ensure quantity_to_trade is Decimal for consistent arithmetic
     quantity_to_trade = Decimal(str(quantity_to_trade))

     while len(order_list) > 0 and quantity_to_trade > 0:
        head_order = order_list.get_head_order()
        traded_price = head_order.price # This is already Decimal
        counter_party = head_order.trade_id
        new_book_quantity = None

        if quantity_to_trade < head_order.quantity:
            traded_quantity = quantity_to_trade
            new_book_quantity = head_order.quantity - quantity_to_trade
            head_order.update_quantity(new_book_quantity, head_order.timestamp)
            quantity_to_trade = Decimal('0') # Set to Decimal zero
        elif quantity_to_trade == head_order.quantity:
            traded_quantity = quantity_to_trade
            self._remove_order(side, head_order.order_id)
            quantity_to_trade = Decimal('0') # Set to Decimal zero
        else:
            traded_quantity = head_order.quantity
            self._remove_order(side, head_order.order_id)
            quantity_to_trade -= traded_quantity

        if verbose:
            print(f"[TRADE] {self.symbol} | Time {self.time} | {traded_quantity} @ {traded_price} | {counter_party} <-> {quote['trade_id']}")

        # This is the trade record that goes to PnL
        trade = {
            "price": traded_price, # Keep as Decimal
            "quantity": traded_quantity, # Keep as Decimal
            "buy_order_id": head_order.order_id if side == 'ask' else quote['trade_id'],
            "sell_order_id": head_order.order_id if side == 'bid' else quote['trade_id'],
            "our_side": quote["side"]  # Add this so PnLTracker knows your role
        }

        trades.append(trade)

        # Also record to trade tape (not necessarily needed by PnLTracker)
        transaction_record = {
            'timestamp': self.time,
            'price': traded_price,
            'quantity': traded_quantity,
            'party1': [counter_party, side, head_order.order_id, new_book_quantity],
            'party2': [quote['trade_id'], 'ask' if side == 'bid' else 'bid', None, None]
        }

        self.tape.append(transaction_record)

     return float(quantity_to_trade), trades # Return float as expected by simulation

    def _remove_order(self, side, order_id):
        if side == 'bid':
            self.bids.remove_order_by_id(order_id)
        else:
            self.asks.remove_order_by_id(order_id)

    # ---- Utilities ----
    def cancel_order(self, side, order_id, time=None):
        self.time = time if time else self.time + 1
        if side == 'bid':
            if self.bids.order_exists(order_id):
                self.bids.remove_order_by_id(order_id)
        elif side == 'ask':
            if self.asks.order_exists(order_id):
                self.asks.remove_order_by_id(order_id)
        else:
            sys.exit('cancel_order() given neither "bid" nor "ask"')

    def modify_order(self, order_id, update, time=None):
        self.time = time if time else self.time + 1
        side = update['side']
        update['order_id'] = order_id
        update['timestamp'] = self.time
        # Ensure price is Decimal for update
        if 'price' in update and not isinstance(update['price'], Decimal):
            update['price'] = Decimal(str(update['price']))
        if side == 'bid' and self.bids.order_exists(order_id):
            self.bids.update_order(update)
        elif side == 'ask' and self.asks.order_exists(order_id):
            self.asks.update_order(update)
        else:
            sys.exit('modify_order() given neither "bid" nor "ask"')

    def get_volume_at_price(self, side, price):
        price = Decimal(str(price)) # Convert to Decimal
        tree = self.bids if side == 'bid' else self.asks
        if tree.price_exists(price):
            return tree.get_price_list(price).volume # Use get_price_list
        return 0

    def get_best_bid(self):
        return self.bids.max_price()

    def get_best_ask(self):
        return self.asks.min_price()

    # ---- String representation ----
    def __str__(self):
        buf = StringIO()
        buf.write(f"=== OrderBook {self.symbol} ===\n")
        buf.write(">> Bids <<\n")
        if self.bids and len(self.bids) > 0:
            for price, orders in reversed(self.bids.price_map.items()):
                buf.write(f"{price}: {orders.volume}\n")
        buf.write(">> Asks <<\n")
        if self.asks and len(self.asks) > 0:
            for price, orders in self.asks.price_map.items():
                buf.write(f"{price}: {orders.volume}\n")
        buf.write(">> Last Trades <<\n")
        for trade in list(self.tape)[-10:]:
            buf.write(f"{trade['quantity']} @ {trade['price']} [{trade['timestamp']}] {trade['party1'][0]}/{trade['party2'][0]}\n")
        return buf.getvalue()


