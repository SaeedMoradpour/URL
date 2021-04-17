from django.urls import path
from django.contrib import admin

from . import views

## import functions in views.py, which make tiny url and retrieve original url


urlpatterns = [

    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
]
