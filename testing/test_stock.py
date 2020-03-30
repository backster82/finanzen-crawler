import finanzen_fundamentals

stock = finanzen_fundamentals.stock.Stock("deutsche_telekom")
print(stock.get_fundamentals())

for col in stock.get_fundamentals().columns:
    print(col)
