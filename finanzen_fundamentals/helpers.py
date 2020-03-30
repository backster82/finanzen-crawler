import time

import pandas
import requests
from lxml import html


def check_site_availability(url):
    try:
        r = requests.get(url)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)


def get_parser(function, stock_name):
    base_url = "https://www.finanzen.net"

    functions = {
        "search": "/suchergebnis.asp?_search=",
        "stock": "/aktien/",
        "estimates": "/schaetzungen/",
        "fundamentals": "/bilanz_guv/",
        "index": "/index/"
    }

    if function not in functions:
        raise ValueError("Got unknown function %r in get_parser" % function)
        return 1

    check_site_availability(base_url)

    url = base_url + functions[function] + stock_name
    response = requests.get(url, verify=True)

    parser = html.fromstring(response.text)

    return parser


def get_parser_paginated(function, stock_name):
    base_url = "https://www.finanzen.net"
    parser_array = []

    functions = {
        "search": "/suchergebnis.asp?_search=" + stock_name,
        "stock": "/aktien/" + stock_name,
        "estimates": "/schaetzungen/" + stock_name,
        "fundamentals": "/bilanz_guv/" + stock_name,
        "index": "/index/" + stock_name + "/werte"
    }

    if function not in functions:
        raise ValueError("Got unknown function %r in get_parser" % function)
        return 1

    check_site_availability(base_url)

    url = base_url + functions[function]
    response = requests.get(url, verify=True)

    parser = html.fromstring(response.text)

    pages = parser.xpath('//div[contains(@class, "finando_paging")]//a//text()')

    if pages == []:
        pages = ['1']

    print("Pages: %r" % pages)

    if len(pages) > 0:
        for i in range(len(pages)):
            time.sleep(2)
            url = base_url + functions[function] + "?p=%s" % str(i+1)
            response = requests.get(url, verify=True)

            parser = html.fromstring(response.text)
            parser_array.append(parser)

    return parser_array


def search_stock(stock: str, limit: int = -1):
    indices = ["name", "fn_stock_name", "isin", "wkn"]
    df = pandas.DataFrame(columns=indices)

    parser = get_parser("search", stock)

    table_xpath = '//div[contains(@class, "table")]//tr'
    summary_table = parser.xpath(table_xpath)

    if len(summary_table) == 0:
        raise ValueError("Site did find any entries for %r" % stock)

    skip_first_element = 0
    results = []

    for table_element in summary_table:
        # Todo: Find cause for the first element being [] []
        if skip_first_element == 0:
            skip_first_element = 1
        else:
            raw_name = ''.join(table_element.xpath('.//a/text()')).strip()
            raw_link = ''.join(table_element.xpath('.//a//@href')).strip()
            raw_isin = ''.join(table_element.xpath('.//td')[1].xpath('./text()')).strip()
            raw_wkn = ''.join(table_element.xpath('.//td')[2].xpath('./text()')).strip()

            fn_stock_name = raw_link.replace("/aktien/", "").replace("-aktie", "")

            if limit == 0:
                break
            elif limit > 0:
                limit -= 1

            df = df.append(pandas.DataFrame(data=[[raw_name, fn_stock_name, raw_isin, raw_wkn]], columns=indices))
    return df
