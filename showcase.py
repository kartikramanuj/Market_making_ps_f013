import asyncio
import json
import websockets
from decimal import Decimal
from collections import defaultdict
from OrderBook import OrderBook
from OrderBook import OrderTree

# Binance local snapshot storage
bids = defaultdict(Decimal)
asks = defaultdict(Decimal)

# Your own order matching engine
ob = OrderBook(symbol='BTC/USDT', tick_size=Decimal('0.01'))

def print_binance_book():
    print("\n==== Binance Order Book ====")
    top_bids = sorted(bids.items(), key=lambda x: x[0], reverse=True)[:5]
    top_asks = sorted(asks.items(), key=lambda x: x[0])[:5]
    print("Bids:")
    for price, qty in top_bids:
        print(f"  {price} -> {qty}")
    print("Asks:")
    for price, qty in top_asks:
        print(f"  {price} -> {qty}")

async def binance_order_book(symbol="btcusdt"):
    ws_url = f"wss://stream.binance.com:9443/ws/{symbol}@depth20@100ms"

    async with websockets.connect(ws_url) as websocket:
        print(f"Connected to Binance order book stream for {symbol.upper()}.")
        message_count = 0
        max_messages = 5  # adjust this as you want

        while message_count < max_messages:
            message = await websocket.recv()
            data = json.loads(message)
            message_count += 1
            bids_list = data.get('bids', [])
            asks_list = data.get('asks', [])
            bids.clear()
            asks.clear()

            # Build new snapshot
            for price_str, qty_str in bids_list:
                price = Decimal(price_str)
                qty = Decimal(qty_str)
                if qty > 0:
                    bids[price] = qty

            for price_str, qty_str in asks_list:
                price = Decimal(price_str)
                qty = Decimal(qty_str)
                if qty > 0:
                    asks[price] = qty

            
            ob.bids = OrderTree()
            ob.asks = OrderTree()


            for price, qty in bids.items():
                ob.process_order({
                    'type': 'limit',
                    'side': 'bid',
                    'price': price,
                    'quantity': qty,
                    'trade_id': 'binance'
                }, from_data=False, verbose=False)

            for price, qty in asks.items():
                ob.process_order({
                    'type': 'limit',
                    'side': 'ask',
                    'price': price,
                    'quantity': qty,
                    'trade_id': 'binance'
                }, from_data=False, verbose=False)

            # Print both books
            print_binance_book()
            print("\n==== Your Internal OrderBook ====")
            print(ob)

asyncio.run(binance_order_book())
