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
from datetime import datetime
import calendar
import logging
from collections import defaultdict


# initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache dropdown menu
cachedMenu = {}

# ignore 'region'
queryFields = set(['title','programTitle','showType','status','genre','seasonEpisode','dateFrom','dateTo','timeFrom','timeTo','keyword','orderBy','timezone'])
reportFields = ['stationName', 'affiliate', 'date', 'day', 'start','timezone', 'duration','title','programTitle','seasonEpisode','status']
criteriaFields = ['title','episodeTitle','status','timezone']


# default report dict
default_report_dict = dict.fromkeys(reportFields, 'empty')


report_content = None

# Create your views here.
def index(request):
    template = loader.get_template('analytics/main.html')
    fields = get_dropdown_fields()
    fields['tab'] = 'analytics'
    if request.user.is_authenticated():
        return render(request,'analytics/main.html', fields)
    else:
        return render_to_response('users/home.html')


def CreateTableData(query_results):
    total_show_time = {}
    prime_time = {}
    FirstRun = {}
    titleSet = {}
    affiliateSet = {}
    for res in query_results:
        title = res['title']
        if title not in titleSet:
            titleSet[title] = len(titleSet)
        aff = res['stationName']
        if aff is not None and aff != "" and aff not in affiliateSet:
            affiliateSet[aff] = len(affiliateSet)
        if title in total_show_time:
            total_show_time[title] += 1
            time = datetime.strptime(res['airDateTime'],"%Y-%m-%dT%H:%M:%S").time().hour
            if time >= 20 and time <= 23:
                prime_time[title] += 1
            if res['status'] == 'FirstRun':
                FirstRun[title] += 1
        else:
            total_show_time[title] = 1
            time = datetime.strptime(res['airDateTime'],"%Y-%m-%dT%H:%M:%S").time().hour
            prime_time[title] = 0
            FirstRun[title] = 0
            if time >= 20 and time <= 23:
                prime_time[title] += 1
            if res['status'] == 'FirstRun':
                FirstRun[title] += 1
    # create the tables for Graphs - Show affiliate bar chart
    Show_affiliate = []
    Show_affiliate.append(["TV Shows"]*(len(affiliateSet)+1))
    Show_airings = []
    Show_airings.append(["TV Shows"]*(len(titleSet)+1))
    Show_airings.append(["Total Airings"]*(len(titleSet)+1))
    Show_airings.append(["Prime Time Airings"]*(len(titleSet)+1))
    Show_airings.append(["First Run"]*(len(titleSet)+1))
    for i in range(len(titleSet)):
        Show_affiliate.append([0]*(len(affiliateSet)+1 ))
    for aff in affiliateSet.keys():
        Show_affiliate[0][affiliateSet[aff]+1] = aff
    for show in titleSet.keys():
        Show_affiliate[titleSet[show]+1][0] = show
        Show_airings[0][titleSet[show]+1] = show
    for res in query_results:
        title = res['title']
        aff = res['stationName']
        index_title = titleSet[title]+1
        if aff is not None and aff != "" and aff in affiliateSet:
            index_aff = affiliateSet[aff] + 1
            Show_affiliate[index_title][index_aff] += 1
    # create the table for Graphs - show time
    for show in titleSet.keys():
        Show_airings[1][titleSet[show]+1] = total_show_time[show]
        Show_airings[2][titleSet[show]+1] = prime_time[show]
        Show_airings[3][titleSet[show]+1] = FirstRun[show]

    show_hours_table = []
    show_hours_table.append(['Tv Show', 'Air Time'])
    show_prime_hours_table = []
    show_prime_hours_table.append(['Tv Show', 'Prime Air Time'])
    show_first_hours_table = []
    show_first_hours_table.append(['Tv Show', 'First Run Time'])
    for i in range(len(titleSet)):
        show_hours_table.append(['Show Name',0])
        show_prime_hours_table.append(['Show Name',0])
        show_first_hours_table.append(['Show Name',0])
    for show in titleSet.keys():
        show_hours_table[titleSet[show]+1][0] = show
        show_hours_table[titleSet[show]+1][1] = float(total_show_time[show])
        show_prime_hours_table[titleSet[show]+1][0] = show
        show_prime_hours_table[titleSet[show]+1][1] = float(prime_time[show])
        show_first_hours_table[titleSet[show]+1][0] = show
        show_first_hours_table[titleSet[show]+1][1] = float(FirstRun[show])
    return Show_affiliate,Show_airings,show_hours_table,show_prime_hours_table,show_first_hours_table

def get_report(request):
    global report_content
    data = dict(request.POST.iteritems())
    allFields = defaultdict(dict)
    commonFields = defaultdict(dict)
    res = []
    multiTimeZones = False
    for k,v in data.iteritems():
        if k == 'timezone' and v == 'All':
            multiTimeZones = True
        if k != "csrfmiddlewaretoken" and k != "title_0" and k != 'title_1' and k != 'title_2':
            commonFields[k] = v
    for k,v in data.iteritems():
        if (k == "title_0" or k == 'title_1' or k == 'title_2') and v != 'All':
            logger.info('REQUEST PARAMS %s' % str(v))
            commonFields['title'] = v
            content = api_get_report(commonFields)
            content = reformReport(content) if content else [default_report_dict]
            res.extend(content)
    report_content = res
    Show_affiliate,\
    Show_airings,\
    show_hours_table,\
    show_prime_hours_table,\
    show_first_hours_table = CreateTableData(report_content)
    dict_graphs = {'station_graph':Show_affiliate,\
                   'airtime_graph':Show_airings,\
                   'pie_total' : show_hours_table,\
                   'pie_prime' : show_prime_hours_table,\
                   'pie_firstRun' : show_first_hours_table}
    return JsonResponse(dict_graphs,safe=False)


def save_query(request):
    logger.info('SAVING QUERY')
    if request.user.is_authenticated():
        userID = request.user.username
    if request.POST:
        fields = dict(request.POST.iteritems())
        fields['userID'] = userID
        fields[request.POST['field']] = request.POST['value']
        status_code = api_save_query(fields)
        return HttpResponse(status_code == requests.codes.ok)




"""
Helper function
"""
def get_dropdown_fields():
    global cachedMenu
    if cachedMenu:
        return cachedMenu
    attributes = criteriaFields
    res = {}
    for attr in attributes:
        r = requests.get('http://localhost:8080/api/v1/menu/'+ attr)
        js = r.json()
        if type(js) is dict:
            res[attr] = js[attr]

    cachedMenu = res
    return res


def api_get_report(fields):
    DATA = fields_transform(fields)
    r = requests.post('http://localhost:8080/api/v1/program', data=DATA)
    return r.json()



def api_save_query(fields):
    DATA = fields_transform(fields)
    query = ''
    for k,v in DATA.iteritems():
        query += k + ': ' + v + ';'
    DATA['query'] = json.dumps(DATA)
    DATA['description'] = query
    DATA['userID'] = fields['userID']
    r = requests.post('http://localhost:8080/api/v1/savedquery/', data=DATA)
    return r.status_code

def fields_transform(fields):
    DATA = {}
    for k,v in fields.iteritems():
        if v and v != 'All' and k in queryFields: DATA[k] = v
    DATA['dateFrom'] = reformat_date(fields['dateFrom'])
    DATA['dateTo'] = reformat_date(fields['dateTo'])
    DATA['timeFrom'] = reformat_time(fields['timeFrom'])
    DATA['timeTo'] = reformat_time(fields['timeTo'])
    return DATA

def reformat_date(date):
    parts = date.split('/')
    return parts[-1]+'-'+'-'.join(parts[:-1])

def reformat_time(time):
    parts = re.split(':| ',time)
    if parts[-1] == 'PM':
        return str(int(parts[0])+12)
    else:
        return str(int(parts[0])%12)


def reformReport(content):
    for c in content:
        if 'airDateTime' not in c: continue
        dayTime = c['airDateTime'].split('T')
        c['date'] = dayTime[0]
        year, month, day = [int(n) for n in dayTime[0].split('-')]
        d = date(year, month, day)
        day = calendar.day_name[d.weekday()]
        c['day'] = day
        c['start'] = dayTime[1]
    return content


def save_csv(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'

    writer = csv.writer(response)
    data = [
    # keep this so we have nice order
    ["Channel","Affiliate","Date","Day","Start Time","TimeZone","Duration","Title",
    "Episode","Episode #", "Status"]
    ]
    for item in report_content:
        row = []
        for f in reportFields:
            row.append(item[f])
        data.append(row)
    for d in data:
        writer.writerow(d)
    return response
