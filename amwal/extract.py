import json
from bs4 import BeautifulSoup
import pandas as pd

from functools import partial

identity = lambda i: i
to_datetime = partial(pd.to_datetime, format="%d/%m/%Y")


def to_numeric_float(series):
    try:
        if not series.empty:
            return series.str.replace(",", "").astype("float64")
        else:
            return series
    except:
        return series


def to_numeric_int(series):
    try:
        if not series.empty:
            return series.str.replace(",", "").astype("int64")
        else:
            return series
    except:
        return series


def to_categorical(series):
    return pd.Categorical(series)


def to_boolean(series):
    return series.astype("bool")


def float_or_nan(num):
    try:
        return float(num)
    except:
        return None


HEADERS = {
    "daily_bulletin": [
        ("Date", to_datetime),
        ("Stock", identity),
        ("Ticker", identity),
        ("Previous Close", to_numeric_float),
        ("Opening Price", to_numeric_float),
        ("High", to_numeric_float),
        ("Low", to_numeric_float),
        ("Close", to_numeric_float),
        ("Change to Previous Close", to_numeric_float),
        ("Change to Previous Close %", to_numeric_float),
        ("Remaining Best Bid Price", to_numeric_float),
        ("Remaining Best Bid Volume", to_numeric_int),
        ("Remaining Best Ask Price", to_numeric_float),
        ("Remaining Best Ask Volume", to_numeric_int),
        ("VWAP", to_numeric_float),
        ("Volume", to_numeric_int),
        ("Total Trades", to_numeric_int),
        ("Value", to_numeric_float),
        ("Previous Trade Date", to_datetime),
        ("Market Segment", to_categorical),
    ],
    "listing": [
        ("Sec. Code", identity),
        ("Ticker", identity),
        ("Warning", to_categorical),
        ("Name", identity),
        ("Short Selling", identity),
        ("Sector", to_categorical),
        ("Market Segment", to_categorical),
    ],
}


class RawExtractor:
    @staticmethod
    def daily_bulletin(doc):
        return RawExtractor.process_json(doc)

    @staticmethod
    def listing(doc):
        processed_listing = RawExtractor.process_json(doc)
        for row in processed_listing:
            del row[0]
            row[3] = BeautifulSoup(row[3], features="html.parser").text
            if "#eed122" in row[2]:
                row[2] = "RED"
            elif "#FF0000" in row[2]:
                row[2] = "YELLOW"
        return processed_listing

    @staticmethod
    def income_statement(doc):
        soup = BeautifulSoup(doc, features="html.parser")
        rows_html = soup.find_all("tr")
        rows_html = [[elm.string for elm in row.children] for row in rows_html]

        yearly_header = []
        yearly_html = []
        quarterly_header = []
        quarterly_html = []

        # This deletes the 4 quarter data. should store it somehow later
        for i in range(len(rows_html)):
            if len(rows_html[i]) < 11:
                yearly_header = rows_html[0][1:]
                yearly_html = rows_html[1:i]
                quarterly_header = rows_html[i][1:]
                quarterly_html = rows_html[i + 1 :]
                break

        income_stmt_table = {
            "yearly": {
                "header": yearly_header,
                "body": {
                    (row[0].strip() if row[0] else row[0]): [
                        float_or_nan(col.replace(",", "")) for col in row[1:]
                    ]
                    for row in yearly_html
                },
            },
            "quarterly": {
                "header": quarterly_header,
                "body": {
                    (row[0].strip() if row[0] else row[0]): [
                        float_or_nan(col.replace(",", "")) for col in row[1:]
                    ]
                    for row in quarterly_html
                },
            },
        }
        return income_stmt_table

    @staticmethod
    def process_json(raw):
        raw = json.loads(raw)["d"]
        raw = json.loads(raw)["aaData"]
        return raw


class DataFrameExtractor:
    @staticmethod
    def daily_bulletin(doc):
        df = pd.DataFrame(
            {
                HEADERS["daily_bulletin"][j][0]: HEADERS["daily_bulletin"][j][1](
                    pd.Series([doc[i][j] for i in range(len(doc))])
                )
                for j in range(len(HEADERS["daily_bulletin"]))
            }
        )
        return df

    @staticmethod
    def listing(doc):
        df = pd.DataFrame(
            {
                HEADERS["listing"][j][0]: HEADERS["listing"][j][1](
                    pd.Series([doc[i][j] for i in range(len(doc))])
                )
                for j in range(len(HEADERS["listing"]))
            }
        )
        return df

    @staticmethod
    def yearly_income(doc):
        if "yearly" in doc and "body" in doc["yearly"] and doc["yearly"]["body"]:
            df = pd.DataFrame(
                doc["yearly"]["body"],
                index=[int(year) for year in doc["yearly"]["header"]],
            )
            return df
        else:
            return None

    @staticmethod
    def quarterly_income(doc):
        if (
            "quarterly" in doc
            and "body" in doc["quarterly"]
            and doc["quarterly"]["body"]
        ):
            df = pd.DataFrame(doc["yearly"]["body"], index=doc["yearly"]["header"])
            return df
        else:
            return None
