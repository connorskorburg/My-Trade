from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('dashboard', views.dashboard),
    path('search', views.search),
    path('trades', views.trades),
    path('sell', views.sell),
    path('login', views.login),
    path('logout', views.logout),
    path('register', views.register),
]