from django.urls import path
from manajer.views import *

app_name = 'manajer'

urlpatterns = [
    path('', dashboard_manajer, name='dashboard'),
]