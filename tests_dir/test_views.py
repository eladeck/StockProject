from django.http import JsonResponse
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
import myapp.models as models


class BaseTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.home_url = reverse('index')
        self.single_stock_url = reverse('single_stock', args=['AAPL'])
        self.historic_url = reverse('single_stock_historic', args=['AAPL'])
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.compare_url = reverse('compare')
        self.trade_url = reverse('trade')
        self.buy_url = reverse('buy')
        self.sell_url = reverse('sell')
        self.user = {
            'firstname': 'Alaa',
            'lastname': 'Yahia',
            'email': 'alaa.yahia.1995@gmail.com',
            'password': 'rails7777',
        }


class TestViews(BaseTest):

    def test_project_home_list_GET(self):
        response = self.client.get(self.home_url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')

    def test_project_single_stock_GET(self):
        response = self.client.get(self.single_stock_url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'single_stock.html')

    def test_project_historic_GET(self):
        response = self.client.get(self.historic_url)
        self.assertEquals(response.status_code, 200)
        self.assertIsInstance(response, JsonResponse)

    def test_compare(self):
        response = self.client.get(self.compare_url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'compare_two_stocks.html')


class RegisterTest(BaseTest):
    def test_can_view_page_correctly(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')

    def test_can_register_user(self):
        response = self.client.post(self.register_url, self.user, format='text/html')
        self.assertEqual(response.status_code, 302)

    """
   Tests:
   def test_cant_register_user_withshortpassword(self):
        response=self.client.post(self.register_url,self.user_short_password,format='text/html')
        self.assertEqual(response.status_code,400)

   
   # def test_cant_register_user_with_invalid_email(self):
   #      response=self.client.post(self.register_url,self.user_invalid_email,format='text/html')
   #      self.assertEqual(response.status_code,400)


   # def test_cant_register_user_with_taken_email(self):
   #      self.client.post(self.register_url,self.user,format='text/html')
   #      response=self.client.post(self.register_url,self.user,format='text/html')
   #      self.assertEqual(response.status_code,400)"""


class LoginTest(BaseTest):
    def test_can_access_page(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_login_success(self):
        self.client.post(self.register_url, self.user, format='text/html')
        user = User.objects.filter(email=self.user['email']).first()
        user.is_active = True
        user.save()
        response = self.client.post(self.login_url, self.user, format='text/html')
        self.assertEqual(response.status_code, 200)

    def test_cant_login_with_no_username(self):
        response = self.client.post(self.login_url, {'password': 'passwpedtest', 'username': ''},
                                    format='text/html')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_cant_login_with_no_password(self):
        response = self.client.post(self.login_url, {'username': 'usernametest', 'password': ''},
                                    format='text/html')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')


class LogoutTest(BaseTest):
    def test_can_access_page(self):
        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, 302)  # 302: should be redirected.
        # TODO: issue 4.
        # self.assertTemplateUsed(response,'index.html')

    def test_logout_success(self):
        self.client.post(self.register_url, self.user, format='text/html')
        user = User.objects.filter(email=self.user['email']).first()
        user.is_active = True
        user.save()
        response = self.client.post(self.logout_url, self.user, format='text/html')
        user.is_active = False
        user.save()
        self.assertEqual(response.status_code, 302)  # 302: should be redirected.


class TradeTest(BaseTest):

    def set_up_trade(self):
        self.client.post(self.register_url, self.user, format='text/html')
        res = self.client.post(self.login_url, self.user, format='text/html')
        self.assertTemplateUsed(res, 'login.html')
        user1 = User.objects.filter(email=self.user['email']).first()
        self.assertEqual(user1.is_active, True)
        self.client.login(username=self.user['email'], password=self.user['password'])

    def test_access_trade_page_if_logedin(self):
        self.set_up_trade()
        response = self.client.get(self.trade_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'trade.html')

    def test_access_trade_page_if_not_logedin(self):
        response = self.client.get(self.trade_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_valid_buy(self):
        self.set_up_trade()
        user = User.objects.filter(email=self.user['email']).first()
        first_balance = user.userprofile.balance
        response = self.client.post(self.buy_url, {'stock_selector': 'AAPL', 'number_of_stocks': 4}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'trade.html')
        user = User.objects.filter(email=self.user['email']).first()
        balance = user.userprofile.balance
        self.assertGreater(first_balance, balance)
        transactions = models.Transaction.objects.filter(user=user)
        self.assertIsNotNone(transactions.get())

    def test_invalid_buy(self):
        self.set_up_trade()
        user = User.objects.filter(email=self.user['email']).first()
        first_balance = user.userprofile.balance
        response = self.client.post(self.buy_url, {'stock_selector': 'AAPL', 'number_of_stocks': 1000}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'trade.html')
        user = User.objects.filter(email=self.user['email']).first()
        balance = user.userprofile.balance
        self.assertEquals(first_balance, balance)
        self.assertEquals(response.context['error'], "not enough balance")

    def test_valid_sell(self):
        self.set_up_trade()
        user = User.objects.filter(email=self.user['email']).first()
        buy_response = self.client.post(self.buy_url, {'stock_selector': 'AAPL', 'number_of_stocks': 4}, follow=True)
        self.assertEqual(buy_response.status_code, 200)
        buy_balance = user.userprofile.balance
        response = self.client.post(self.sell_url, {'stock_selector': 'AAPL', 'number_of_stocks': 3}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'trade.html')
        user = User.objects.filter(email=self.user['email']).first()
        balance = user.userprofile.balance
        self.assertGreater(balance, buy_balance)
        transactions = models.Transaction.objects.filter(user=user)
        self.assertEqual(abs(transactions.first().quantity), 4)
        self.assertEqual(abs(transactions.last().quantity), 3)

    def test_invalid_sell(self):
        self.set_up_trade()
        user = User.objects.filter(email=self.user['email']).first()
        first_balance = user.userprofile.balance
        response = self.client.post(self.sell_url, {'stock_selector': 'AAPL', 'number_of_stocks': 4}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'trade.html')
        user = User.objects.filter(email=self.user['email']).first()
        balance = user.userprofile.balance
        self.assertEqual(balance, first_balance)
        self.assertEquals(response.context['error'], "Not enough stocks to sell")
