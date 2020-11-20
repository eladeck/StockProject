import requests
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from myapp import stock_api
from myapp.models import Stock, UserProfile, Transaction
from myapp.forms import UserProfileForm, UserForm
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import logout,login,authenticate
from django.contrib import messages
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

        # to let the user login after registeration
        user = authenticate(username=email, password=password)
        if user is not None:
            login(request, user)

        return redirect('index')
    else:
        # If not post (regular request) -> render register page
        return render(request, 'register.html', {'page_title': 'Register'})


def logout_view(request):
    logout(request)
    return redirect('index')


def my_account(request):
    user = User.objects.get(pk=request.user.id)
    user_profile = UserProfile.objects.get(user__pk=request.user.id)
    stock_transactions = Transaction.objects.filter(user=request.user)
    frm_user_profile = UserProfileForm(instance=user_profile)
    frm_user = UserForm(instance=user)
    context = {'frm_user': frm_user, 'frm_user_profile': frm_user_profile, 'stock_transactions': stock_transactions}
    return render(request, 'my_account.html', context=context)


def update_my_account(request):
    # user_profile = UserProfile.objects.get(user__pk=request.user.id)
    # frm_user_profile = UserProfileForm(request.POST, instance=user_profile)
    if request.method == 'POST':
        frm_user = UserForm(request.POST, instance=request.user)
        if frm_user.is_valid():
            frm_user.save()
            messages.success(request, 'Profile details updated successfully.')
        else:
            messages.error(request, f'error: {frm_user.errors.as_data()}')
    return redirect('/accounts/myaccount')


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

@login_required
def user_money_view(request):
    total_money = 0
    if request.method == 'GET':
        user = User.objects.get(pk=request.user.id)
        user_profile = UserProfile.objects.get(user__pk=request.user.id)
        stock_transactions = Transaction.objects.filter(user=request.user)
        #stock_data = {"sympol": "", "quantity": 0, "current_price": 0}
        stocks_data = {}

        for trans in stock_transactions:
            if trans.stock_symbol not in stocks_data:
                stock_data = {}
                recent_stock_price = trade_logic.get_stock_price(trans.stock_symbol)
                stock_data["current_price"] = recent_stock_price
                stock_data["quantity"] = trans.quantity
                stocks_data[trans.stock_symbol] = stock_data
            else:
               stocks_data[trans.stock_symbol]["quantity"] += trans.quantity

        total_money += user_profile.balance
        for stock,data in stocks_data.items():
            total_money += data["quantity"] * data["current_price"]

        #frm_user_profile = UserProfileForm(instance=user_profile)
        #frm_user = UserForm(instance=user)
        context = {'balance': user_profile.balance,'money': total_money, "stocks_data": stocks_data}
        return render(request, 'user_money.html', context=context)
