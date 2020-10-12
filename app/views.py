from django.shortcuts import render
import json
import requests
import os

# Create your views here.

# render home page
def index(request):
  return render(request, 'index.html')

# render dashboard
def dashboard(request):
  key = os.environ.get('FINHUB_API_KEY')
  r = requests.get(f'https://finnhub.io/api/v1/news?category=general&token={key}')
  res = r.json()
  context = {
    'results': json.dumps(r.json()),
    'first': res[0],
  }
  return render(request, 'dashboard.html', context)
