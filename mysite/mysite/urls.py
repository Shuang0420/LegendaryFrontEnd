"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from users.forms import LoginForm
from django.contrib.auth import views
from django.views.generic import RedirectView

urlpatterns = [
    # point the root URLconf at the mysample.urls module
    url(r'^users/$',RedirectView.as_view(url='/admin/')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/', views.login, {'template_name': 'users/login.html', 'authentication_form': LoginForm}, name='login'),
    url(r'^logout/$', views.logout, {'next_page': 'login'}, name='logout'),
    url(r'^$', include('dashboard.urls')),
    url(r'^dashboard/', include('dashboard.urls')),
    url(r'^report/', include('report.urls')),
    url(r'^analytics/', include('analytics.urls')),
    url(r'^admin/', admin.site.urls),
    #url(r'^login/$', auth_views.login, name='login'),
    #url(r'^logout/$', auth_views.logout, name='logout'),
]
