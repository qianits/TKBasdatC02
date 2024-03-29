from django.urls import path
from panitia.views import *

app_name = 'panitia'

urlpatterns = [
    path('', dashboard_panitia, name='dashboard'),
    path('mulai_pertandingan/<str:id>', panitia_memulai_pertandingan, name='memulai_pertandingan'),
    # path('notulensi_rapat/<str:id>/', notulensi, name='notulensi_rapat'),
    path('manage_pertandingan/', panitia_manage_pertandingan, name='manage_pertandingan'),
    path('rapat_pertandingan/', daftar_pertandingan, name='daftar_pertandingan'),
    # path('mulai-rapat/<uuid:id_pertandingan>/', mulai_rapat, name='mulai_rapat'),
    path('pertandingan/', pertandingan_list, name='pertandingan_list'),
    path('pertandingan/<uuid:id_pertandingan>/rapat/', rapat_form, name='rapat_form')
]