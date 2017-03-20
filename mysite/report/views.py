from django.shortcuts import render

# Create your views here.
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
#from json2html import *
from django.http import JsonResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, inch, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from StringIO import StringIO
# Create your views here.
'''
https://docs.djangoproject.com/en/1.10/intro/tutorial01/
'''


report_content = None

# Create your views here.
def index(request):
    template = loader.get_template('report/main.html')
    if request.user.is_authenticated():
        return render(request,'report/main.html')
    else:
        return render_to_response('users/home.html')
    # return HttpResponse(template.render(request))
    #return render(request,'report/main.html')


savedQueries = [['GameOfThrones 1 month','Game of Thrones,"month":1'],['Daredevil 1 month','Daredevil,"month":1']]

#[{u'query': u'{"showtype": ["Serie', u'queryDes': None}, {u'query': u'bySeries', u'queryDes': None}, {u'query': u'search by Series', u'queryDes': None}]
#{'savedQueries': [['GameOfThrones 1 month', 'Game of Thrones,"month":1'], ['Daredevil 1 month', 'Daredevil,"month":1']]}

def saved_queries(request):
    template = loader.get_template('report/saved_queries.html')
    #return render(request,'report/saved_queries.html',savedQueries)
    if request.user.is_authenticated():
        userID = request.user.username
    queries = api_get_saved_query(userID)
    #print queries
    data = {}
    #data['savedQueries'] = queries
    data['savedQueries'] = savedQueries
    data['test'] = 'hello'
    #return JsonResponse(queries, safe=False)
    return HttpResponse(template.render(data))


def api_get_saved_query(userID):
    r = requests.get('http://localhost:8080/api/v1/savedquery/' + userID)
    # HttpResponse(r.status_code == requests.codes.ok)
    return r.json()


def api_save_query(fields):
    query = 'series'
    DATA = {}
    DATA['userID'] = fields['userID']
    DATA['query'] = query
    DATA['description'] = str(DATA)
    print DATA
    #DATA = urllib.urlencode(DATA).encode("utf-8")
    r = requests.post('http://localhost:8080/api/v1/savedquery/', data=DATA)
    return r.status_code


def api_get_report(fields):
    #d = '?showtype=' + fields['showtype']+'&language=en'+'&title='+fields['program_title']
    d = '?title='+fields['program_title']
    r = requests.get('http://localhost:8080/api/v1/program'+d)
    print r.json()
    return r.json()


def get_report(request):
    global report_content
    #ctx ={}
    #ctx.update(csrf(request))
    if request.POST:
        '''
    	ctx['program_title'] = request.POST['program_title']
    	ctx['region'] = request.POST['region']
    	ctx['genre'] = request.POST['genre']
    	ctx['date_from'] = request.POST['date_from']
    	ctx['date_to'] = request.POST['date_to']
    	ctx['time_from'] = request.POST['time_from']
    	ctx['time_to'] = request.POST['time_to']
        if request.POST.get('save'):
            print 'save'
            status = save_query(ctx)
            data = {"status":status}
            messages.success(request, "Saved successfully !")
            #return render(request, 'report/main.html', data)
            print status, type(status)
            return HttpResponse(status)
            '''
        #return render(request, 'report/main.html', ctx)
        #return HttpResponse(report_content, content_type='application/json')
        fields = dict(request.POST.iteritems())
        content = api_get_report(fields)
        print content
        # update global content for pdf saving
        report_content = content
        return JsonResponse(content, safe=False)
        #return JsonResponse(report_content)





# FOR PYTHON 2.7
def save_query(request):
    print 'save'
    if request.user.is_authenticated():
        userID = request.user.username
    if request.POST:
        fields = dict(request.POST.iteritems())
        fields['userID'] = userID
        status_code = api_save_query(fields)
        return HttpResponse(status_code == requests.codes.ok)






def save_pdf(request):
    print 'rc',report_content
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=report'
    buff = StringIO()
    menu_pdf = SimpleDocTemplate(buff, rightMargin=72,
                                leftMargin=72, topMargin=72, bottomMargin=18)

    # container for pdf elements
    elements = []
    data = [
    #report_content[0].keys(),
    # keep this so we have nice order
    ["Title", "Show Type","Station Name", "Air Time", "Duration", "Description"]
    ]
    for item in report_content:
        data.append([str(item['Title']),
                    str(item['Showtype']),
                    str(item['StationName']),
                    str(item['airdatetime']),
                    str(item['Duration']),
                    str(item['Description'])
                    ])
    style = TableStyle([('ALIGN',(1,1),(-2,-2),'RIGHT'),
                           ('TEXTCOLOR',(1,1),(-2,-2),colors.red),
                           ('VALIGN',(0,0),(0,-1),'TOP'),
                           ('TEXTCOLOR',(0,0),(0,-1),colors.blue),
                           ('ALIGN',(0,-1),(-1,-1),'CENTER'),
                           ('VALIGN',(0,-1),(-1,-1),'MIDDLE'),
                           ('TEXTCOLOR',(0,-1),(-1,-1),colors.green),
                           ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                           ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                           ])
    # Add the content as before then...
    s = getSampleStyleSheet()
    s = s["BodyText"]
    s.wordWrap = 'CJK'
    data2 = [[Paragraph(cell, s) for cell in row] for row in data]
    t=Table(data2)
    t.setStyle(style)

    #Send the data and build the file
    elements.append(t)

    menu_pdf.build(elements)
    response.write(buff.getvalue())
    buff.close()
    return response
