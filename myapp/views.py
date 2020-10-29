import requests
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from myapp import stock_api
from myapp.models import Stock
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import logout
from . import stock_api, models
from datetime import datetime


# View for the home page - a list of 20 of the most active stocks
def index(request):
    # Query the stock table, filter for top ranked stocks and order by their rank.
    data = Stock.objects.filter(top_rank__isnull=False).order_by('top_rank')
    return render(request, 'index.html', {'page_title': 'Main', 'data': data})


# View for the single stock page
# symbol is the requested stock's symbol ('AAPL' for Apple)
def single_stock(request, symbol):
    data = stock_api.get_stock_info(symbol)
    return render(request, 'single_stock.html', {'page_title': 'Stock Page - %s' % symbol, 'data': data})


def register(request):
    # If post -> register the user and redirect to main page
    if request.method == 'POST':
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        email = request.POST.get('email')
        password = request.POST.get('password')

        newuser = User.objects.create_user(username=email, email=email, password=password)
        newuser.first_name = firstname
        newuser.last_name = lastname
        newuser.save()

        user_profile = models.UserProfile.objects.create(user=newuser, balance=5000)
        user_profile.save()

        return redirect('index')
    else:
        # If not post (regular request) -> render register page
        return render(request, 'register.html', {'page_title': 'Register'})


def logout_view(request):
    logout(request)
    return redirect('index')


# API for a stock's price over time
# symbol is the requested stock's symbol ('AAPL' for Apple)
# The response is JSON data of an array composed of "snapshot" objects (date + stock info + ...), usually one per day
def single_stock_historic(request, symbol):
    data = stock_api.get_stock_historic_prices(symbol, time_range='1m')
    return JsonResponse({'data': data})


@login_required
def trade(request):
    content = {'user': request.user}
    stock_list = stock_api.get_all_stocks()
    content.update({'stock_list': stock_list})

    params = request.GET
    user = request.user
    if "buy" in params or "sell" in params:
        user_profile = models.UserProfile.objects.get(user=user)
        if user.is_authenticated:

            try:
                print(int(params['number_of_stocks']))
                print(int(params['number_of_stocks'][0]))
                number_of_stocks = int(params["number_of_stocks"][0])
                if number_of_stocks <= 0:
                    raise Exception
                stock_info = stock_api.get_stock_info(params["stock_selector"])
                stock_price = float(stock_info['latestPrice'])
            except Exception:
                content.update({"error": "Error in input data"})
                return render(request, 'trade.html', content)

            stock_symbol = stock_info["symbol"]
            price = stock_price * number_of_stocks
            if 'buy' in params:
                if user_profile.balance >= stock_price * number_of_stocks:
                    t = models.Transaction.objects.create(user_id=models.UserProfile.objects.get(user=request.user),
                                                          stock_symbol=stock_symbol,
                                                          trans_date=datetime.now(),
                                                          buy_or_sell=0,
                                                          quantity=number_of_stocks,
                                                          price=price)
                    t.save()
                    user_profile.balance -= price
                    if stock_symbol in user_profile.stocks:
                        user_profile.stocks[stock_symbol] += number_of_stocks
                    else:
                        user_profile.stocks[stock_symbol] = number_of_stocks
                    user_profile.save()
                    content.update({'success': f'You have bought {number_of_stocks} {stock_symbol} for a price {price}'
                                               f'\n your current balance is: {user_profile.balance}'})

                else:
                    content.update({"error": "not enough balance"})
                    return render(request, 'trade.html', content)

            elif 'sell' in params:
                available_stocks = models.UserProfile.objects.get(user=request.user).stocks[stock_symbol]
                if available_stocks >= number_of_stocks:
                    t = models.Transaction.objects.create(user_id=models.UserProfile.objects.get(user=request.user),
                                                          stock_symbol=stock_symbol,
                                                          trans_date=datetime.now(),
                                                          buy_or_sell=1,
                                                          quantity=number_of_stocks,
                                                          price=price)
                    t.save()

                    user_profile.stocks[stock_symbol] -= number_of_stocks

                    user_profile.save()

                    content.update({'success': f'You have sold {number_of_stocks} for a price {price}'
                                               f'\n your current balance is: {user_profile.balance}'})
                else:
                    content.update({"error": "not enough stocks"})
        else:
            return redirect('login')




    rendered_page = render(request, 'trade.html', content)
    return rendered_page


def compare(request):
    stock_list = stock_api.get_all_stocks()
    data = {'stock_list': stock_list,
            }
    return render(request, 'compare_two_stocks.html', data)
