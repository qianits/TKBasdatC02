from django.shortcuts import redirect, render
from django.contrib import messages
import psycopg2
import locale
import uuid
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse
locale.setlocale(locale.LC_ALL, '')

from penonton.models import *

# TODO: Handle error kalau tidak ada jadwal pertandingan pada hari itu

### UNTUK CR Pembelian_Tiket
def dashboard_penonton(request):
    return render(request, 'dashboard_penonton.html')

def pilih_stadium(request):
    context = {}
    db_connection = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="qistina",
        password="Qistina04"
    )
    cursor = db_connection.cursor()
    
    cursor.execute("set search_path to uleague")
    cursor.execute("select * from stadium")
    stadiums = cursor.fetchall()
    context['stadiums'] = stadiums
    db_connection.close()
    if (request.method == 'POST'):
        nama_stadium = request.POST.get('nama_stadium')
        selected_date = request.POST.get('date')
        StadiumTemp.objects.create(nama_stadium=nama_stadium, tanggal=selected_date)
        return HttpResponseRedirect(reverse("penonton:list_waktu_stadium")) 
    return render(request, 'pembelian_tiket.html', context=context)

def get_waktu_stadium(nama_stadium, selected_date, cursor):
    query_get_waktu = """SELECT TO_CHAR(start_datetime, 'HH:MI') as start, TO_CHAR(end_datetime, 'HH:MI') as end, id_pertandingan
    FROM pertandingan
    JOIN stadium ON stadium.id_stadium = pertandingan.stadium
    WHERE stadium.nama = %s 
    AND TO_CHAR(start_datetime, 'YYYY-MM-DD') LIKE %s
    """
    list_waktu = cursor.execute(query_get_waktu, (nama_stadium, selected_date))
    list_waktu = cursor.fetchall()
    return list_waktu

def list_waktu_stadium(request):
    stadium_temps = StadiumTemp.objects.all()
    tanggal_list = [stadium_temp.tanggal for stadium_temp in stadium_temps]
    stadium_list = [stadium_temp.nama_stadium for stadium_temp in stadium_temps]

    if len(tanggal_list) > 0:
        selected_date = tanggal_list[-1]
    else:
        selected_date = None  # Atau nilai default yang sesuai

    if len(stadium_list) > 0:
        nama_stadium = stadium_list[-1]
    else:
        nama_stadium = None  # Atau nilai default yang sesuai

    context={}
    db_connection = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="qistina",
        password="Qistina04"
    )
    cursor = db_connection.cursor()
    cursor.execute("set search_path to uleague")
    list_waktu_stadium = get_waktu_stadium(nama_stadium, selected_date, cursor)
    context = {"waktu" : list_waktu_stadium,
                "nama_stadium" : nama_stadium}
    db_connection.close()
    if (request.method == 'POST'):
        id_pertandingan = request.POST.get('id_pertandingan')
        PertandinganTemp.objects.create(id_pertandingan=id_pertandingan)
        return HttpResponseRedirect(reverse("penonton:pilihan_pertandingan")) 

    return render(request, 'list_waktu_stadium.html', context=context)

def pilihan_pertandingan(request):

    pertandingan_temps = PertandinganTemp.objects.all()
    pertandingan_list = [pt_temp.id_pertandingan for pt_temp in pertandingan_temps]

    if len(pertandingan_list) > 0:
        selected_pertandingan = pertandingan_list[-1]
    else:
        selected_pertandingan = None  # Atau nilai default yang sesuai

    context={}
    db_connection = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="qistina",
        password="Qistina04"
    )

    cursor = db_connection.cursor()
    cursor.execute("set search_path to uleague")
    list_waktu_stadium = get_waktu_stadium(nama_stadium, selected_date, cursor)

    return context

### UNTUK R LIST PERTANDINGAN
def list_pertandingan(request):
    context = {}
    db_connection = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="qistina",
        password="Qistina04"
    )
    cursor = db_connection.cursor()
    cursor.execute("set search_path to uleague")
    list_tanding = get_list_pertandingan(cursor)
    context['pertandingan'] = list_tanding
    db_connection.close()
    if (request.method == 'POST'):
        rapat = request.POST.get('nama_stadium')
        StadiumTemp.objects.create(nama_stadium=nama_stadium, tanggal=selected_date)
        return HttpResponseRedirect(reverse("penonton:list_waktu_stadium")) 
    return render(request, 'list_pertandingan.html', context=context)

def get_list_pertandingan(cursor):
    query_get_list = """
    SELECT string_agg(tp.nama_tim, ' vs ') as tim, s.nama, p.start_datetime, p.end_datetime::time as waktuakhir, p.id_pertandingan
    FROM Pertandingan p
    JOIN Tim_Pertandingan tp ON p.id_pertandingan = tp.id_pertandingan
    JOIN Stadium s ON s.id_stadium = p.stadium
    GROUP BY s.nama, p.start_datetime, p.id_pertandingan
    ORDER BY p.start_datetime
    """
    list_tanding = cursor.execute(query_get_list,)
    list_tanding = cursor.fetchall()
    return list_tanding