from django.urls import path
from authentication.views import *

app_name = 'authentication'

urlpatterns = [
    path('', authentication, name='authentication'),
    path('register_manajer_penonton/',register_manajer_penonton , name='register_manajer_penonton'),
    path('register_panitia/',register_panitia , name='register_panitia'),
    path('login/', login, name='login'),
] 