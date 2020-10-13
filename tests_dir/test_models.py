from django.test import TestCase
from myapp.models import Stock


class StockModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        Stock.objects.create(symbol='1', name='test_stock', price=3.5, change_percent=5, )

    def test_symbol_length(self):
        stock = Stock.objects.get(symbol='1')
        max_length = stock._meta.get_field('symbol').max_length
        self.assertEquals(max_length, 12)

    def test_symbol_not_none(self):
        stock = Stock.objects.get(symbol='1')
        self.assertIsNotNone(stock.symbol)

    def test_name_length(self):
        stock = Stock.objects.get(symbol='1')
        max_length = stock._meta.get_field('name').max_length
        self.assertEquals(max_length, 64)

    def test_name_not_none(self):
        stock = Stock.objects.get(symbol='1')
        self.assertIsNotNone(stock.name)

    def test_price_not_none(self):
        stock = Stock.objects.get(symbol='1')
        self.assertIsNotNone(stock.price)

    def test_change_percent_not_none(self):
        stock = Stock.objects.get(symbol='1')
        self.assertIsNotNone(stock.change_percent)

    def test_primary_excahnge_length(self):
        stock = Stock.objects.get(symbol='1')
        max_length = stock._meta.get_field('primary_exchange').max_length
        self.assertEquals(max_length, 32)
