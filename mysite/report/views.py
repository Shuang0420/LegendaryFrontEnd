from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

# Create your views here.
'''
https://docs.djangoproject.com/en/1.10/intro/tutorial01/
'''

# Create your views here.
def index(request):
    template = loader.get_template('report/main.html')
    return HttpResponse(template.render(request))
    # return HttpResponse("Hello, world. Go to /mysample/1 to see dashboard 1")
