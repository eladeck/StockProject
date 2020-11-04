from myapp import stock_api
from myapp import models
from myapp.exceptions import trade_excpetions, custom_exception


def get_stock_price(stock_symbol):

    stock_info = stock_api.get_stock_info(stock_symbol)
    stock_price = float(stock_info['latestPrice'])
    return stock_price



def create_transaction(user, stock_symbol, number_of_stocks, price):
    t = models.Transaction.objects.create(user=user,
                                          stock_symbol=stock_symbol,
                                          quantity=number_of_stocks,
                                          price=price)
    t.save()


def get_number_of_stocks(user, stock_symbol):
    transactions = models.Transaction.objects.filter(user=user, stock_symbol=stock_symbol)
    total_number_of_stocks = 0
    for transaction in transactions:
        total_number_of_stocks += transaction.quantity
    return total_number_of_stocks
