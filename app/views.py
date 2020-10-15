from django.shortcuts import render, redirect
import json
import requests
import os
from .models import *
import bcrypt
from django.contrib import messages
# Create your views here.

# render home page
def index(request):
  return render(request, 'index.html')


# process login
def login(request):
  errors = validate_login(request.POST)
  if len(errors) > 0:
    for key, val in errors.items():
      print(request, val)
      messages.error(request, val)
    return redirect('/')
  else:
    mysql = MySQLConnection('MyTradeDB')
    query = 'SELECT * FROM user WHERE username = %(username)s;'
    data = {
      'username': request.POST['username']
    }
    users = mysql.query_db(query, data)
    if len(users) > 0:
      user = users[0]
      if bcrypt.checkpw(request.POST['password'].encode(), user['password'].encode()):
        request.session['user_id'] = user['id']
        return redirect('/dashboard')
      else:
        messages.error(request,'Password did not match')
        return redirect('/')
    else:
      return redirect('/')

# process logout
def logout(request):
  request.session.flush()
  return redirect('/')


# process register
def register(request):
  errors = validate_registration(request.POST)
  if len(errors) > 0:
    for key, val in errors.items():
      messages.error(request, val)
    return redirect('/')
  elif request.POST['password'] == request.POST['conf_password']:
    password = request.POST['password']
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    # create the user
    mysql = MySQLConnection('MyTradeDB')
    query = 'INSERT INTO user (first_name, last_name, username, password, account_balance, created_at, updated_at) VALUES (%(first_name)s, %(last_name)s, %(username)s, %(password)s, %(account_balance)s, NOW(), NOW())'
    data = {
      'first_name': request.POST['first_name'],
      'last_name': request.POST['last_name'],
      'username': request.POST['username'],
      'password': password_hash,
      'account_balance': 1000.00,
    }
    user_id = mysql.query_db(query, data)
    request.session['user_id'] = user_id
    return redirect('/dashboard')
  else:
    return redirect('/')


# render dashboard
def dashboard(request):
  if not 'user_id' in request.session:
    return redirect('/')
  else:
    mysql = MySQLConnection('MyTradeDB')
    query = 'SELECT * FROM user WHERE id = %(id)s'
    data = {
      'id': request.session['user_id']
    }
    users = mysql.query_db(query, data)
    user = users[0]
    print(user)
    key = os.environ.get('FINHUB_API_KEY')
    r = requests.get(f'https://finnhub.io/api/v1/news?category=general&token={key}')
    res = r.json()
    context = {
      'results': json.dumps(r.json()),
      'first': res[0],
      'user': user,
      'balance': "{:.2f}".format(user['account_balance']),
    }
    return render(request, 'dashboard.html', context)


# render search page
def showSearch(request):
  if not 'user_id' in request.session:
    return redirect('/')
  else: 
    key = os.environ.get('FINHUB_API_KEY')
    symbol = request.session['symbol']
    r = requests.get(f'https://finnhub.io/api/v1/quote?symbol={symbol}&token={key}')
    res = r.json()
    # find user balance
    mysql = MySQLConnection('MyTradeDB')
    query = 'SELECT * FROM user WHERE id = %(id)s'
    data = {
      'id': request.session['user_id']
    }
    users = mysql.query_db(query, data)
    user = users[0]
    print(user)
    context = {
      'results': json.dumps(r.json()),
      'current': "{:.2f}".format(res['c']),
      'symbol': symbol,
      'balance': "{:.2f}".format(user['account_balance']),
    }
    return render(request, 'search.html', context)


def search(request):
  if not 'user_id' in request.session:
    return redirect('/')
  else:
    print(request.POST)
    if request.POST['symbol'] == '':
      return redirect('/dashboard')
    else:
      request.session['symbol'] = request.POST['symbol']
      return redirect('/showSearch')


# buy trade
def buyTrade(request):
  if not 'user_id' in request.session:
    return redirect('/')
  else:
    if request.method == 'GET':
      return redirect('/dashboard')
    # connect to DB and add a new trade
    mysql = MySQLConnection('MyTradeDB')
    query = 'INSERT INTO trade (symbol, price_per_share, total_price, shares, created_at, updated_at, user_id) VALUES (%(symbol)s, %(price_per_share)s, %(total_price)s, %(shares)s, NOW(), NOW(), %(user_id)s);'
    # set vars to be added to db
    total = float(request.POST['total'])
    price = float(request.POST['price'])
    symbol = request.POST['symbol']
    shares = int(request.POST['shares'])
    # insert data
    data = {
      'symbol': symbol,
      'price_per_share': price,
      'total_price': total,
      'shares': shares,
      'user_id': request.session['user_id']
    }
    result = mysql.query_db(query, data)
    print(result)
    # # fetch user from DB
    mysql = MySQLConnection('MyTradeDB')
    user_query = 'SELECT * FROM user WHERE id = %(id)s'
    user_data = {
      'id': request.session['user_id']
    }
    users = mysql.query_db(user_query, user_data)
    user = users[0]
    # update user's account balance
    new_balance = float(user['account_balance']) - float(request.POST['total'])
    mysql = MySQLConnection('MyTradeDB')
    balance_query = 'UPDATE user SET account_balance = %(balance)s WHERE id = %(id)s;'
    balance_data = {
      'balance': new_balance,
      'id': request.session['user_id'],
    }
    updated_user = mysql.query_db(balance_query, balance_data)
    return redirect('/trades')

# render search page
def sell(request):
  if not 'user_id' in request.session:
    return redirect('/')
  else:
    key = os.environ.get('FINHUB_API_KEY')
    symbol = 'AAPL'
    r = requests.get(f'https://finnhub.io/api/v1/quote?symbol={symbol}&token={key}')
    res = r.json()
    context = {
      'results': json.dumps(r.json()),
      'current': res['c'],
      'symbol': symbol,
    }
    return render(request, 'sell.html', context)


# render sold trades 
def trades(request):
  if not 'user_id' in request.session:
    return redirect('/')
  else:
    mysql = MySQLConnection('MyTradeDB')
    query = 'SELECT * FROM user WHERE id = %(id)s'
    data = {
      'id': request.session['user_id']
    }
    users = mysql.query_db(query, data)
    user = users[0]
    context = {
      'balance': "{:.2f}".format(user['account_balance']),
    }
    return render(request, 'trades.html', context)

# add balance
def add_balance(request):
  if not 'user_id' in request.session:
    return redirect('/')
  else:
    if request.POST['amount'] == '' or float(request.POST['amount']) <= 0:
      messages.error(request, 'Please Enter Amount!')
      return redirect('/trades')
    elif float(request.POST['amount']) > 1000:
      messages.error(request, 'Amount Must Be $1000 or less!')
      return redirect('/trades')
    else:
      print('success')
      mysql = MySQLConnection('MyTradeDB')
      query = 'SELECT * FROM user WHERE id = %(id)s'
      data = {
        'id': request.session['user_id']
      }
      users = mysql.query_db(query, data)
      user = users[0]
      new_balance = float(request.POST['amount']) + float(user['account_balance'])
      mysql = MySQLConnection('MyTradeDB')
      balance_query = 'UPDATE user SET account_balance = %(balance)s WHERE id = %(id)s;'
      balance_data = {
        'balance': new_balance,
        'id': request.session['user_id'],
      }
      updated_user = mysql.query_db(balance_query, balance_data)
      print(updated_user)
      return redirect('/trades')
  return redirect('/')