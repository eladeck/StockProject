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
from myapp.logic import trade_logic, register_logic
from django.views.decorators.csrf import csrf_exempt
from myapp.exceptions import custom_exception,trade_excpetions


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

        register_logic.create_profile(newuser)

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


def compare(request):
    stock_list = stock_api.get_all_stocks()
    data = {'stock_list': stock_list,
            }
    return render(request, 'compare_two_stocks.html', data)


@login_required
@csrf_exempt
def trade(request):
    stock_list = stock_api.get_all_stocks()
    context = {'stock_list': stock_list}
    try:
        if request.method == 'POST':
            params = request.POST
            stock_symbol = params["stock_selector"]
            number_of_stocks = int(params["number_of_stocks"])
            if number_of_stocks <= 0:
                raise trade_excpetions.InvalidNumberOfStocksExceptions("Invalid number")

            stock_price = trade_logic.get_stock_price(stock_symbol)

            user_profile = models.UserProfile.objects.get(user=request.user)
            total_price = stock_price * number_of_stocks

            if 'sell' in params:
                available_stocks = trade_logic.get_number_of_stocks(request.user, stock_symbol)
                if available_stocks < number_of_stocks:
                    raise trade_excpetions.NotEnoughStocksException("Not enough stocks to sell")

                number_of_stocks *= -1
                trade_logic.create_transaction(request.user, stock_symbol, number_of_stocks, stock_price)

                user_profile.balance += total_price
                user_profile.save()

            elif 'buy' in params:
                if total_price > user_profile.balance:
                    raise trade_excpetions.NotEnoughMoneyException("Not enough money")

                trade_logic.create_transaction(request.user, stock_symbol, number_of_stocks, stock_price)

                user_profile.balance -= total_price
                user_profile.save()

            return render(request, 'trade.html', context)

    except custom_exception.CustomException as e:
        context.update({'error': str(e)})

    return render(request, 'trade.html', context)
