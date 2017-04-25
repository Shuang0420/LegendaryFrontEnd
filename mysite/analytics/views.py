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
import logging

# {u'showType': u'All', u'title': u'48 Hours', u'dateTo': u'04/22/2017', u'region': u'All', u'dateFrom': u'04/08/2017', u'timeTo': u'3:29 PM', u'timeFrom': u'3:29 AM', u'csrfmiddlewaretoken': u'PW4WJpZ5CmH3VUu2XyhZ4OKdgNapNvPCPQxd97NsIuHYWOlX4FEzXHLuSCG5h5LR'}
VERBOSE = True
# initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create your views here.
def index(request):
    template = loader.get_template('analytics/main.html')
    #fields = get_dropdown_fields()
    fields = {}
    fields['tab'] = 'analytics'
    if request.user.is_authenticated():
        return render(request,'analytics/main.html', fields)
    else:
        return render_to_response('users/home.html')


def get_report(request):
    data = dict(request.POST.iteritems())
    if 'field' and 'value' in request.POST:
        data[request.POST['field']] = request.POST['value']
        if VERBOSE:
            logger.info('REQUEST PARAMS %s' % str(data))
        content = api_get_report(data)
        content = reformReport(content)
        return JsonResponse(content, safe=False)


def api_get_report(fields):
    DATA = fields_transform(fields)
    if VERBOSE:
        logger.info('API DATA %s' % str(DATA))
    r = requests.post('http://localhost:8080/api/v1/program', data=DATA)
    #print 'get report',r.json()
    return r.json()



def fields_transform(fields):
    DATA = {}
    DATA['dateFrom'] = reformat_date(fields['dateFrom'])
    DATA['dateTo'] = reformat_date(fields['dateTo'])
    DATA['timeFrom'] = reformat_time(fields['timeFrom'])
    DATA['timeTo'] = reformat_time(fields['timeTo'])
    # DATA['title'] = fields['title']
    # if 'showType' in fields and fields['showType'] != 'All':
    #     DATA['showType'] = fields['showType']
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
