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
    # get the data from the backend
    #   id = request.data.get('userID')
    #timeRange = request.data.get('timeRange')
    #statistic = request.data.get('statistic')
    if request.user.is_authenticated():
        params = {}
        params["userID"] = "emilie"
        params["timeRange"] = "7"
        params["statistic"] = "hour"
        r = requests.post('http://localhost:8080/api/v1/favoriteairing/', params)
        print r
        airtimes = r.json

        params["statistic"] = "listing"
        r = requests.post('http://localhost:8080/api/v1/favoriteairing/', params)
        print r
        upcoming = r.json
        if request.user.is_authenticated():
            userID = request.user.username
        queries = api_get_saved_query(userID)
        for query in queries:
            query["safequery"] = str(query["query"]).replace(' ',"~")
        pageData = {}
        pageData['upcoming'] = upcoming
        pageData['airtimes'] = airtimes
        pageData['savedQueries'] = queries
        pageData['tab'] = 'dashboard'
        return HttpResponse(template.render(pageData))
    else:
        return render_to_response('users/home.html')
    
    # return HttpResponse("Hello, world. Go to /mysample/1 to see dashboard 1")

def api_get_search(title):
    #d = '?showtype=' + fields['showtype']+'&language=en'+'&title='+fields['program_title']
    r = requests.get('http://localhost:8080/api/v1/show/'+title)
    return r.json()


def search(request):
    if request.POST:
        fields = dict(request.POST.iteritems())
        title = fields["program_title"]
        result = api_get_search(title)
        return JsonResponse(result, safe=False)

def favourite_programs(request):
    template = loader.get_template('dashboard/favourite.html')
    userID = 'emilie'
    r = requests.get('http://localhost:8080/api/v1/favoriteshow/' + userID)
    obj = r.json()
    favourite_shows = {}
    favourite_shows["favourites"] = obj
    favourite_shows['tab'] = 'dashboard'
    return HttpResponse(template.render(favourite_shows, request))

def add_fav(request):
    template = loader.get_template('dashboard/favourite.html')    
    fields = dict(request.GET.iteritems())
    showID = fields["showId"]
    userID = 'emilie'
    payload = {'userID':userID,'showID':showID}
    r = requests.post('http://localhost:8080/api/v1/favoriteshow/', payload)
    r = requests.get('http://localhost:8080/api/v1/favoriteshow/' + userID)
    obj = r.json()
    favourite_shows = {}
    favourite_shows["favourites"] = obj
    favourite_shows['tab'] = 'dashboard'
    return HttpResponse(template.render(favourite_shows, request))

def api_get_saved_query(userID):
    r = requests.get('http://localhost:8080/api/v1/savedquery/' + userID)
    return r.json()

def remove_fav(request):
    template = loader.get_template('dashboard/favourite.html')    
    fields = dict(request.GET.iteritems())
    showID = fields["showId"]
    userID = 'emilie'
    payload = {'userID':userID,'showID':showID}
    r = requests.delete('http://localhost:8080/api/v1/favoriteshow/', data = payload)
    r = requests.get('http://localhost:8080/api/v1/favoriteshow/' + userID)
    obj = r.json()
    favourite_shows = {}
    favourite_shows["favourites"] = obj
    favourite_shows['tab'] = 'dashboard'
    return HttpResponse(template.render(favourite_shows, request))
