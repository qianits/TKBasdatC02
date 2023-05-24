from django.shortcuts import redirect, render
from django.contrib import messages
import psycopg2
import locale
import uuid
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse
locale.setlocale(locale.LC_ALL, '')
from django.http import JsonResponse
from manajer.models import *

def dashboard_manajer(request):
    return render(request, 'dashboard_manajer.html')

### UNTUK R List_Pertandingan
# Menampilkan pertandingan-pertandingan timnya
def list_pertandingan(request):
    # TODO: Ganti ID Manajer dengan ID manajer login
    id_manajer = "63ede258-e39c-45b4-b8b8-8de9f8e891bd"
    context = {}
    db_connection = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="qistina",
        password="Qistina04"
    )
    cursor = db_connection.cursor()
    cursor.execute("set search_path to uleague")
    list_tanding = get_list_pertandingan(id_manajer, cursor)
    context['pertandingan'] = list_tanding
    db_connection.close()
    return render(request, 'list_pertandingan.html', context=context)

def get_list_pertandingan(id_manajer, cursor):
    query_get_list = """
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
    WHERE tm.id_manajer = %s)
    GROUP BY s.nama, p.start_datetime, p.id_pertandingan
    """
    list_tanding = cursor.execute(query_get_list, (id_manajer,))
    list_tanding = cursor.fetchall()
    return list_tanding

### UNTUK R History_rapat

def history_rapat(request):
    # TODO: Ganti ID Manajer dengan ID manajer login
    id_manajer = "63ede258-e39c-45b4-b8b8-8de9f8e891bd"
    context = {}
    db_connection = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="qistina",
        password="Qistina04"
    )
    cursor = db_connection.cursor()
    cursor.execute("set search_path to uleague")
    hist_rapat = get_history_rapat(id_manajer, cursor)
    context['rapat'] = hist_rapat
    db_connection.close()
    # if (request.method == 'POST'):
    #     rapat = request.POST.get('rapat')
    #     NotulensiTemp.objects.create(notulensi=rapat)
    #     return HttpResponseRedirect(reverse("manajer:notulensi_rapat")) 
    return render(request, 'history_rapat.html', context=context)

def get_history_rapat(id_manajer, cursor):
    query_get_list = """
    SELECT string_agg(tp.nama_tim, ' vs ') as tim, concat(np.nama_depan, ' ' ,np.nama_belakang) as nama_panitia, s.nama, p.start_datetime, p.end_datetime::time as waktuakhir, r.id_pertandingan
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
    WHERE r.manajer_tim_a = %s) OR 
    r.manajer_tim_b in 
    (SELECT r.manajer_tim_b
    FROM Pertandingan p
    JOIN Rapat r ON p.id_pertandingan = r.id_pertandingan
    JOIN Tim_Pertandingan tp ON p.id_pertandingan = tp.id_pertandingan
    JOIN Stadium s ON s.id_stadium = p.stadium
    JOIN Non_Pemain np ON r.perwakilan_panitia= np.id
    WHERE r.manajer_tim_b = %s)
    GROUP BY s.nama, p.start_datetime, r.id_pertandingan, np.nama_depan, np.nama_belakang, waktuakhir
    """
    list_rapat = cursor.execute(query_get_list, (id_manajer, id_manajer,))
    list_rapat= cursor.fetchall()
    return list_rapat

def notulensi_rapat(request):
    context={}
    # not_temps = NotulensiTemp.objects.all()
    # not_list = [not_temp.notulensi for not_temp in not_temps]

    # if len(not_list) > 0:
    #     selected_not = not_list[-1]
    # else:
    #     selected_not = None  # Atau nilai default yang sesuai
    # context['rapat'] = rapat
    return render(request, 'notulensi_rapat.html')