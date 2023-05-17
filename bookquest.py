"""This product includes software developed by Bryant Moscon
(http://www.bryantmoscon.com/)"""

from cryptofeed import FeedHandler
from cryptofeed.defines import L2_BOOK
from cryptofeed.types import OrderBook
from cryptofeed.exchanges import BinanceFutures
from cryptofeed.backends.aggregate import Throttle
from questdb.ingress import Sender, IngressError, TimestampNanos
import sys
import asyncio
from concurrent.futures import ProcessPoolExecutor
import logging
from sys import stdout

# Define logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logFormatter = logging.Formatter(\
    "%(asctime)s %(levelname)-8s %(filename)s:%(funcName)s %(message)s")
consoleHandler = logging.StreamHandler(stdout)
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)

QUEST_HOST = '127.0.0.1'
QUEST_PORT = 9009

def push_to_db(key: str, exchange: str, symbol: str, vals: str, receipt_timestamp: int, timestamp: int) -> None:
    """Insert new row into QuestDB table.

    It will automatically create a new table if it doesn't exists yet.
    Args:
        key (str): _description_
        exchange (str): _description_
        symbol (str): _description_
        vals (str): _description_
        receipt_timestamp (int): _description_
        timestamp (int): _description_
    """
    logger.info(f"Pushing data to QuestDB table={key}")
    try:
        with Sender(QUEST_HOST, QUEST_PORT) as sender:
            task = sender.row(
                key,
                symbols={
                    'pair': symbol,
                    'exchange': exchange},
                columns={
                    'orders': vals,
                    'receipt_timestamp': receipt_timestamp,
                    'timestamp': timestamp},
                at=TimestampNanos.now())
            sender.flush()
    except IngressError as e:
        sys.stderr.write(f'Got error: {e}\n')

async def callback(data: OrderBook, receipt: float, key: str='book', depth: int=1) -> None:
    """
    Custom callback for L2_BOOK Cryptofeed channel that pushes data to QuestDB
    Args:
        data (OrderBook): _description_
        receipt (float): _description_
        key (str, optional): _description_. Defaults to 'book'.
        depth (int, optional): _description_. Defaults to 1.
    """
    loop = asyncio.get_event_loop()
    book = data.book
    vals = ','.join([f"bid_{i}_price={book.bids.index(i)[0]},bid_{i}_size={book.bids.index(i)[1]}" \
        for i in range(depth)] + \
        [f"ask{i}_price={book.asks.index(i)[0]},ask_{i}_size={book.asks.index(i)[1]}" \
        for i in range(depth)])
    receipt_timestamp = receipt
    receipt_timestamp_int = int(receipt_timestamp * 1_000_000)
    timestamp_int = int(receipt_timestamp_int * 1000)
    with ProcessPoolExecutor() as p:
        await loop.run_in_executor(p, \
            push_to_db, key, data.exchange, data.symbol, vals, receipt_timestamp_int, timestamp_int)

def main() -> None:
    """Get top of the Binance Futures orderbook in a given time window."""
    f = FeedHandler()
    f.add_feed(
        BinanceFutures(
            symbols=['BTC-USDT-PERP', 'ETH-USDT-PERP'], 
            channels=[L2_BOOK], 
            callbacks={
                L2_BOOK: Throttle(callback, window=60)
            }
       )
    )
    f.run()

if __name__ == '__main__':
    main()