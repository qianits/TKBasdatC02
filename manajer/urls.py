from django.urls import path
from manajer.views import *

app_name = 'manajer'

urlpatterns = [
    path('', dashboard_manajer, name='dashboard'),
    path('list_pertandingan/', list_pertandingan, name='list_pertandingan'),
    path('history_rapat/', history_rapat, name='history_rapat'),
    path('notulensi_rapat/<str:rapat>/', notulensi_rapat, name='notulensi_rapat')
]