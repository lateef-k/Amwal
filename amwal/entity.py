from __future__ import annotations
import re
import pathlib
from dateutil import parser
from pandas import DataFrame, Series


from amwal.download import SyncDownloader
from amwal.exceptions import (
    StockNumberNotFoundError,
    TickerNotFoundError,
    MalformedCorpIdentifierError,
    MalformedDateStringError,
)
from amwal.log import logger
from amwal.core import Engine
from amwal.extract import DataFrameExtractor
from amwal.cache import JsonCache


class Market:

    valid_stock_number_patt = re.compile(r"^\d{3,4}$")
    valid_ticker_patt = re.compile(r"^[A-Z]+$")

    def __init__(self, cache_path="amwal_cache", downloader=SyncDownloader):
        self.engine = Engine(downloader=downloader)
        JsonCache.cache_path = pathlib.Path(cache_path)

        logger.warning("The Boursa website has been updated, the library only works for Market.Listing and Corporation.price_history right now.")

    def daily_bulletin(self, date: str, **kwargs) -> DataFrame:
        try:
            date = parser.parse(date, dayfirst=True)
        except ValueError:
            raise MalformedDateStringError(date)
        else:
            date = date.strftime("%d-%m-%Y")
        date = date.replace("-", "_")
        return DataFrameExtractor.daily_bulletin(
            self.engine.daily_bulletin(date, **kwargs)
        )

    def listing(self, **kwargs) -> DataFrame:
        return DataFrameExtractor.listing(self.engine.listing(**kwargs))

    def find_ticker(self, ticker: str, **kwargs) -> dict:
        listing = self.listing()
        found = listing.loc[lambda df: df['Ticker'] == ticker.upper()]
        if not found.empty:
            return found.to_dict("records")[0]
        else:
            raise TickerNotFoundError(ticker)

    def find_stock_index(self, stock_index: int, **kwargs) -> dict:
        listing = self.listing()
        found = listing.loc[lambda df: df['Stock Index'] == stock_index]

        if not found.empty:
            return found.to_dict("records")[0]
        else:
            raise StockNumberNotFoundError(stock_index)

    @staticmethod
    def is_ticker(ident: str) -> bool:
        if re.match(Market.valid_ticker_patt, ident):
            return True
        else:
            return False

    @staticmethod
    def is_stock_number(ident: str) -> bool:
        if re.match(Market.valid_stock_number_patt, ident):
            return True
        else:
            return False

    def get_corporation(self, ident: str, **kwargs) -> Corporation:
        return Corporation(ident, self, **kwargs)


class Corporation:
    def __init__(self, ident: str, market: Market, **kwargs):

        if isinstance(ident, int):
            ident = str(ident)
        elif isinstance(ident, str):
            ident = ident.upper()
        else:
            raise MalformedCorpIdentifierError(ident)

        if market.is_stock_number(ident):
            ret = market.find_stock_number(ident, **kwargs)
        elif market.is_ticker(ident):
            ret = market.find_ticker(ident, **kwargs)
        else:
            raise MalformedCorpIdentifierError(ident)
        self.index = ret["Stock Index"]
        self.ticker = ret["Ticker"]
        self.name = ret["Name"]
        self.sector = ret["Sector"]
        self.listing_type = ret["Market Segment"]
        self._market = market

    def _income_statement(self, **kwargs):
        return self._market.engine.income_statement(self.index, **kwargs)

    def _price_history(self, **kwargs):
        return self._market.engine.price_history(self.ticker, **kwargs)

    def price_history(self, **kwargs):
        return DataFrameExtractor.price_history(self._price_history(**kwargs))

    def yearly_income(self, **kwargs):
        return DataFrameExtractor.yearly_income(self._income_statement(**kwargs))

    def quarterly_income(self, **kwargs):
        return DataFrameExtractor.quarterly_income(self._income_statement(**kwargs))
