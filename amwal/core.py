from amwal.cache import JsonCache, cached
from amwal.extract import RawExtractor
from amwal.log import logger


class Engine:
    def __init__(self, downloader):
        self.downloader = downloader

    @cached([JsonCache()])
    def daily_bulletin(self, date, ):
        # should validate date here with dateutil.parsing
        date = date.replace("_", "/")
        res = self.downloader.daily_bulletin(date)
        res = RawExtractor.daily_bulletin(res)
        return res

    @cached([JsonCache()])
    def listing(self, ):
        res = self.downloader.listing()
        res = RawExtractor.listing(res)
        return res

    @cached([JsonCache()])
    def income_statement(self, stock_number, ):
        res = self.downloader.income_statement(stock_number)
        res = RawExtractor.income_statement(res)
        return res

    @cached([JsonCache()])
    def price_history(self, stock_symbol, ):
        #changing the logger too late since cache runs first
        res = self.downloader.price_history(stock_symbol)
        res = RawExtractor.price_history(res)
        return res
