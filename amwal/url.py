bulletin = "https://www.boursakuwait.com.kw/markets/bulletin_data/daily_bulletin/company_statistics.aspx/getData"
finlan = "https://www.boursakuwait.com.kw/markets/financial_data/companies.aspx/getData"
listing = (
    "https://www.boursakuwait.com.kw/data-api/legacy-mix-services?UID=3166765&SID=3090B191-7C82-49EE-AC52-706F081F265D&L=EN&UNC=0&UE=KSE&H=1&M=1&RT=303&SRC=KSE&AS=1"
)


def findata(stock_number, findata_kind):
    return f"https://www.boursakuwait.com.kw/en/stock/financial-data/{findata_kind}#{stock_number}"


def price_history(ticker):
    return f"https://www.boursakuwait.com.kw/chart?UID=&SID=0L=EN&UNC=1&UE=KSE&H=1&M=1&RT=37&E=KSE&S={ticker}%60R&AE=1&CM=3&CT=3&SD=20010121000000&ED=20210121000000"


