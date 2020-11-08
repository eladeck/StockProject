from django.contrib.auth.models import User
from django.test import TestCase

from myapp import models
from myapp.logic import register_logic


class TestRegisterLogic(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        login = self.client.login(username='testuser', password='12345')

    def test_create_profile(self):
        register_logic.create_profile(self.user)
        does_exist = models.UserProfile.objects.filter(user=self.user).exists()
        self.assertTrue(does_exist)
