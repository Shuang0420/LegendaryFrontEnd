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
import re
import csv
from django.views.decorators.csrf import csrf_exempt
from datetime import date
import calendar

# Create your views here.
'''
https://docs.djangoproject.com/en/1.10/intro/tutorial01/
'''


report_content = None

# Create your views here.
def index(request):
    template = loader.get_template('report/main.html')
    fields = get_dropdown_fields()
    #print 'fields',fields
    if request.user.is_authenticated():
        return render(request,'report/main.html', fields)
    else:
        return render_to_response('users/home.html')
    # return HttpResponse(template.render(request))
    #return render(request,'report/main.html')


def saved_queries(request):
    template = loader.get_template('report/saved_queries.html')
    #return render(request,'report/saved_queries.html',savedQueries)
    if request.user.is_authenticated():
        userID = request.user.username
    queries = api_get_saved_query(userID)
    #print queries
    data = {}
    #data['savedQueries'] = queries
    data['savedQueries'] = queries
    #data['test'] = 'hello'
    #return JsonResponse(queries, safe=False)
    return HttpResponse(template.render(data))



def run_saved_query(request):
    template = loader.get_template('report/saved_queries.html')
    fields = dict(request.GET.iteritems())
    DATA = fields["query"]
    DATA = str(DATA.replace('~',' '))
    DATA = json.loads(DATA)
    content = api_get_report(DATA)
    content = reformReport(content)
    report_content = content
    results = {}
    results['results'] = report_content
    if request.user.is_authenticated():
        userID = request.user.username
    queries = api_get_saved_query(userID)
    results['savedQueries'] = queries
    return HttpResponse(template.render(results))



def get_report(request):
    global report_content
    #ctx ={}
    #ctx.update(csrf(request))
    fields = ['showID', 'title', 'programTitle', 'showType', 'airDateTime',
    'duration', 'stationName', 'showRatingId', 'language', 'description',
    'castcrew', 'programRatingId', 'scheduleRatingID', 'status', 'originalAirDate']
    if request.POST:
        #return render(request, 'report/main.html', ctx)
        #return HttpResponse(report_content, content_type='application/json')
        fields = dict(request.POST.iteritems())
        content = api_get_report(fields)
        content = reformReport(content)
        # update global content for pdf saving
        report_content = content
        return JsonResponse(content, safe=False)
        #return JsonResponse(report_content)


def reformReport(content):
    for c in content:
        dayTime = c['airDateTime'].split('T')
        #print 'dayTime',dayTime
        c['date'] = dayTime[0]
        year, month, day = [int(n) for n in dayTime[0].split('-')]
        d = date(year, month, day)
        day = calendar.day_name[d.weekday()]
        c['day'] = day
        c['start'] = dayTime[1]
    return content


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




def save_csv(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'

    writer = csv.writer(response)
    data = [
    #report_content[0].keys(),
    # keep this so we have nice order
    ["Channel","Affiliate","Date","Day","Start","Duration","Title",
    "Episode","Episode #", "Status"]
    ]
    for item in report_content:
        data.append([str(item['stationName']),
                    str(item['affiliate']),
                    str(item['date']),
                    str(item['day']),
                    str(item['start']),
                    str(item['duration']),
                    str(item['title']),
                    str(item['programTitle']),
                    str(item['programid']),
                    str(item['status'])
                    ])
    for d in data:
        writer.writerow(d)
    return response



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
        data.append([str(item['title']),
                    str(item['showType']),
                    str(item['stationName']),
                    str(item['airDateTime']),
                    str(item['duration']),
                    str(item['description'])
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



"""
Helper function
"""
def get_dropdown_fields():
    attributes = ['title','showType','genre','region']
    res = {}
    for attr in attributes:
        r = requests.get('http://localhost:8080/api/v1/menu/'+ attr)
        js = r.json()
        res[attr] = js[attr]
    return res


def fields_transform(fields):
    DATA = {}
    if 'title' in fields:
        if fields['title'] == 'All':
            DATA['dateFrom'] = reformat_date(fields['dateFrom'])
            DATA['dateTo'] = reformat_date(fields['dateTo'])
            DATA['timeFrom'] = reformat_time(fields['timeFrom'])
            DATA['timeTo'] = reformat_time(fields['timeTo'])
        else:
            DATA['title'] = fields['title']
    if 'showType' in fields and fields['showType'] != 'All':
        DATA['showType'] = fields['showType']
    return DATA


def reformat_date(date):
    parts = date.split('/')
    return parts[-1]+'-'+'-'.join(parts[:-1])

def reformat_time(time):
    parts = re.split(':| ',time)
    if parts[-1] == 'PM':
        return str(int(parts[0])+12)
    else:
        return parts[0]



def api_get_saved_query(userID):
    r = requests.get('http://localhost:8080/api/v1/savedquery/' + userID)
    # HttpResponse(r.status_code == requests.codes.ok)
    queries = r.json()
    for query in queries:
        query["safequery"] = str(query["query"]).replace(' ',"~")
    return queries


def api_save_query(fields):
    print fields
    DATA = fields_transform(fields)
    query = ''
    for k,v in DATA.iteritems():
        query += k + ': ' + v + ';'
    DATA['query'] = json.dumps(DATA)
    DATA['description'] = query
    DATA['userID'] = fields['userID']
    #DATA['description'] = str(DATA).strip()#.replace("'","")
    #DATA = urllib.urlencode(DATA).encode("utf-8")
    r = requests.post('http://localhost:8080/api/v1/savedquery/', data=DATA)
    return r.status_code


def api_get_report(fields):
    DATA = fields_transform(fields)
    r = requests.post('http://localhost:8080/api/v1/program', data=DATA)
    print 'get report',r.json()
    return r.json()
