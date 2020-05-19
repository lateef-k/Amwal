import requests
import json
import re
from enum import Enum
from bs4 import BeautifulSoup
from functools import lru_cache
from dateutil import parser #use this for date parsing/checking

from amwal import url
from amwal.exceptions import (
    StockNumberNotFoundError,
    TickerNotFoundError,
    MalformedCorpIdentifierError,
)
from amwal.cache import Cache
from amwal.config import *

class FinDataType(Enum):
    INCOME_STATEMENT = "income-statement"
    BALANCE_SHEET = "balance-sheet"
    CASH_FLOW_STATEMENT = "cash-flow-statement"

class Market:

    cache = Cache()

    valid_stock_number_patt = re.compile(r"^\d{3,4}$")
    valid_ticker_patt = re.compile(r"^[A-Z]+$")

    @staticmethod
    @lru_cache(365)
    def daily_bulletin(date):
        date = date.strip()
        #should validate date here with dateutil.parsing
        cache_result = Market.cache.get_resource(Market.date_to_id(date))
        if cache_result:
            return cache_result

        session = requests.session()
        session.cookies.set(name="bk_lang", value="rK1YIM29JoA=")
        session.headers.update({"Content-Type": "application/json; charset=utf-8"})

        logger.info(f"Scraping daily bulletin on {date}")
        res = session.post(url.bulletin, json={"d": date},)

        res = Market.process_json(res.content)
        Market.cache.append_resource(Market.date_to_id(date), res)
        return res

    # Not necessary with listing funciton
    @staticmethod
    @lru_cache(maxsize=1)
    def financial_landing():
        finlan_id = "financial_landing"

        cache_result = Market.cache.get_resource(finlan_id)
        if cache_result:
            return cache_result

        session = requests.session()
        session.cookies.set(name="bk_lang", value="rK1YIM29JoA=")
        session.headers.update({"Content-Type": "application/json; charset=utf-8"})
        logger.info(f"Scraping tne financial data landing page")
        res = session.post(url.finlan)
        res = Market.process_json(res.content)
        Market.cache.append_resource(finlan_id, res)
        return res

    @staticmethod
    @lru_cache(maxsize=1)
    def listing():
        listing_id = "listing"

        cache_result = Market.cache.get_resource(listing_id)
        if cache_result:
            return cache_result

        session = requests.session()
        session.cookies.set(name="bk_lang", value="rK1YIM29JoA=")
        session.headers.update({"Content-Type": "application/json; charset=utf-8"})
        logger.info(f"Scraping the listed companies page")
        res = session.post(url.listing, json={
            "cat":"listed",
            "instrument":""
        })
        res = Market.process_json(res.content)
        for i,row in enumerate(res):
            del row[0]
            row[3] = BeautifulSoup(row[3]).text
            if "#eed122" in row[2]:
                row[2] = "RED"
            elif "#FF0000" in row[2]:
                row[2] = "YELLOW"
        Market.cache.append_resource(listing_id, res)
        return res

    @staticmethod
    def find_ticker(ticker):
        finlan = Market.listing()
        found = [stock for stock in finlan if stock[1] == ticker]
        if found:
            found = found[0]
            return {"stock_number": found[0], "ticker": found[1], "name": found[3], "sector":found[5], "market": found[6]}
        else:
            raise TickerNotFoundError(ticker)

    @staticmethod
    def find_stock_number(stock_number):
        finlan = Market.listing()
        found = [stock for stock in finlan if stock[0] == stock_number]
        if found:
            found = found[0]
            return {"stock_number": found[0], "ticker": found[1], "name": found[3], "sector":found[5], "market": found[6]}
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


class Corporation:
    def __init__(self, ident):

        if isinstance(ident, int):
            ident = str(ident)
        elif isinstance(ident, str):
            ident = ident.upper()
        else:
            raise MalformedCorpIdentifierError(ident)

        if Market.is_stock_number(ident):
            ret = Market.find_stock_number(ident)
        elif Market.is_ticker(ident):
            ret = Market.find_ticker(ident)
        else:
            raise MalformedCorpIdentifierError(ident)

        self.stock_number = ret["stock_number"]
        self.ticker = ret["ticker"]
        self.name = ret["name"]
        self.sector = ret["sector"]
        self.market =  ret["market"]

        self._income_stmt_url = url.fin_url(
            self.stock_number, FinDataType.INCOME_STATEMENT.value
        )

    @property
    def income_statement(self):
        inc_stmt_id = f"{self.ticker}_income_stmt"

        cache_result = Market.cache.get_resource(inc_stmt_id)
        if cache_result:
            return cache_result

        session = requests.session()
        session.cookies.set(name="bk_lang", value="rK1YIM29JoA=")
        res = session.get(self._income_stmt_url)

        soup = BeautifulSoup(res.content, features="html.parser")
        rows_html = soup.find_all("tr")
        rows_html = [[elm.string for elm in row.children] for row in rows_html]

        income_stmt_table = {
            "header": rows_html[0][1:],
            "body": {
                (row[0].strip() if row[0] else row[0]): row[1:] for row in rows_html[1:]
            },
        }

        Market.cache.append_resource(inc_stmt_id, income_stmt_table)

        return income_stmt_table
