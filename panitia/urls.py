from django.urls import path
from panitia.views import *

app_name = 'panitia'

urlpatterns = [
    path('', dashboard_panitia, name='dashboard'),
    path('mulai_pertandingan/', panitia_memulai_pertandingan, name='memulai_pertandingan'),
]