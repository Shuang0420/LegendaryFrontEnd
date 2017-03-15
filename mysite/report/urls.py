from django.conf.urls import url

from . import views

app_name = 'mysample'
urlpatterns = [
    # ex: /mysample/
    url(r'^$', views.index, name='index'),
    url(r'^get_report/+$', views.get_report_by_title),
    url(r'^save_pdf/+$', views.save_pdf),
    # ex: /mysample/1/
    # url(r'^(?P<id>[0-9]+)/$', views.dashboard, name='dashboard'),
]
