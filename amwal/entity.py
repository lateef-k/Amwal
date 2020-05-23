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
    DontCacheException
)
from amwal.cache import DiskCache, LRUCache, cached_recomputable
from amwal.extractor import RawExtractor
from amwal.log import logger

class Market:

    valid_stock_number_patt = re.compile(r"^\d{3,4}$")
    valid_ticker_patt = re.compile(r"^[A-Z]+$")

    def __init__(
        self, downloader=SyncDownloader, cache=None, extractor=RawExtractor
    ):
        self.downloader = downloader
        self.cache = DiskCache() if not cache else cache
        self.extractor = extractor

    @cached_recomputable(LRUCache(maxsize=365))
    def daily_bulletin(self, date, **kwargs):
        date = date.strip()
        key = Market.date_to_id(date)

        #raise not cache exception if date invalid
        if 'recompute' not in kwargs or not kwargs['recompute']: 
            cache_result = self.cache[key]
            if cache_result:
                return cache_result

        # should validate date here with dateutil.parsing
        res = self.downloader.daily_bulletin(date)
        res = self.extractor.daily_bulletin(res)
        self.cache[key] = res
        return res

    @property
    def listing(self, **kwargs):
        key = "listing"

        if not ('recompute' in kwargs and kwargs['recompute']): 
            cache_result = self.cache[key]
            if cache_result:
                return cache_result

        res = self.downloader.listing()
        res = self.extractor.listing(res)
        self.cache[key] = res
        return res

    def find_ticker(self, ticker):
        listing = self.listing
        found = [stock for stock in listing if stock[1] == ticker]
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
        listing = self.listing
        found = [stock for stock in listing if stock[0] == stock_number]
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

    def get_corporation(self, ident):
        return Corporation(ident, self)

    def disable_cache(self):
        logger.info("Disabling disk cache")
        DiskCache.enabled = False

    def enable_cache(self):
        logger.info("Enabling disk cache")
        DiskCache.enabled = True


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
    def income_statement(self, **kwargs):
        key = f"{self.ticker}_income_stmt"

        cache_result = self._market.cache[key]
        if cache_result:
            return cache_result

        res = self._market.downloader.income_statement(self.stock_number)
        res = self._market.extractor.income_statement(res)

        self._market.cache[key] = res
        return res
