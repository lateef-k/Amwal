bulletin = "https://www.boursakuwait.com.kw/markets/bulletin_data/daily_bulletin/company_statistics.aspx/getData"
finlan = "https://www.boursakuwait.com.kw/markets/financial_data/companies.aspx/getData"
listing = (
    "https://www.boursakuwait.com.kw/market_participants/listed_companies.aspx/getData"
)


def findata(stock_number, findata_kind):
    return f"https://www.boursakuwait.com.kw/stock/{stock_number}/financial-data/{findata_kind}"


def profile(stock_number):
    return f"https://www.boursakuwait.com.kw/stock/{stock_number}/profile"
