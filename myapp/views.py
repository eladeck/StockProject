from django.shortcuts import render, redirect
from myapp import stock_api
from myapp.models import Stock, UserProfile, Transaction
from myapp.forms import UserProfileForm, UserForm
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import logout,login,authenticate
from django.contrib import messages


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

        # initial values for user Profile
        user_profile = UserProfile()
        user_profile.user = newuser
        user_profile.balance = 500
        user_profile.stocks_num = 0
        user_profile.save()

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
    stock_transactions = Transaction.objects.filter(user_id_id=request.user.id)
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
