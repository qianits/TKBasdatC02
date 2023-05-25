from django.urls import path
from panitia.views import *

app_name = 'panitia'

urlpatterns = [
    path('', dashboard_panitia, name='dashboard'),
    path('rapat_pertandingan/', daftar_pertandingan, name='daftar_pertandingan'),
    path('mulai-rapat/<uuid:id_pertandingan>/', mulai_rapat, name='mulai_rapat'),
]