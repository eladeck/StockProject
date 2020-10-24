from django.db import models
from django.contrib.auth.models import User #maybe I will need it.

SELL = 0
BUY = 1
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

class Transaction(models.Model):
	#trans_id (Pk) - comes by Django
	#user_id  (fk  with Users table) - to do.
	stock_id = models.ForeignKey(Stock, on_delete=models.CASCADE)  # to understand on delete
	trans_date = models.DateField()
	buy_or_Sell = models.IntegerField(null=True)
	quantity = models.IntegerField(null=True)
	price = models.FloatField(null=True)
	new_balance = models.FloatField(null=True)








