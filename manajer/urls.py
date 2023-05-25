from django.urls import path
from manajer.views import *

app_name = 'manajer'

urlpatterns = [
    path('', dashboard_manajer, name='dashboard'),
    path('list_pertandingan_manajer/', list_pertandingan_manajer, name='list_pertandingan_manajer'),
    path('history_rapat/', history_rapat, name='history_rapat'),
    path('notulensi_rapat/<str:id>/', notulensi, name='notulensi_rapat'),
    path('peminjaman_stadium/', peminjaman_stadium, name='peminjaman_list'),
    path('peminjaman_stadium/stadium/<str:stadium>/', pilih_waktu, name='pilih_waktu'),
    # path('registrasi/', registrasi, name="registrasi"),
    # path('mengelola_tim', mengelola_tim, name='mengelola_tim')
]