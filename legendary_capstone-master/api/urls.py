# api/urls.py

from django.conf.urls import url

from api import views

urlpatterns = [
  url(r'^auth?.', views.auth, name='auth'),
  url(r'^user/?', views.user, name='user'),
  url(r'^show/?', views.show, name='show'),
  url(r'^favoriteairing/?', views.favoriteAiring, name='favoriteAiring'),
  url(r'^favoriteshow/+$', views.favoriteShow, name='favoriteShow'),
  url(r'^savedquery/?', views.savedQuery, name='savedQuery'),
  url(r'^menu/?', views.menu, name='menu'),
  url(r'^program?.', views.program, name='program'),
]