from django.conf.urls import url

from . import views

app_name = 'mysample'
urlpatterns = [
    # ex: /mysample/
    url(r'^$', views.index, name='index'),
    url(r'^add_fav/+$', views.add_fav),
    url(r'^remove_fav/+$', views.remove_fav),
    url(r'^search/+$', views.search),
    url(r'^favourite/+$', views.favourite_programs),
    # ex: /mysample/1/
    # url(r'^(?P<id>[0-9]+)/$', views.dashboard, name='dashboard'),
]
