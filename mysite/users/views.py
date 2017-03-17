from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.template import loader


#log/views.py
# Create your views here.
# this login required decorator is to not allow to any
# view without authenticating
#@login_required(login_url="login/")
def home(request):
    template = loader.get_template('users/home.html')
    return render(request,"users/home.html")
