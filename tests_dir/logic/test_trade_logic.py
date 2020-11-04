from django.contrib.auth.models import User
from django.test import TestCase

from myapp import models
from myapp.logic import trade_logic


class TestTradeLogic(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

    def test_get_stock_price(self):
        stock_price = trade_logic.get_stock_price('A')
        self.assertIsNotNone(stock_price)

    def test_create_transaction(self):
        stock_info = {
            'stock_symbol': 'A',
            'number_of_stocks': 10,
            'price': 3.0
        }

        trade_logic.create_transaction(user=self.user, **stock_info)

        does_exist = models.Transaction.objects.filter(user=self.user).exists()
        self.assertTrue(does_exist)

    def test_get_number_of_stocks(self):
        stock_info = {
            'stock_symbol': 'A',
            'number_of_stocks': 10,
            'price': 3.0
        }
        trade_logic.create_transaction(user=self.user, **stock_info)

        stock_info = {
            'stock_symbol': 'A',
            'number_of_stocks': -5,
            'price': 3.0
        }
        trade_logic.create_transaction(user=self.user, **stock_info)

        number_of_stocks = trade_logic.get_number_of_stocks(self.user, 'A')
        self.assertEqual(number_of_stocks, 5)
