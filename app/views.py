from django.shortcuts import render

# Create your views here.

# render home page
def index(request):
  return render(request, 'index.html')