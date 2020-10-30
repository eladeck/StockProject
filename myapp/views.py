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
from myapp.logic import trade_logic


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
    stock_list = stock_api.get_all_stocks()
    content = {'stock_list': stock_list}
    rendered_page = render(request, 'trade.html', content)
    return rendered_page


def compare(request):
    stock_list = stock_api.get_all_stocks()
    data = {'stock_list': stock_list,
            }
    return render(request, 'compare_two_stocks.html', data)


def buy(request):
    content = {}
    stock_list = stock_api.get_all_stocks()
    content.update({'stock_list': stock_list})
    params = request.GET
    user = request.user

    stock_info = trade_logic.parse_input(params)

    if stock_info is None:
        content.update({"error": "Invalid input"})
        return render(request, 'trade.html', content)

    if not models.UserProfile.objects.filter(user=user).exists():
        trade_logic.create_profile(user)

    user_profile = models.UserProfile.objects.get(user=user)

    if stock_info['total_price'] > user_profile.balance:
        content.update({"error": "not enough balance"})
        return render(request, 'trade.html', content)

    user_profile.balance -= stock_info['total_price']
    user_profile.save()

    trade_logic.create_transaction(user, stock_info)

    content.update({'success': f'You have bought {stock_info["number_of_stocks"]} {stock_info["symbol"]} '
                               f'for a price {stock_info["total_price"]}'
                               f'\n your current balance is: {user_profile.balance}'})

    return render(request,'trade.html',content)


def sell(request):
    content = {}
    stock_list = stock_api.get_all_stocks()
    content.update({'stock_list': stock_list})
    params = request.GET
    user = request.user

    stock_info = trade_logic.parse_input(params)

    if stock_info is None:
        content.update({"error": "Invalid input"})
        return render(request, 'trade.html', content)

    if not models.UserProfile.objects.filter(user=user).exists():
        trade_logic.create_profile(user)

    user_profile = models.UserProfile.objects.get(user=user)

    available_stocks = trade_logic.get_number_of_stocks(user, stock_info['symbol'])
    if available_stocks < stock_info['number_of_stocks']:
        content.update({"error": "Not enough stocks to sell"})
        return render(request, 'trade.html', content)

    user_profile.balance += stock_info['total_price']
    user_profile.save()

    stock_info['number_of_stocks'] *= -1
    trade_logic.create_transaction(user, stock_info)

    content.update({'success': f'You have sold {abs(stock_info["number_of_stocks"])} {stock_info["symbol"]} '
                               f'for a price {stock_info["total_price"]}'
                               f'\n your current balance is: {user_profile.balance}'})



    return render(request, 'trade.html', content)
