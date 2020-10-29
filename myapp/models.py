from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Stock(models.Model):
    symbol = models.CharField(max_length=12, primary_key=True)
    name = models.CharField(max_length=64)
    top_rank = models.IntegerField(null=True)
    price = models.FloatField()
    change = models.FloatField(null=True)
    change_percent = models.FloatField()
    market_cap = models.FloatField(null=True)
    primary_exchange = models.CharField(null=True, max_length=32)


class UserProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	balance = models.FloatField()
	stocks_num = models.IntegerField(default=0)


class Transaction(models.Model):
	#trans_id (Pk) - comes by Django
	user_id = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True)
	stock_symbol = models.CharField(max_length=12,null=True)
	trans_date = models.DateTimeField()
	buy_or_Sell = models.IntegerField()
	quantity = models.IntegerField()
	price = models.FloatField()