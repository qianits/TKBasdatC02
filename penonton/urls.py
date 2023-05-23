from django.urls import path
from penonton.views import *

app_name = 'penonton'

urlpatterns = [
    path('', dashboard_penonton, name='dashboard'),
    path('pembelian_tiket/', pilih_stadium, name='pembelian_tiket'),
    path('pembelian_tiket/list_waktu_stadium/', list_waktu_stadium, name='list_waktu_stadium')
]