# api/urls.py

from django.conf.urls import url

from api import views

urlpatterns = [
  url(r'^user/?', views.user, name='user'),
  url(r'^favoriteshow/?', views.favoriteShow, name='favoriteShow'),
  url(r'^savedquery/?', views.savedQuery, name='savedQuery'),
  url(r'^menu/?', views.menu, name='menu'),
  url(r'^program?.', views.program, name='program'),
]