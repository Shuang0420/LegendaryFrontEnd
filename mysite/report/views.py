from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.template import loader
from django.template.context_processors import csrf
from django.template import RequestContext

# Create your views here.
'''
https://docs.djangoproject.com/en/1.10/intro/tutorial01/
'''

# Create your views here.
def index(request):
    template = loader.get_template('report/main.html')
    # return HttpResponse(template.render(request))
    return render(request,'report/main.html')


'''
def get_report(request):
    if 'program_title' in request.GET:
        mes=request.GET['program_title']
    return HttpResponse(mes)
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
    return render(request, 'report/main.html', ctx)
