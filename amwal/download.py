import requests
from enum import Enum

from amwal import url
from amwal.log import logger


class FinDataType(Enum):
    INCOME_STATEMENT = "income-statement"
    BALANCE_SHEET = "balance-sheet"
    CASH_FLOW_STATEMENT = "cash-flow-statement"


class SyncDownloader:
    @staticmethod
    def daily_bulletin(date):
        session = requests.session()
        session.cookies.set(name="bk_lang", value="rK1YIM29JoA=")
        session.headers.update({"Content-Type": "application/json; charset=utf-8"})

        logger.info(f"Scraping daily bulletin on {date}")
        res = session.post(url.bulletin, json={"d": date},)
        return res.content

    @staticmethod
    def listing():
        session = requests.session()
        session.cookies.set(name="bk_lang", value="rK1YIM29JoA=")
        session.headers.update({"Content-Type": "application/json; charset=utf-8"})
        logger.info(f"Scraping the listed companies page")
        res = session.post(url.listing, json={"cat": "listed", "instrument": ""})
        return res.content

    @staticmethod
    def income_statement(stock_number):
        session = requests.session()
        session.cookies.set(name="bk_lang", value="rK1YIM29JoA=")
        logger.info(f"Scraping the income statement of {stock_number}")
        res = session.get(url.findata(stock_number, FinDataType.INCOME_STATEMENT.value))
        return res.content

    @staticmethod
    def profile(stock_number):
        session = requests.session()
        session.cookies.set(name="bk_lang", value="rK1YIM29JoA=")
        logger.info(f"Scraping the profile of {stock_number}")
        res = session.get(url.profile(stock_number))
        return res.content
