from django.urls import path
from penonton.views import *

app_name = 'penonton'

urlpatterns = [
    path('', dashboard_penonton, name='dashboard'),
    path('pembelian_tiket/', pembelian_tiket, name='pembelian_tiket')
]