from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader


# Create your views here.
'''
https://docs.djangoproject.com/en/1.10/intro/tutorial01/
'''

# Create your views here.
def index(request):
    template = loader.get_template('mysample/index.html')
    # return HttpResponse("Hello, world. You're at the polls index.")
    context = {
        'latest_question_list': '1122',
    }
    return HttpResponse(template.render(context, request))



def dashboard(request, question_id):
    return HttpResponse("You're looking at dashboard %s." % question_id)
