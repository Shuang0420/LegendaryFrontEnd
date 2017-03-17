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
def saved_queries(request):
    template = loader.get_template('report/saved_queries.html')
    #return render(request,'report/saved_queries.html',savedQueries)
    data = {}
    data['savedQueries'] = savedQueries
    print data
    return HttpResponse(template.render(data))


jsonfile = [{"program_title": "king","region": "US","genre":"comedy", "start_date": "03/14/2017", "end_date": "03/15/2017", "time": "09:30"}]


'''
def loadJson():
    infoFromJson = json.loads(jsonfile)
    return json2html.convert(json = infoFromJson)
    '''

def process_query(fields):
    r = requests.get('http://localhost:8080/api/v1/savedQueries/', data=fields)
    print fields
    print r.status_code
    content = r.json()
    # HttpResponse(r.status_code == requests.codes.ok)
    return content



def get_report(request):
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
        #return HttpResponse(jsonfile, content_type='application/json')
        fields = dict(request.POST.iterlists())
        content = process_query(fields)
        return JsonResponse(jsonfile, safe=False)
        #return JsonResponse(jsonfile)





# FOR PYTHON 2.7
def save_query(request):
    print 'save'
    userID = 'test'
    query = 'test query'
    if request.POST:
        DATA = dict(request.POST.iterlists())
        DATA['userID'] = userID
        print DATA
        #DATA = urllib.urlencode(DATA).encode("utf-8")
        r = requests.put('http://localhost:8080/api/v1/savedQueries/', data=DATA)
        return HttpResponse(r.status_code == requests.codes.ok)






def save_pdf(request):
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=report'
    buff = StringIO()
    menu_pdf = SimpleDocTemplate(buff, rightMargin=72,
                                leftMargin=72, topMargin=72, bottomMargin=18)

    # container for pdf elements
    elements = []
    data = [
    jsonfile[0].keys(),
    ]
    for item in jsonfile:
        data.append(item.values())
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
