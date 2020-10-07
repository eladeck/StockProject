from django.test import TestCase
from myapp import stock_api
import requests

class StockAPITestCase(TestCase):
    def setUp(self):
        pass

    def test_get_top_stocks(self):
        response = stock_api._get_top_stocks()
        self.assertEqual(len(response), 20)
