from django.urls import path
from panitia.views import *

app_name = 'panitia'

urlpatterns = [
    path('', dashboard_panitia, name='dashboard'),
    path('pertandingan/', pertandingan_list, name='pertandingan_list'),
    path('pertandingan/<uuid:id_pertandingan>/rapat/', rapat_form, name='rapat_form')
]