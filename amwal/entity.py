import requests
import json
import re
from enum import Enum
from bs4 import BeautifulSoup
from functools import lru_cache
from dateutil import parser  # use this for date parsing/checking


from amwal import url
from amwal.download import SyncDownloader
from amwal.exceptions import (
    StockNumberNotFoundError,
    TickerNotFoundError,
    MalformedCorpIdentifierError,
)
from amwal.cache import JsonCache
from amwal.extractor import RawExtractor
from amwal.config import *


class Market:

    valid_stock_number_patt = re.compile(r"^\d{3,4}$")
    valid_ticker_patt = re.compile(r"^[A-Z]+$")

    def __init__(
        self, downloader=SyncDownloader, cache=JsonCache(), extractor=RawExtractor
    ):
        self.downloader = downloader
        self.cache = cache
        self.extractor = extractor

    @lru_cache(365)
    def daily_bulletin(self, date):
        date = date.strip()
        # should validate date here with dateutil.parsing
        cache_result = self.cache.get_resource(Market.date_to_id(date))
        if cache_result:
            return cache_result
        res = self.downloader.daily_bulletin(date)
        res = self.extractor.daily_bulletin(res)
        self.cache.add_resource(Market.date_to_id(date), res)
        return res

    @lru_cache(maxsize=1)
    def listing(self):
        listing_id = "listing"

        cache_result = self.cache.get_resource(listing_id)
        if cache_result:
            return cache_result

        res = self.downloader.listing()
        res = self.extractor.listing(res)
        self.cache.add_resource(listing_id, res)
        return res

    def find_ticker(self, ticker):
        finlan = self.listing()
        found = [stock for stock in finlan if stock[1] == ticker]
        if found:
            found = found[0]
            return {
                "stock_number": found[0],
                "ticker": found[1],
                "name": found[3],
                "sector": found[5],
                "listing_type": found[6],
            }
        else:
            raise TickerNotFoundError(ticker)

    def find_stock_number(self, stock_number):
        finlan = self.listing()
        found = [stock for stock in finlan if stock[0] == stock_number]
        if found:
            found = found[0]
            return {
                "stock_number": found[0],
                "ticker": found[1],
                "name": found[3],
                "sector": found[5],
                "listing_type": found[6],
            }
        else:
            raise StockNumberNotFoundError(stock_number)

    @staticmethod
    def is_ticker(ident):
        if re.match(Market.valid_ticker_patt, ident):
            return True
        else:
            return False

    @staticmethod
    def is_stock_number(ident):
        if re.match(Market.valid_stock_number_patt, ident):
            return True
        else:
            return False

    @staticmethod
    def date_to_id(date):
        return date.replace("/", "_")

    @staticmethod
    def process_json(raw):
        raw = json.loads(raw)["d"]
        raw = json.loads(raw)["aaData"]
        return raw

    def get_corporation(self, ident):
        return Corporation(ident, self)

    def disable_cache(self):
        self.cache.disable()

    def enable_cache(self):
        self.cache.enable()


class Corporation:
    def __init__(self, ident, market):

        if isinstance(ident, int):
            ident = str(ident)
        elif isinstance(ident, str):
            ident = ident.upper()
        else:
            raise MalformedCorpIdentifierError(ident)

        if market.is_stock_number(ident):
            ret = market.find_stock_number(ident)
        elif market.is_ticker(ident):
            ret = market.find_ticker(ident)
        else:
            raise MalformedCorpIdentifierError(ident)

        self.stock_number = ret["stock_number"]
        self.ticker = ret["ticker"]
        self.name = ret["name"]
        self.sector = ret["sector"]
        self.listing_type = ret["listing_type"]
        self._market = market

    @property
    def income_statement(self):
        inc_stmt_id = f"{self.ticker}_income_stmt"

        cache_result = self._market.cache.get_resource(inc_stmt_id)
        if cache_result:
            return cache_result

        res = self._market.downloader.income_statement(self.stock_number)
        res = self._market.extractor.income_statement(res)

        self._market.cache.add_resource(inc_stmt_id, res)

        return res
