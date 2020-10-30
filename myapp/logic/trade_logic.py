from myapp import stock_api
from myapp import models

def parse_input(params):
    try:
        number_of_stocks = int(params["number_of_stocks"])
        if number_of_stocks <= 0:
            raise Exception
        stock_info = stock_api.get_stock_info(params["stock_selector"])
        stock_price = float(stock_info['latestPrice'])
        total_price = stock_price * number_of_stocks
        stock_info.update({'number_of_stocks': number_of_stocks,
                           'total_price': total_price})
        return stock_info
    except Exception:
        return None

def create_transaction(user, stock_info):
    t = models.Transaction.objects.create(user=user,
                                          stock_symbol=stock_info['symbol'],
                                          quantity=stock_info['number_of_stocks'],
                                          price=stock_info['total_price'])
    t.save()

def create_profile(user):
    profile = models.UserProfile.objects.create(user=user, balance=5000)
    profile.save()

def get_number_of_stocks(user,stock_symbol):
    transactions = models.Transaction.objects.filter(user=user,stock_symbol=stock_symbol)
    total_number_of_stocks = 0
    for transaction in transactions:
        total_number_of_stocks += transaction.quantity
    return total_number_of_stocks
