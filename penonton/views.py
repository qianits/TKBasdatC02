from django.shortcuts import redirect, render
from django.contrib import messages
import psycopg2
import locale
import uuid
locale.setlocale(locale.LC_ALL, '')
from django.http import JsonResponse

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
    if request.method == 'POST':
        id_stadium = request.POST.get('stadium')
        selected_date = request.POST.get('date')
        # TODO: something with the stadium ID and selected date
        return render(request, 'list_waktu_stadium.html', {'id_stadium': id_stadium, 'selected_date': selected_date})
    return render(request, 'pembelian_tiket.html', context=context)

def list_waktu_stadium(id_stadium, request):
    db_connection = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="qistina",
        password="Qistina04"
    )
    cursor = db_connection.cursor()

    id_stadium = request.GET.get('id_stadium')
    selected_date = request.GET.get('selected_date')
    return render(request, 'list_waktu_stadium.html')

def get_waktu_stadium(id_stadium,  cursor):
    # TODO : Selected date
    query_get_waktu = """ SELECT start_datetime, end_datetime
    FROM pertandingan
    JOIN stadium ON stadium.id_stadium = pertandingan.stadium
    WHERE id_stadium = %s
    """
    list_waktu = cursor.execute(query_get_waktu, (id_stadium,))
    list_waktu = cursor.fetchall()
    return list_waktu


