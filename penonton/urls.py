from django.urls import path
from penonton.views import *

app_name = 'penonton'

urlpatterns = [
    path('', dashboard_penonton, name='dashboard'),
    path('pembelian_tiket/', pembelian_tiket, name='pembelian_tiket'),
    path('pilih_pertandingan/', pilih_pertandingan, name='pilih_pertandingan'),
    path('list_pertandingan/', list_pertandingan, name='list_pertandingan'),
    path('beli_tiket/<str:id>', beli_tiket, name='beli_tiket'),
]