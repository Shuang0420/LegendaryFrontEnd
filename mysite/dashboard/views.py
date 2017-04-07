from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.template import loader
from django.shortcuts import render_to_response
from rest_framework import status
import json
import requests

# Create your views here.
'''
https://docs.djangoproject.com/en/1.10/intro/tutorial01/
'''
def format(rows, fields):
    try:
        if rows == None or fields == None:
            raise ValueError('Null input')
        if len(rows) == 0:
            return ""
        if len(rows[0]) != len(fields):
            raise ValueError('Inconsistent field lengths')
        dicts = (dict(zip(fields,row)) for row in rows)
        return dicts
    except ValueError as err:
        return (err)

# Create your views here.
def index(request):
    template = loader.get_template('dashboard/main.html')
    upcoming = [['Game of thrones','1: Song of fire and ice','1/1/2017 9:00 pm','1 hr'],['Game of thrones','2: Battle of the bastards','1/8/2017 9:00 pm','1 hr'],['Daredevil','1: The blind lady','1/2/2017 9:00 pm','1 hr'],['Daredevil','2: Struggler','1/9/2017 9:00 pm','1 hr']]
    airtimes = [['Game of thrones','1: Song of fire and ice','2 hr'],['Game of thrones','2: Battle of the bastards','2 hr'],['Daredevil','1: The blind lady','1 hr'],['Daredevil','2: Struggler','2 hr']]
    savedQueries = [['GameOfThrones 1 month','Game of Thrones,"month":1'],['Daredevil 1 month','Daredevil,"month":1']]
    pageData = {}
    pageData['upcoming'] = upcoming
    pageData['airtimes'] = airtimes
    pageData['savedQueries'] = savedQueries
    if request.user.is_authenticated():
        return HttpResponse(template.render(pageData))
    else:
        return render_to_response('users/home.html')
    # return HttpResponse("Hello, world. Go to /mysample/1 to see dashboard 1")

def api_get_search(title):
    #d = '?showtype=' + fields['showtype']+'&language=en'+'&title='+fields['program_title']
    r = requests.get('http://localhost:8080/api/v1/show/'+title)
    print r.json()
    return r.json()


def search(request):
    if request.POST:
        fields = dict(request.POST.iteritems())
        title = fields["program_title"]
        result = api_get_search(title)
        return JsonResponse(result, safe=False)

def favourite_programs(request):
    template = loader.get_template('dashboard/favourite.html')
    favourite_shows = {}
    favourite_shows["favourites"] = [['Game Of Thrones',1],['Mad Men',2]]
    return HttpResponse(template.render(favourite_shows, request))

def add_fav(request):
    fields = dict(request.GET.iteritems())
    showID = fields["showId"]
    payload = {'userID':'emilie','showID':showID}
    r = requests.post('http://localhost:8080/api/v1/favoriteshow/', payload)
    return HttpResponse(r)
   

def remove_fav(request):
    global report_content

    if request.POST:
        fields = dict(request.POST.iteritems())
        content = api_get_report(fields)
        print content
        # update global content for pdf saving
        report_content = content
        return JsonResponse(content, safe=False)
    
