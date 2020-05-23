import requests
import json
import re
from enum import Enum
from bs4 import BeautifulSoup
from functools import lru_cache
from dateutil import parser  # use this for date parsing/checking


from amwal.download import SyncDownloader
from amwal.exceptions import (
    StockNumberNotFoundError,
    TickerNotFoundError,
    MalformedCorpIdentifierError,
    DontCacheException,
)
from amwal.extract import RawExtractor
from amwal.log import logger
from amwal.core import Engine


class Market:

    valid_stock_number_patt = re.compile(r"^\d{3,4}$")
    valid_ticker_patt = re.compile(r"^[A-Z]+$")

    def __init__(self, downloader=SyncDownloader, extractor=RawExtractor):
        self.engine = Engine(downloader=downloader, extractor=extractor)

    def daily_bulletin(self, date, **kwargs):
        date = date.strip()
        date = date.replace("/", "_")
        return self.engine.daily_bulletin(date)

    def listing(self, **kwargs):
        return self.engine.listing(**kwargs)

    def find_ticker(self, ticker):
        listing = self.listing()
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
        listing = self.listing()
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

    def get_corporation(self, ident):
        return Corporation(ident, self)

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

    def income_statement(self, **kwargs):
        return self._market.engine.income_statement(self.stock_number)
