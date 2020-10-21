def test_get_stock_info(self):
        response = stock_api.get_stock_estimates(self.stock_object['symbol'])
        self.assertIsNotNone(response)
        self.assertEqual(response['symbol'], self.stock_object['symbol'])
