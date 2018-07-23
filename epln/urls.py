from django.urls import path
from . import views

app_name = 'pln'
urlpatterns = [
    path('struk/', views.strukView, name='struk'),
]