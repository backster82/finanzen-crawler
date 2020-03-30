# finanzen-crawler-objectified
Finanzen-Fundamentals is a Python package that can be used to retrieve fundamentals of stocks. The data is fetched 
from [finanzen.net](https://www.finanzen.net), a German language financial news site. Note that the api is English 
but all data will be returned in German.

This implementation is derived from Joshuas Hruziks finanzen-fundamentals and implements the functions in an and object oriented way.
 
# Installation
This module can currently not be found on PyPi or any other python repository. 

To use the module check it out into your project. 

`git clone -b objectified https://github.com/backster82/finanzen-crawler.git`

If you choose to download the source code, make sure that you have the following dependencies installed:
* requests
* numpy 
* pandas 
* lxml
* time 

You can install all of them by running: `pip install requests lxml numpy pandas time`.

# Usage
## Import
After you successfully installed the package, you can include it in your projects by importing it.

```import finanzen_fundamentals```

## The stock.Stock \_\_init__ function 

Init expects as first value the stock name as it is used by finanzen.net. German Telekom is for ex. listed as deutsche_telekom
On init fundamentals, estimations and current stock quotes are crawled and stores into object members.

The object can be initialized with an stock market as optional parameter exchange. 
The default is TGT for Tradegate. 
To lookup the values for exchange see statics.py 

So for German Telekom the stock object instantiation on exchange Frankfurt Stock Exchange would look like this: 
```stock = finanzen_fundamentals.stock.Stock("deutsche_telekom", exchange="FSE")```

If your unsure what the correct value for the stock name is, see chapter #Search Stock

## Fundamentals
### Get fundamentals 
You can retrieve the fundamentals from an given stock.Stock object by calling get_fundamentals: 

```fundamentals = stock.get_fundamentals()```

Data will be returned in form of an pandas Dataframe

### Update fundamentals

To update the fundamentals just call the update_fundamentals function.

```stock.update_fundamentals()```

## Estimates
### Get estimates
You can retrieve the estimates from an given stock.Stock object by calling get_estimates: 

```estimates = stock.get_estimates()```

Data will be returned in form of an pandas Dataframe

### Update estimates
To update the estimates just call the update_estimates function.

```stock.update_estimates()```

## Current stock quotes 
### Get current stock quote 
You can retrieve the current quotes from an given stock.Stock object by calling get_quotes: 

```quotes = stock.get_quotes()```

Data will be returned in form of an pandas Dataframe

### Update current stock quotes 
To update the current stock quotes just call the update_quotes function.

```stock.update_quotes()```

## Search Stock
To get the correct name for an stock you can use the search_stock function.

The function accepts the stock as string and an number of results. 
The result number is optional. Search stocks without number of results will return all 
results found. 

ex. ```stock_names = finanzen_net.helpers.search_stock("telekom", 5)``` 

Data will be returned in form of an pandas Dataframe which will have the following columns: 
- name
- fn_stock_name
- isin
- wkn