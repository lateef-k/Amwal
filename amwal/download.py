import requests
from enum import Enum

# import aiohttp
# import asyncio
from amwal import url
from amwal.log import logger


class FinDataType(Enum):
    INCOME_STATEMENT = "income-statement"
    BALANCE_SHEET = "balance-sheet"
    CASH_FLOW_STATEMENT = "cash-flow-statement"


LANG_COOKIE = {"bk_lang": "rK1YIM29JoA="}
JSON_HEADER = {"Content-Type": "application/json; charset=utf-8"}


class SyncDownloader:
    @staticmethod
    def daily_bulletin(date):
        logger.info(f"Scraping daily bulletin on {date}")
        res = requests.post(
            url.bulletin, headers=JSON_HEADER, cookies=LANG_COOKIE, json={"d": date}
        )
        return res.content

    @staticmethod
    def listing():
        logger.info(f"Scraping the listed companies page")
        res = requests.post(
            url.listing,
        )
        return res.content

    @staticmethod
    def income_statement(stock_number):
        logger.info(f"Scraping the income statement of {stock_number}")
        res = requests.get(
            url.findata(stock_number, FinDataType.INCOME_STATEMENT.value),
            cookies=LANG_COOKIE,
        )
        return res.content

    @staticmethod
    def price_history(ticker):
        logger.info(f"Scraping the profile of {ticker}")
        res = requests.get(url.price_history(ticker),headers={'content-type':'application/json'})
        return res.content


# class AsyncDownloader:
#    @staticmethod
#    async def daily_bulletin(date):
#        async with aiohttp.ClientSession(headers=JSON_HEADER, cookies=LANG_COOKIE) as session:
#            async with session.post(url.bulletin, json={"d": date}) as response:
#                return await response.read()
#
#    @staticmethod
#    async def listing():
#        async with aiohttp.ClientSession(headers=JSON_HEADER, cookies=LANG_COOKIE) as session:
#            async with session.post(url.listing, json={"cat": "listed", "instrument": ""}) as response:
#                return await response.read()
#
#    @staticmethod
#    async def income_statement(stock_number):
#        async with aiohttp.ClientSession(cookies=LANG_COOKIE) as session:
#            async with session.post(url.findata(stock_number, FinDataType.INCOME_STATEMENT.value)) as response:
#                return await response.read()
#
#    @staticmethod
#    async def profile(stock_number):
#        async with aiohttp.ClientSession(cookies=LANG_COOKIE) as session:
#            async with session.post(url.profile(stock_number)) as response:
#                return await response.read()
