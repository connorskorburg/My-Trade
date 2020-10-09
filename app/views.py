from django.shortcuts import render

# Create your views here.

# render home page
def index(request):
  return render(request, 'index.html')

# render dashboard
def dashboard(request):
  return render(request, 'dashboard.html')