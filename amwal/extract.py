import json
import pandas as pd
from functools import partial
from datetime import datetime
from bs4 import BeautifulSoup


to_datetime = partial(pd.to_datetime, format="%d-%m-%Y")


def to_price(price): return price/10


def identity(i):
    return i


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
        ("date", to_datetime),
        ("stock", identity),
        ("ticker", identity),
        ("previous_close", to_numeric_float),
        ("opening_price", to_numeric_float),
        ("high", to_numeric_float),
        ("low", to_numeric_float),
        ("close", to_numeric_float),
        ("change_to_previous_close", to_numeric_float),
        ("change_to_previous_close_percent", to_numeric_float),
        ("remaining_best_bid_price", to_numeric_float),
        ("remaining_best_bid_volume", to_numeric_int),
        ("remaining_best_ask_price", to_numeric_float),
        ("remaining_best_ask_volume", to_numeric_int),
        ("vwap", to_numeric_float),
        ("volume", to_numeric_int),
        ("total_trades", to_numeric_int),
        ("value", to_numeric_float),
        ("previous_trade_date", to_datetime),
        ("market_segment", to_categorical),
    ],
    "listing": [
        # NOTE: stock_index used to be sec_code
        ("Stock Index", identity),
        ("Name", identity),
        ("Ticker", identity),
        ("Sector", to_categorical),
        ("Market Segment", to_categorical),
    ],
    "price_history": [
        ("Date", pd.to_datetime),
        ("Open", to_numeric_float),
        ("High", to_numeric_float),
        ("Low", to_numeric_float),
        ("Close", to_numeric_float),
        ("Volume", to_numeric_int),
        ("Total Value Traded", to_numeric_float),
        # ("ID", to_numeric_int) #don't see a use for this now
    ]
}


class RawExtractor:
    @staticmethod
    def price_history(doc):
        loaded = json.loads(doc)
        price_history = loaded["DAT"]["HIS"]
        price_history = [
            (datetime.fromtimestamp(row[0]
                                    ).strftime("%d-%m-%Y"), *row[1:])
            for row in price_history
        ]
        return price_history

    @staticmethod
    def daily_bulletin(doc):
        return RawExtractor.process_json(doc)

    @staticmethod
    def listing(doc):
        data = json.loads(doc)['DAT']

        listing_data = data['TD']
        listing_data = [d.split("|") for d in listing_data]
        listing_data = list(
            filter(lambda row: row[1].split("`")[1] == "R", listing_data))

        sectors = data['ID']
        sectors = [string.split("|") for string in sectors]
        sectors = {dat[1]: dat[4] for dat in sectors}

        def simplify(raw):
            return [raw[12],
                    raw[3],
                    raw[19],
                    sectors[raw[4]],
                    {"P": "Premier Market", "M": "Main Market"}[raw[8]]
                    ]
            return

        return list(map(simplify, listing_data))

    @staticmethod
    def income_statement(doc):
        soup = BeautifulSoup(doc, features="html.parser")
        rows_html = soup.find_all("tr")
        rows_html = [[str(elm.string) for elm in row.children]
                     for row in rows_html]

        yearly_header = []
        yearly_html = []
        quarterly_header = []
        quarterly_html = []

        # This deletes the 4 quarter data. should store it somehow later
        for i in range(len(rows_html)):
            if len(rows_html[i]) == 5:
                yearly_header = rows_html[0][1:]
                yearly_html = rows_html[1:i]
                quarterly_header = rows_html[i][1:]
                quarterly_html = rows_html[i + 1:]
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


def rows_to_df(datasource, doc):
    return pd.DataFrame(
        {
            HEADERS[datasource][j][0]: HEADERS[datasource][j][1](
                pd.Series([doc[i][j] for i in range(len(doc))])
            )
            for j in range(len(HEADERS[datasource]))
        }
    )


class DataFrameExtractor:
    @staticmethod
    def price_history(doc):
        return rows_to_df("price_history", doc)

    @staticmethod
    def daily_bulletin(doc):
        return rows_to_df("daily_bulletin", doc)

    @staticmethod
    def listing(doc):
        return rows_to_df("listing",doc)

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
            df = pd.DataFrame(doc["yearly"]["body"],
                              index=doc["yearly"]["header"])
            return df
        else:
            return None
