from django.shortcuts import render, redirect
import json
import requests
import os
from .models import *
import bcrypt
from django.contrib import messages
import smtplib
# Create your views here.



# render home page
def index(request):
  return render(request, 'index.html')



# process login
def login(request):
  # check for valid login
  errors = validate_login(request.POST)
  if len(errors) > 0:
    for key, val in errors.items():
      print(request, val)
      messages.error(request, val)
    return redirect('/')
  else:
    # fetch user
    mysql = MySQLConnection('MyTradeDB')
    query = 'SELECT * FROM user WHERE username = %(username)s;'
    data = {
      'username': request.POST['username']
    }
    users = mysql.query_db(query, data)
    # check for valid user
    if len(users) > 0:
      user = users[0]
      # check if password matches user and return user
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
  if not 'user_id' in request.session:
    return redirect('/')
  else:
    # clear session
    request.session.flush()
    return redirect('/')



# process register
def register(request):
  # check for valid input
  errors = validate_registration(request.POST)
  if len(errors) > 0:
    for key, val in errors.items():
      messages.error(request, val)
    return redirect('/')
  # check to see if passwords match
  elif request.POST['password'] == request.POST['conf_password']:
    # hash and salt password
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



# email contact 
def contact(request):
  errors = validate_contact(request.POST)
  if len(errors) > 0:
    for key, val in errors.items():
      messages.warning(request, val)
    return redirect('/#contact')
  else: 
    # send message to email
    with smtplib.SMTP('smtp.gmail.com', 587) as smpt:
      
      email_address = 'connorskorburgcontact@gmail.com'
      name = request.POST['name']
      user_email = request.POST['contact-email']
      user_message = request.POST['message']

      smpt.ehlo()
      smpt.starttls()
      smpt.ehlo()
      
      smpt.login(email_address, os.environ.get('CONTACT_EMAIL_PASS'))
      
      subject = f'New Message from {name}, {user_email}'
      body = user_message

      message = f'Subject: {subject}\n\n{body}'

      smpt.sendmail(email_address, email_address, message)
    
      messages.success(request, 'Email Successfully sent!')
    return redirect('/')


# render dashboard
def dashboard(request):
  if not 'user_id' in request.session:
    return redirect('/')
  else:
    # fetch user
    mysql = MySQLConnection('MyTradeDB')
    query = 'SELECT * FROM user WHERE id = %(id)s'
    data = {
      'id': request.session['user_id']
    }
    users = mysql.query_db(query, data)
    user = users[0]
    # get latest trades
    mysql = MySQLConnection('MyTradeDB')
    trades_query = 'SELECT * FROM trade WHERE user_id = %(id)s ORDER BY created_at DESC LIMIT 10;'
    trades_data = {
      'id': request.session['user_id']
    }
    trades = mysql.query_db(trades_query, trades_data)
    # check for valid trade
    if len(trades) == 0:
      trades = False
      latest_trade = False
    else:
      latest_trade = trades[0]
    # fetch latest news
    key = os.environ.get('FINHUB_API_KEY')
    r = requests.get(f'https://finnhub.io/api/v1/news?category=general&token={key}')
    res = r.json()
    context = {
      'results': json.dumps(r.json()),
      'first': res[0],
      'user': user,
      'balance': "{:.2f}".format(user['account_balance']),
      'latest_trade': latest_trade,
      'trades': trades,
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
    # check for valid stock symbol
    if request.POST['symbol'] == '':
      return redirect('/dashboard')
    else:
      # pass symbol data to search query route
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
def sellTrade(request):
  if not 'user_id' in request.session:
    return redirect('/')
  else:

    # get user 
    mysql = MySQLConnection('MyTradeDB')
    user_query = 'SELECT * FROM user WHERE id = %(user_id)s;'
    user_data = {
      'user_id': request.session['user_id']
    }
    users = mysql.query_db(user_query, user_data)
    user = users[0]

    # update user balance
    new_balance = float(user['account_balance']) + float(request.POST['total_price_gained'])
    mysql = MySQLConnection('MyTradeDB')
    update_user_query = 'UPDATE user SET account_balance = %(balance)s WHERE id = %(user_id)s;'
    update_user_data = {
      'balance': new_balance,
      'user_id': request.session['user_id'],
    }
    updated_user = mysql.query_db(update_user_query, update_user_data)

    # get trade that was bought
    mysql = MySQLConnection('MyTradeDB')
    trade_query = 'SELECT * FROM trade WHERE id = %(trade_id)s;'
    trade_data = {
      'trade_id': request.POST['trade_id']
    }
    trades = mysql.query_db(trade_query, trade_data)
    if len(trades) == 0:
      trade = False
    else: 
      trade = trades[0]

    # updated trade bought
    updated_shares = int(trade['shares']) - int(request.POST['shares_sold'])
    updated_total_price = float(trade['price_per_share']) * float(updated_shares)
    mysql = MySQLConnection('MyTradeDB')
    updated_trade_query = 'UPDATE trade SET shares = %(updated_shares)s, total_price = %(updated_total_price)s WHERE id = %(trade_id)s;'
    updated_trade_data = {
      'updated_shares': updated_shares,
      'updated_total_price': updated_total_price,
      'trade_id': request.POST['trade_id']
    }
    updated_trade = mysql.query_db(updated_trade_query, updated_trade_data)

    # create sold trade
    mysql = MySQLConnection('MyTradeDB')
    sold_query = 'INSERT INTO sold_trade (symbol, price_sold, shares_sold, total_price_gained, created_at, updated_at, user_id, trade_id) VALUES (%(symbol)s, %(price_sold)s, %(shares_sold)s, %(total_price_gained)s, NOW(), NOW(), %(user_id)s, %(trade_id)s);'
    sold_data = {
      'symbol': request.POST['symbol'],
      'price_sold': request.POST['price_sold'],
      'shares_sold': request.POST['shares_sold'],
      'total_price_gained': request.POST['total_price_gained'],
      'user_id': request.session['user_id'],
      'trade_id': request.POST['trade_id'],
    }
    sold_trade = mysql.query_db(sold_query, sold_data)
    return redirect('/trades')



# sell trade
def sell(request, id):
  if not 'user_id' in request.session:
    return redirect('/')
  else:
    # fetch user
    mysql = MySQLConnection('MyTradeDB')
    user_query = 'SELECT * FROM user WHERE id = %(id)s'
    user_data = {
      'id': request.session['user_id']
    }
    users = mysql.query_db(user_query, user_data)
    user = users[0]
    # fetch trade to sell
    mysql = MySQLConnection('MyTradeDB')
    query = 'SELECT * FROM trade WHERE id = %(id)s;'
    data = {
      'id': id,
    }
    trade = mysql.query_db(query, data)
    # check to see if trade is found
    if len(trade) == 0:
      trade = False
      current = False
    else:
      trade = trade[0]
      # fetch current price
      key = os.environ.get('FINHUB_API_KEY')
      symbol = trade['symbol']
      r = requests.get(f'https://finnhub.io/api/v1/quote?symbol={symbol}&token={key}')
      res = r.json()
      current = "{:.2f}".format(res['c'])
    context = {
      'trade': trade,
      'user': user,
      'current': current
    }
    return render(request, 'sell.html', context)



# render sold trades 
def trades(request):
  if not 'user_id' in request.session:
    return redirect('/')
  else:
    # fetch user
    mysql = MySQLConnection('MyTradeDB')
    query = 'SELECT * FROM user WHERE id = %(id)s'
    data = {
      'id': request.session['user_id']
    }
    users = mysql.query_db(query, data)
    user = users[0]
    # find trades 
    mysql = MySQLConnection('MyTradeDB')
    trades_query = 'SELECT * FROM trade WHERE user_id = %(id)s ORDER BY created_at DESC LIMIT 10;'
    trades_data = {
      'id': request.session['user_id'],
    }
    trades = mysql.query_db(trades_query, trades_data)
    # check to see if valid trade
    if len(trades) == 0:
      trades = False
    # find sold trades
    mysql = MySQLConnection('MyTradeDB')
    sold_query = 'SELECT * FROM sold_trade WHERE user_id = %(id)s ORDER BY created_at DESC LIMIT 10;'
    sold_data = {
      'id': request.session['user_id'],
    }
    sold_trades = mysql.query_db(sold_query, sold_data)
    # check if sold trades
    if len(sold_trades) == 0:
      sold_trades = False
    context = {
      'balance': "{:.2f}".format(user['account_balance']),
      'trades': trades,
      'sold_trades': sold_trades,
    }
    return render(request, 'trades.html', context)



# add balance
def add_balance(request):
  if not 'user_id' in request.session:
    return redirect('/')
  else:
    # check for valid input
    if request.POST['amount'] == '' or float(request.POST['amount']) <= 0:
      messages.error(request, 'Please Enter Amount!')
      return redirect('/trades')
    # check for valid amount
    elif float(request.POST['amount']) > 1000:
      messages.error(request, 'Amount Must Be $1000 or less!')
      return redirect('/trades')
    else:
      # fetch user
      mysql = MySQLConnection('MyTradeDB')
      query = 'SELECT * FROM user WHERE id = %(id)s'
      data = {
        'id': request.session['user_id']
      }
      users = mysql.query_db(query, data)
      user = users[0]
      new_balance = float(request.POST['amount']) + float(user['account_balance'])
      # update user with new balance
      mysql = MySQLConnection('MyTradeDB')
      balance_query = 'UPDATE user SET account_balance = %(balance)s WHERE id = %(id)s;'
      balance_data = {
        'balance': new_balance,
        'id': request.session['user_id'],
      }
      updated_user = mysql.query_db(balance_query, balance_data)
      return redirect('/trades')
  return redirect('/')