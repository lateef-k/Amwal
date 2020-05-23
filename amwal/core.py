
from amwal.cache import DiskCache, MemoryCache, cached


class Engine:
    def __init__(self, downloader, extractor):
        self.downloader = downloader
        self.extractor = extractor

    @cached([MemoryCache(maxsize=365), DiskCache()])
    def daily_bulletin(self, date):
        # should validate date here with dateutil.parsing
        date = date.replace("_", "/")
        res = self.downloader.daily_bulletin(date)
        res = self.extractor.daily_bulletin(res)
        return res

    @cached([MemoryCache(maxsize=1), DiskCache()])
    def listing(self):
        res = self.downloader.listing()
        res = self.extractor.listing(res)
        return res

    @cached([MemoryCache(maxsize=1), DiskCache()])
    def income_statement(self, stock_number):
        res = self.downloader.income_statement(stock_number)
        res = self.extractor.income_statement(res)
        return res
