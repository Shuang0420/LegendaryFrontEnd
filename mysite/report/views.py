from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.template import loader
from django.template.context_processors import csrf
from django.template import RequestContext
import requests
import urllib2
from django.contrib import messages
import json
#import json2html
from json2html import *
from django.http import JsonResponse
# Create your views here.
'''
https://docs.djangoproject.com/en/1.10/intro/tutorial01/
'''

# Create your views here.
def index(request):
    template = loader.get_template('report/main.html')
    # return HttpResponse(template.render(request))
    return render(request,'report/main.html')


jsonfile = [{"program_title": "king","region": "US","genre":"comedy", "start_date": "03/14/2017", "end_date": "03/15/2017", "time": "09:30"}]


'''
def loadJson():
    infoFromJson = json.loads(jsonfile)
    return json2html.convert(json = infoFromJson)
    '''


def get_report_by_title(request):
    ctx ={}
    ctx.update(csrf(request))
    if request.POST:
    	ctx['program_title'] = request.POST['program_title']
    	ctx['region'] = request.POST['region'] +','
    	ctx['genre'] = request.POST['genre']
    	ctx['date_range'] = 'Date Range: '
    	ctx['date_from'] = request.POST['date_from']
    	ctx['date_to'] = '- '+request.POST['date_to']
    	ctx['time_range'] = 'Time Range: '
    	ctx['time_from'] = request.POST['time_from']
    	ctx['time_to'] = '- '+request.POST['time_to']
        if request.POST.get('save'):
            print 'save'
            save_query(ctx)
            messages.success(request, "Saved successfully !")
            return render(request, 'report/main.html')
            #return HttpResponse(messages)
    #return render(request, 'report/main.html', ctx)
    #return HttpResponse(jsonfile, content_type='application/json')
    return JsonResponse(jsonfile, safe=False)
    #return JsonResponse(jsonfile)



# FOR PYTHON 2.7
def save_query(DATA):
    userID = 'test'
    query = 'test query'
    DATA['userID'] = userID
    print DATA
    #DATA = urllib.urlencode(DATA).encode("utf-8")
    r = requests.put('http://localhost:8080/api/v1/savedQueries/', data=DATA)
    print r
