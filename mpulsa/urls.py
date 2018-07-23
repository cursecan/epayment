from django.urls import path

from . import views

app_name = 'pulsa'
urlpatterns = [
    path('', views.pulsaTopup, name='index'),
]