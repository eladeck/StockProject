from django.test import TestCase
from myapp import stock_api
import requests
import random


class StockAPITestCase(TestCase):
    def setUp(self):
        self.public_token = stock_api.PUBLIC_TOKEN
        self.base_url = stock_api.BASE_URL
        """
        next 2 lines do this:
        get all stock symbols from the api, choose a random one to use it for testing.
        We could test all of them, but doing thousands of requests for a test does not make sense to me
        """
        response = requests.get('{}/beta/ref-data/symbols?token={}'.format(
            self.base_url,
            self.public_token))
        self.stock_object = random.choice(response.json())
        # it is also possible to create a static symbol object to use.

    def test_request_data(self):
        # TODO: the function stock_api._request_data() needs exception handling.
        response = stock_api._request_data('/stable/stock/{symbol}/quote'.format(symbol=self.stock_object['symbol']),
                                           additional_parameters={'displayPercent': 'true'})
        self.assertIsNotNone(response)

        with self.assertRaises(Exception):
            response = stock_api._request_data("")

    def test_get_top_stocks(self):
        response = stock_api._get_top_stocks()
        self.assertIsNotNone(response)
        # function name get_top_stocks actually returns top 20 stocks
        # that is why the following line checks with 20
        self.assertEqual(len(response), 20)

    def test_get_stock_info(self):
        response = stock_api.get_stock_info(self.stock_object['symbol'])
        self.assertIsNotNone(response)
        self.assertEqual(response['symbol'], self.stock_object['symbol'])

        with self.assertRaises(Exception):
            response = stock_api.get_stock_info("")

    def test_get_stock_historic_prices(self):
        response = stock_api.get_stock_historic_prices(self.stock_object['symbol'])
        self.assertIsNotNone(response)
        with self.assertRaises(Exception):
            response = stock_api.get_stock_historic_prices("")
