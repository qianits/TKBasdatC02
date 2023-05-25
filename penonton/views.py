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
    username = request.session.get('username')
    print("masuk")
    
    # Ini sesuain sama local postgresql lu
    db_connection = psycopg2.connect(
            host="localhost",
            database="postgres",
            user="postgres",
            password="123"
        )

    cursor = db_connection.cursor()
    cursor.execute("set search_path to ULeague")

    # Untuk Informasi
    informasi = get_informasi(cursor, username) 
    status = get_status(cursor,informasi[0][0])   
    info_pertandingan = get_pertandingan(cursor,[informasi[0][0]])

    nama = informasi[0][1] + " " + informasi[0][2]
    email = informasi[0][4]
    no_hp = informasi[0][3]
    alamat = informasi[0][5]

    if info_pertandingan != None:
        list_of_id_pertandingan = [x[0] for x in info_pertandingan]
        list_of_id_stadium = [x[3] for x in info_pertandingan]
        
        list_of_tim_pertandingan = [] # ['UIFC vs IPB Warriors', 'a vs b']
        for id in list_of_id_pertandingan:
            temp = get_tim_bertanding(cursor,id)
            temp2 = [item[0] for item in temp]
            temp3 = " vs ".join(temp2) 
            list_of_tim_pertandingan.append(temp3)
        
        list_of_nama_stadion = []
        for id in list_of_id_stadium:
            temp = get_nama_stadion(cursor,id)
            temp2 = [item[0] for item in temp]
            list_of_nama_stadion.append(temp2)
        
        list_start_date = [x[1] for x in info_pertandingan]
        list_end_date = [x[2] for x in info_pertandingan]

        # ubah ke tupple dulu
        tup1 = [(item,) for item in list_of_tim_pertandingan]
        tup3 = [(item,) for item in list_start_date]
        tup4 = [(item,) for item in list_end_date]

        data = list(zip(tup1, list_of_nama_stadion, tup3, tup4))


        db_connection.commit()
        db_connection.close()
        

        return render(request, 'dashboard_penonton.html',{'nama':nama, 'email':email, 'no_hp':no_hp, 'alamat':alamat, 'status':status, 
                                                           'data':data})

    else:
        db_connection.commit()
        db_connection.close()
        return render(request, 'dashboard_penonton.html',{'nama':nama, 'email':email, 'no_hp':no_hp, 'alamat':alamat, 'status':status})

# Untuk mencari seluruh informasi user
def get_informasi(cursor, username: str):

    # Mencari ID
    query_get_ID = """select ID_Penonton from PENONTON 
    where username = %s
    """
    cursor.execute(query_get_ID,(username,))
    ID = cursor.fetchall()
    ID = ID[0][0]
    
    # Mencari data berdasarkan ID
    query_get_data = """select * from NON_PEMAIN 
    where ID = %s
    """
    cursor.execute(query_get_data,(ID,))
    result = cursor.fetchall()
    
    return result

def get_status(cursor, id: str):
    query_get_status = """select status from STATUS_NON_PEMAIN 
    where ID_Non_Pemain = %s
    """
    cursor.execute(query_get_status,(id,))
    results = cursor.fetchall()
    return results[0][0]

def get_pertandingan(cursor, id: str):
    query_get_id_pertandingan = """select ID_Pertandingan from PEMBELIAN_TIKET 
    where ID_Penonton = %s
    """
    cursor.execute(query_get_id_pertandingan,(id[0],))
    id_pertandingan = cursor.fetchall()
    

    if len(id_pertandingan) == 0:
        return None
    

    query_get_data_pertandingan = """select * from PERTANDINGAN 
    where ID_Pertandingan = %s
    """
    cursor.execute(query_get_data_pertandingan,(id_pertandingan))
    data = cursor.fetchall()


    return data

def get_tim_bertanding(cursor, id: str):
    query_get_tim_bertanding = """select Nama_Tim from TIM_PERTANDINGAN 
    where ID_Pertandingan = %s
    """
    cursor.execute(query_get_tim_bertanding,(id,))
    tim_bertanding = cursor.fetchall()
    
    return tim_bertanding
    
def get_nama_stadion(cursor, id: str):
    query_get_stadium = """select nama from STADIUM 
    where id_stadium = %s
    """
    cursor.execute(query_get_stadium,(id,))
    nama_stadium = cursor.fetchall()
    
    return nama_stadium

def pembelian_tiket(request):
    return render(request, 'pembelian_tiket.html')
  
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
