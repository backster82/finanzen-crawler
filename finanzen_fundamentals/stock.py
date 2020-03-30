import time

import numpy as np
import pandas as pd
import requests
from lxml import html

from . import helpers
from . import statics


class Stock:
    def __init__(self, fn_stock_name: str, exchange: str = "TGT"):
        self.stock_name = fn_stock_name
        self.quotes = pd.DataFrame()
        self.fundamentals = pd.DataFrame()
        self.estimates = pd.DataFrame()
        self.exchange = exchange

        if self.check_stock_uniqueness():
            print("Found stock %r" % self.stock_name)
        else:
            print("Could not find page for %r" % self.stock_name)
            return 1

        self.update_quotes()
        time.sleep(1)
        self.update_fundamentals()
        time.sleep(1)
        self.update_estimates()

    def __str__(self):
        pass

    def check_stock_uniqueness(self):
        parser = helpers.get_parser(function="stock", stock_name=self.stock_name)

        stock_lookup = parser.xpath('//div[contains(@class, "special_info_box")]/text()')

        if len(stock_lookup) > 0:
            return False
        else:
            return True

    def update_quotes(self):
        data_columns = [
            "name",
            "wkn",
            "isin",
            "symbol",
            "price",
            "currency",
            "chg_to_open",
            "chg_percent",
            "time",
            "exchange"
        ]

        url = "https://www.finanzen.net/aktien/" + self.stock_name + "-aktie" + statics.StockMarkets[self.exchange][
            'url_postfix']
        response = requests.get(url, verify=True)

        # sleep()
        parser = html.fromstring(response.text)
        summary_table = parser.xpath('//div[contains(@class,"row quotebox")][1]')

        i = 0

        summary_data = []

        for table_data in summary_table:
            raw_price = table_data.xpath(
                '//div[contains(@class,"row quotebox")][1]/div[contains(@class, "col-xs-5")]/text()')
            raw_currency = table_data.xpath(
                '//div[contains(@class,"row quotebox")][1]/div[contains(@class, "col-xs-5")]/span//text()')
            raw_change = table_data.xpath(
                '//div[contains(@class,"row quotebox")][1]/div[contains(@class, "col-xs-4")]/text()')
            raw_percentage = table_data.xpath(
                '//div[contains(@class,"row quotebox")][1]/div[contains(@class, "col-xs-3")]/text()')
            raw_name = table_data.xpath('//div[contains(@class, "col-sm-5")]//h1/text()')
            raw_instrument_id = table_data.xpath('//span[contains(@class, "instrument-id")]/text()')
            raw_time = table_data.xpath('//div[contains(@class,"row quotebox")]/div[4]/div[1]/text()')
            raw_exchange = table_data.xpath('//div[contains(@class,"row quotebox")]/div[4]/div[2]/text()')

            name = ''.join(raw_name).strip()
            time = ''.join(raw_time).strip()
            exchange = ''.join(raw_exchange).strip()

            instrument_id = ''.join(raw_instrument_id).strip()
            (wkn, isin) = instrument_id.split(sep='/')
            if 'Symbol' in isin:
                (isin, sym) = isin.split(sep='Symbol')
            else:
                sym = ""

            currency = ''.join(raw_currency).strip()

            summary_data = [
                name.replace('&nbsp', ''),
                wkn.replace(' ', '').replace("WKN:", ""),
                isin.replace(' ', '').replace("ISIN:", ""),
                sym.replace(' ', '').replace(":", ""),
                float(raw_price[0].replace(',', '.')),
                currency,
                float(raw_change[0].replace(',', '.')),
                float(raw_percentage[0].replace(',', '.')),
                time,
                statics.StockMarkets[exchange]['real_name']
            ]

        self.value = pd.DataFrame(data=[summary_data], columns=data_columns)

    def update_estimates(self):
        url = "https://www.finanzen.net/schaetzungen/" + self.stock_name

        xp_base_xpath = '//div[contains(@class, "box table-quotes")]//h1[contains(text(), "Schätzungen")]//..'
        xp_data = xp_base_xpath + '//table//tr'

        response = requests.get(url, verify=True)
        parser = html.fromstring(response.text)

        data_table = []

        header_row = 0

        for data_element in parser.xpath(xp_data):
            table_row = []
            for i in data_element:
                table_row.append(i.xpath('./text()')[0])

            if header_row != 0:
                for i in range(1, len(table_row)):
                    if not table_row[i] == '-':
                        table_row[i] = table_row[i].replace(".", "").replace(",", ".")
                        table_row[i] = float(table_row[i].split(" ")[0])

            else:
                table_row[0] = "Estimation"
                header_row = 1

            data_table.append(table_row)
            dataframe = pd.DataFrame(list(map(np.ravel, data_table)))
            dataframe.columns = dataframe.iloc[0]
            dataframe.drop(dataframe.index[0], inplace=True)

        self.estimates = dataframe

    def update_fundamentals(self):
        url = "https://www.finanzen.net/bilanz_guv/" + self.stock_name

        tables = ["Die Aktie",
                  "Unternehmenskennzahlen",
                  "GuV",
                  "Bilanz",
                  "sonstige Angaben"
                  ]

        complete_data_set = []

        for table in tables:
            parser = helpers.get_parser("fundamentals", self.stock_name)

            xp_base = '//div[contains(@class, "box table-quotes")]//h2[contains(text(), "' + table + '")]//..'
            xp_head = xp_base + '//table//thead//tr'
            xp_data = xp_base + '//table//tbody'

            parsed_data_table = parser.xpath(xp_base)

            # drop second empty element in parsed_data_table
            # ToDo: find out why parser.xpath(xp_base) returns 2 elements
            # parsed_data_table.pop()

            for data_element in parsed_data_table:
                header_array = []
                table_data = []
                for i in data_element.xpath('.//table//thead//tr//th/text()'):
                    header_array.append(i)

                table_data.append(header_array)

                # first table element is an checkbox so we'll drop it
                first_col = True
                for i in data_element.xpath('.//table//tr'):
                    if not first_col:
                        data = i.xpath('.//td/text()')
                        for cnt in range(1, len(data)):
                            data[cnt] = data[cnt].replace(".", "").replace(",", ".")
                        table_data.append(data)
                    else:
                        first_col = False

                dataframe = pd.DataFrame(list(map(np.ravel, table_data)))
                dataframe.columns = dataframe.iloc[0]
                dataframe.drop(dataframe.index[0], inplace=True)

                complete_data_set.append(dataframe)

        self.fundamentals = pd.concat(complete_data_set, ignore_index=True)

    def get_quotes(self):
        return self.value

    def get_fundamentals(self):
        return self.fundamentals

    def get_estimates(self):
        return self.estimates
