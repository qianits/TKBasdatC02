from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
import psycopg2
import locale
import uuid
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse
locale.setlocale(locale.LC_ALL, '')
from django.http import JsonResponse
from manajer.models import *
from utils.query import *

def dashboard_manajer(request):
    context={}
    return render(request, 'dashboard_manajer.html', context)

### UNTUK R List_Pertandingan
# Menampilkan pertandingan-pertandingan timnya
def list_pertandingan_manajer(request):
    # TODO: Ganti ID Manajer dengan ID manajer login
    id_manajer = "63ede258-e39c-45b4-b8b8-8de9f8e891bd"
    context ={}
    list_tanding = query(f"""
    SELECT string_agg(tp.nama_tim, ' vs ') as tim, s.nama, p.start_datetime, p.end_datetime::time as waktuakhir, p.id_pertandingan
    FROM Pertandingan p
    JOIN Tim_Pertandingan tp ON p.id_pertandingan = tp.id_pertandingan
    JOIN Stadium s ON s.id_stadium = p.stadium
    WHERE p.id_pertandingan in 
    (SELECT p.id_pertandingan
    FROM Pertandingan p
    JOIN Tim_Pertandingan tp ON p.id_pertandingan = tp.id_pertandingan
    JOIN Stadium s ON s.id_stadium = p.stadium
    JOIN Tim_Manajer tm ON tm.nama_tim = tp.nama_tim
    WHERE tm.id_manajer = '%s')
    GROUP BY s.nama, p.start_datetime, p.id_pertandingan
    """ %(id_manajer))
    context['pertandingan'] = list_tanding
    return render(request, 'list_pertandingan_manajer.html', context=context)


### UNTUK R History_rapat
def history_rapat(request):
    # TODO: Ganti ID Manajer dengan ID manajer login
    id_manajer = "6984f2a7-85e5-4d0d-9d40-79d7469276dd"
    context = {}
    
    hist_rapat = query(f"""SELECT string_agg(tp.nama_tim, ' vs ') as tim, concat(np.nama_depan, ' ' ,np.nama_belakang) as nama_panitia, s.nama, p.start_datetime, p.end_datetime::time as waktuakhir, r.id_pertandingan
    FROM Pertandingan p
    JOIN Rapat r ON p.id_pertandingan = r.id_pertandingan
    JOIN Tim_Pertandingan tp ON p.id_pertandingan = tp.id_pertandingan
    JOIN Stadium s ON s.id_stadium = p.stadium
    JOIN Non_Pemain np ON r.perwakilan_panitia= np.id
    WHERE r.manajer_tim_a in 
    (SELECT r.manajer_tim_a
    FROM Pertandingan p
    JOIN Rapat r ON p.id_pertandingan = r.id_pertandingan
    JOIN Tim_Pertandingan tp ON p.id_pertandingan = tp.id_pertandingan
    JOIN Stadium s ON s.id_stadium = p.stadium
    JOIN Non_Pemain np ON r.perwakilan_panitia= np.id
    WHERE r.manajer_tim_a = '%s' ) OR 
    r.manajer_tim_b in 
    (SELECT r.manajer_tim_b
    FROM Pertandingan p
    JOIN Rapat r ON p.id_pertandingan = r.id_pertandingan
    JOIN Tim_Pertandingan tp ON p.id_pertandingan = tp.id_pertandingan
    JOIN Stadium s ON s.id_stadium = p.stadium
    JOIN Non_Pemain np ON r.perwakilan_panitia= np.id
    WHERE r.manajer_tim_b = '%s' )
    GROUP BY s.nama, p.start_datetime, r.id_pertandingan, np.nama_depan, np.nama_belakang, waktuakhir
    """ %(id_manajer, id_manajer))
    context['rapat'] = hist_rapat
    return render(request, 'history_rapat.html', context=context)

def notulensi(request, id):
    context = {}
    notul = query(f"""SELECT isi_rapat
    FROM Rapat
    WHERE id_pertandingan = '%s'
    """ %(id))
    context['notul'] = notul
    return render(request, 'notulensi_rapat.html', context)
