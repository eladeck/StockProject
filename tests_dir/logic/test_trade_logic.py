from django.contrib.auth.models import User
from django.test import TestCase

from myapp import models
from myapp.logic import trade_logic



class TestTradeLogic(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        login = self.client.login(username='testuser', password='12345')


    def test_parse_input(self):
        params = {
            'number_of_stocks': 10,
            'stock_selector': 'A'
        }
        stock_info = trade_logic.extract_info(params)
        self.assertIsNotNone(stock_info['number_of_stocks'])
        self.assertIsNotNone(stock_info['total_price'])

    def test_parse_input_invalid_data(self):
        params = {
            'number_of_stocks': 'a',
            'stock_selector': 'A'
        }
        stock_info = trade_logic.extract_info(params)
        self.assertIsNone(stock_info)

    def test_create_transaction(self):
        stock_info = {
            'symbol':'A',
            'number_of_stocks': 10,
            'total_price': 30.0,
            'price': 3.0
        }

        trade_logic.create_transaction(user=self.user,stock_info=stock_info)

        does_exist = models.Transaction.objects.filter(user=self.user).exists()
        self.assertTrue(does_exist)

    def test_get_number_of_stocks(self):
        stock_info = {
            'symbol': 'A',
            'number_of_stocks': 10,
            'total_price': 30.0,
            'price': 3.0
        }
        trade_logic.create_transaction(user=self.user, stock_info=stock_info)

        stock_info = {
            'symbol': 'A',
            'number_of_stocks': -5,
            'total_price': 30.0,
            'price': 3.0
        }
        trade_logic.create_transaction(user=self.user, stock_info=stock_info)

        number_of_stocks = trade_logic.get_number_of_stocks(self.user,'A')
        self.assertEqual(number_of_stocks,5)


