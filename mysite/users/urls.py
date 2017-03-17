from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from users.forms import LoginForm

from . import views

app_name = 'users'
urlpatterns = [
    # ex: /mysample/
    # point the root URLconf at the mysample.urls module
    url(r'^$', views.home, name='home'),
    #url(r'^login/+$', auth_views.logout, {'next_page': 'login'}),
    #url(r'^admin/', include(admin.site.urls)),
    #url(r'^$', views.login),
    #url(r'^login/$', views.login, {'template_name': 'login.html'}),
    #url(r'^login/$', views.login, {'template_name': 'login.html', 'authentication_form': LoginForm}),
]
