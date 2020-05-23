import json
from bs4 import BeautifulSoup


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

        income_stmt_table = {
            "header": rows_html[0][1:],
            "body": {
                (row[0].strip() if row[0] else row[0]): row[1:] for row in rows_html[1:]
            },
        }
        return income_stmt_table

    @staticmethod
    def process_json(raw):
        raw = json.loads(raw)["d"]
        raw = json.loads(raw)["aaData"]
        return raw
