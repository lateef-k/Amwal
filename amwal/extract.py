import json
from bs4 import BeautifulSoup
import pandas as pd


HEADERS = {
    "daily_bulletin": [
        "Date",
        "Stock",
        "Ticker",
        "Previous Close",
        "Opening Price",
        "High",
        "Low",
        "Close",
        "Change to Previous Close",
        "Change to Previous Close %",
        "Remaining Best Bid Price",
        "Remaining Best Bid Volume",
        "Remaining Best Ask Price",
        "Remaining Best Ask Volume",
        "VWAP",
        "Volume",
        "Total Trades",
        "Value",
        "Previous Trade Date",
        "Market Segment",
    ],
    "listing": [
        "No",
        "Sec. Code",
        "Ticker",
        "Name",
        "Short Selling",
        "Sector",
        "Market Segment",
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
                    (row[0].strip() if row[0] else row[0]): row[1:]
                    for row in yearly_html
                },
            },
            "quarterly": {
                "header": quarterly_header,
                "body": {
                    (row[0].strip() if row[0] else row[0]): row[1:]
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
                HEADERS["daily_bulletin"][j]: [doc[i][j] for i in range(len(doc))]
                for j in range(len(HEADERS["daily_bulletin"]))
            }
        )
        return df

    @staticmethod
    def listing(doc):
        df = pd.DataFrame(
            {
                HEADERS["listing"][j]: [doc[i][j] for i in range(len(doc))]
                for j in range(len(HEADERS["listing"]))
            }
        )
        return df

    @staticmethod
    def yearly_income(doc):
        df = pd.DataFrame(doc["yearly"]["body"], index=doc["yearly"]["header"])
        return df

    @staticmethod
    def quarterly_income(doc):
        df = pd.DataFrame(doc["yearly"]["body"], index=doc["yearly"]["header"])
        return df
