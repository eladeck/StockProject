from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
	path('', views.index, name='index'),
	path('stock/<str:symbol>/', views.single_stock, name='single_stock'),
	path('historic/<str:symbol>/', views.single_stock_historic, name='single_stock_historic'),
	path('accounts/login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
	path('accounts/logout/', views.logout_view, name='logout'),
	path('accounts/register/', views.register, name='register'),
	path('trade/', views.trade, name='trade'),
	path('trade/buy', views.buy, name='buy'),
	path('trade/sell', views.sell, name='sell'),
	path('compare', views.compare, name='compare')
]