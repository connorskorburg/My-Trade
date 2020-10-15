from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('dashboard', views.dashboard),
    path('search', views.search),
    path('showSearch', views.showSearch),
    path('trades', views.trades),
    path('buyTrade', views.buyTrade),
    path('sell', views.sell),
    path('login', views.login),
    path('logout', views.logout),
    path('register', views.register),
    path('add_balance', views.add_balance),
]