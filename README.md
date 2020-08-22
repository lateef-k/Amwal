## Amwal - Unofficial API For the Kuwaiti Stock Market (Boursa)

Amwal is a small python library designed to make it easier to get information from the Kuwaiti stock market, known as the Boursa. Unfortunately, since the Boursa website doesn't have an official HTTP API, this is a substitute that offers the same function by scraping the website directly for the data. 

Some features to make life easier 

- Scraped data is cached in a JSON file by default to avoid making redundant requests
- The data is converted into a properly typed pandas dataframe. 
- The API surface is small, intuitive, easy to use. It also mirrors the structure of the website itself.

## Installation

```
pip install amwal
```

This project depends on the following libraries:
- python-dateutil
- pandas
- requests
- beautifulsoup4


## Quick start

The main class representing the market as a whole is `amwal.Market`. For example, to get the companies listed on the Boursa:

```python
from amwal import Market

market = Market()
listing = market.listing()
```

The `listing` object is a pandas dataframe mirroring the [listing page](https://www.boursakuwait.com.kw/market-participants/listed-companies) of the Boursa website.

To get the daily price bulletin for 05/05/2020 (day/month/year):

```python 
from amwal import Market

market = Market()
bulletin = market.daily_bulletin("05/05/2020")
```


To get information on a specific company, we first get an object representing the company. The `Market` object has a method called `get_corporation`. It takes a valid ticker or stock number and returns a `Corporation` object. For example, to get zain's price history

```python
from amwal import Market
market = Market()
zain = market.get_corporation("zain")
```
we can now get information about Zain by calling the methods of the `zain` object. To get the price history, for example:

```python
price_history = zain.price_history()
```
This will return a dataframe containing price points streching back until 2004. To get Zain's yearly income statement, we call the `yearly_income` method:
```python
yearly_income = zain.yearly_income()
```
It's pretty straightforward

## Notes

#### Cache

You may have noticed that an *amwal_cache* folder has been created in the path where the python interpreter was started. By default, data that is scraped is cached in the folder as JSON files.

You can change the name of the folder that Amwal uses to cache or retrieve results by supplying a `cache_path` argument to the `Market` constructor:

```python
market = Market(cache_path="another_cache")
```
You can also turn off the cache globally by doing the following

```python
from amwal.cache import JsonCache
JsonCache.enabled = False
```

Or for a single function call by passing the `recompute=True` argument
```python
zain = zain.price_history(recompute=True)
```

#### Be considerate

Don't DDOS the Boursa website with a million requests. Keep the cache enabled instead of repeatedly asking for the same resource. Limit your requests.

#### Pandas

Pandas has many useful functions to serialize dataframes, or to convert from a dataframe into other representations. So if you want to save the data as a CSV or a JSON or convert into a numpy array, there are ways to do that, refer to the Pandas documentation.

#### Log

You can get some output by passing a `verbose=True` argument to the scraping functions.

## API 

```python
class Market(cache_path='amwal_cache', downloader=SyncDownloader) -> Market

  def daily_bulletin(self, date: str, verbose: bool = False, recompute: bool = False) ‑> pandas.core.frame.DataFrame 
  #date should be a string formatted as dd/mm/yyyyy

  def listing(self, verbose: bool = False, recompute: bool = False) ‑> pandas.core.frame.DataFrame 

  @staticmethod
  def is_stock_number(ident: str) ‑> bool 

  @staticmethod
  def is_ticker(ident: str) ‑> bool

  def get_corporation(self, ident: str, verbose: bool = False) ‑> Corporation 

class Corporation (ident: str, market: Market, **kwargs)  
#You should not call this constructor directly, use get_corporation instead.

  def price_history(self, verbose: bool = False, recompute: bool = False) ‑> pandas.core.frame.DataFrame 

  def quarterly_income(self, verbose: bool = False, recompute: bool = False) ‑> pandas.core.frame.DataFrame 

  def yearly_income(self, verbose: bool = False, recompute: bool = False) ‑> pandas.core.frame.DataFrame 
```

---

### TODO:

- Add balance sheet and cash flow statement methods to the corporation class.
- Change scraping to be asynchronous. 



