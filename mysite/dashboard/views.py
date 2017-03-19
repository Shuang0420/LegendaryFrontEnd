from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render_to_response

# Create your views here.
'''
https://docs.djangoproject.com/en/1.10/intro/tutorial01/
'''

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


'''
def dashboard(request, id):
    template = loader.get_template('dashboard.html')
    context = {
            'dashboard_id': id,
    }
    return HttpResponse(template.render(context, request))
    '''
