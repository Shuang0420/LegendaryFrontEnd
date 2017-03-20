from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.template import loader
import requests
from django.http import HttpResponse
from django.shortcuts import render_to_response


savedQueries = [['GameOfThrones 1 month','Game of Thrones,"month":1'],['Daredevil 1 month','Daredevil,"month":1']]
#log/views.py
# Create your views here.
# this login required decorator is to not allow to any
# view without authenticating
#@login_required(login_url="login/")
def home(request):
    template = loader.get_template('users/home.html')
    if request.user.is_authenticated():
        userID = request.user.username
        queries = api_get_saved_query(userID)
        #print queries
        data = {}
        #data['savedQueries'] = queries
        data['savedQueries'] = savedQueries
        #return JsonResponse(queries, safe=False)
        return render(request,"users/home.html",data)
    else:
        return render_to_response('users/home.html')


def api_get_saved_query(userID):
    r = requests.get('http://localhost:8080/api/v1/savedquery/' + userID)
    # HttpResponse(r.status_code == requests.codes.ok)
    return r.json()
