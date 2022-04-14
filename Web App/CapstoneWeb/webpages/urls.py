from django.urls import path

from . import views
from django.conf.urls import include, url
import django.contrib.auth.urls as urls
from django.shortcuts import redirect

urlpatterns = [
    # path('', views.home, name='home'),
    # path('welcome/', views.welcome, name='welcome'),
    
    # path('trip/', views.inspect_trip, name='trip'),
    path('trip/<str:trip_id>/', views.inspect_trip, name='trip1'),
    path('welcome/', views.welcome, name='welcome'),
    path('welcome/<str:sort_by>/<int:is_ascending>/', views.welcome, name='welcome1'),
    # path('trips/', views.trips, name='trips'),
    # path('trips/<str:sort_by>/<int:is_ascending>/', views.trips, name='trips1'),
    path('grid/', views.grid, name='grid'),
    # path('example/', views.example, name='example'),
    # path('accounts/', include('django.contrib.auth.urls')),
    # path('login/', views.home, name='login'),
    urls.urlpatterns[0],
    urls.urlpatterns[1],
    # url(r'^user/login-custom-template/$', auth_views.login, {'template_name': 'path-to-custom-template.html'}, name='login-custom')
    path('', lambda request: redirect('login/', permanent=False)),

]
