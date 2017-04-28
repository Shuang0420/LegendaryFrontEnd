from django.conf.urls import url

from . import views

app_name = 'mysample'
urlpatterns = [
    # ex: /mysample/
    url(r'^$', views.index, name='index'),
    url(r'^get_report/+$', views.get_report),
    url(r'^save_query/+$', views.save_query),
    url(r'^save_csv/+$', views.save_csv),
]
