from amwal.cache import JsonCache, MemoryCache, cached, SqliteCache
from amwal.extract import RawExtractor


class Engine:
    def __init__(self, downloader):
        self.downloader = downloader

    @cached(
        [
            MemoryCache(maxsize=365),
            SqliteCache(filename="amwal.sqlite", autocommit=True),
        ]
    )
    def daily_bulletin(self, date):
        # should validate date here with dateutil.parsing
        date = date.replace("_", "/")
        res = self.downloader.daily_bulletin(date)
        res = RawExtractor.daily_bulletin(res)
        return res

    @cached(
        [MemoryCache(maxsize=1), SqliteCache(filename="amwal.sqlite", autocommit=True)]
    )
    def listing(self):
        res = self.downloader.listing()
        res = RawExtractor.listing(res)
        return res

    @cached(
        [MemoryCache(maxsize=1), SqliteCache(filename="amwal.sqlite", autocommit=True)]
    )
    def income_statement(self, stock_number):
        res = self.downloader.income_statement(stock_number)
        res = RawExtractor.income_statement(res)
        return res