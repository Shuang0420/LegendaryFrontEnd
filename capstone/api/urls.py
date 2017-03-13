# api/urls.py

from django.conf.urls import url

from api import views

urlpatterns = [
  url(r'^user/?', views.user, name='user'),
  url(r'^favoriteShows/?', views.favoriteShows, name='favoriteShows'),
  url(r'^savedQueries/?', views.savedQueries, name='savedQueries'),
  url(r'^menu/?', views.menu, name='menu'),
  url(r'^programs?.', views.programs, name='programs'),
]