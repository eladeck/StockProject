from typing import List

from django.test import TestCase  # since we are not using the database, we will just use the builtin unittest.TestCase
from unittest import TestCase


class TestNothingAtAll(TestCase):

    def test_demo_equal(self):
        a_number: int = 1
        self.assertEqual(a_number, a_number)

    def test_demo_false(self):
        this_is_false: List = []  # an empty list is False
        self.assertFalse(this_is_false)
