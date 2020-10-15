from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('dashboard', views.dashboard),
    path('register', views.register),
    path('login', views.login),
    path('logout', views.logout),
    path('showSearch', views.showSearch),
    path('search', views.search),
    path('buyTrade', views.buyTrade),
    path('sell/<int:id>', views.sell),
    path('sellTrade', views.sellTrade),
    path('trades', views.trades),
    # path('sell', views.sell),
    path('add_balance', views.add_balance),
]