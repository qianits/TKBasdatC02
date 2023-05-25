from django.shortcuts import redirect, render
from django.contrib import messages
import psycopg2
import locale
import uuid
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse
from utils.query import *
locale.setlocale(locale.LC_ALL, '')

from penonton.models import *

def dashboard_penonton(request):
    return render(request, 'dashboard_penonton.html')

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

### UNTUK CR Pembelian_Tiket
def pembelian_tiket(request):
    context ={}
    stadiums = query("select * from stadium")
    context['stadiums'] = stadiums
    if (request.method == 'POST'):
        nama_stadium = request.POST.get('nama_stadium')
        selected_date = request.POST.get('date')
        StadiumTemp.objects.create(nama_stadium=nama_stadium, tanggal=selected_date)
        return HttpResponseRedirect(reverse("penonton:pilih_pertandingan")) 
    return render(request, 'pembelian_tiket.html', context=context)

def pilih_pertandingan(request):
    stadium_temps = StadiumTemp.objects.all()
    tanggal_list = [stadium_temp.tanggal for stadium_temp in stadium_temps]
    stadium_list = [stadium_temp.nama_stadium for stadium_temp in stadium_temps]

    context={}
    nilai_var = "Nilai Default"  # Nilai default jika variabel tidak ditemukan dalam POST request
    if request.method == 'POST':
        nilai_var = request.POST.get('nilai_var')  # Mengambil nilai variabel dari POST request

    if len(tanggal_list) > 0:
        selected_date = tanggal_list[-1]
    else:
        selected_date = None  # Atau nilai default yang sesuai

    if len(stadium_list) > 0:
        nama_stadium = stadium_list[-1]
    else:
        nama_stadium = None  # Atau nilai default yang sesuai

    list_waktu_stadium = query("""
    SELECT ut.tim_a, ut.tim_b, ut.nama, ut.waktuawal, ut.waktuakhir, ut.id_pertandingan AS idp
    FROM (
    SELECT tp1.nama_tim as tim_a, tp2.nama_tim as tim_b, s.nama, p.start_datetime::time AS waktuawal, p.end_datetime::time AS waktuakhir, p.id_pertandingan,
    ROW_NUMBER() OVER (PARTITION BY p.id_pertandingan ORDER BY p.start_datetime) AS row_num
    FROM Pertandingan p
    JOIN Tim_Pertandingan tp1 ON p.id_pertandingan = tp1.id_pertandingan
    JOIN Tim_Pertandingan tp2 ON p.id_pertandingan = tp2.id_pertandingan
    JOIN Stadium s ON s.id_stadium = p.stadium
    WHERE tp1.nama_tim <> tp2.nama_tim AND s.nama = '%s' AND TO_CHAR(start_datetime, 'YYYY-MM-DD') LIKE '%s') AS ut
    WHERE row_num = 1
    ORDER BY waktuawal""" %(nama_stadium, selected_date))
    context = {"waktu" : list_waktu_stadium,
                "nama_stadium" : nama_stadium,
                'tanggal': selected_date,
                'nilai_var': nilai_var}
    if (request.method == 'POST'):
        id_pertandingan = request.POST.get('id_pertandingan')
        PertandinganTemp.objects.create(id_pertandingan=id_pertandingan)
        return HttpResponseRedirect(reverse("penonton:pilihan_pertandingan")) 
    return render(request, 'pilih_pertandingan.html', context=context)

def beli_tiket(request, id):
    context = {'tiket': ['VIP', 'Main East', 'Kategori 1', 'Kategori 2'],
                'pembayaran': ['E-Wallet', 'Transfer Bank'],
                'id': id }
    if (request.method == 'POST'):
        jenis_pembayaran = request.POST.get('jenis_pembayaran')
        jenis_tiket = request.POST.get('jenis_tiket')
        # TODO: GANTI JD YG LOGIN & kalo make local error
        receipt = str(uuid.uuid4())
        jenis_pembayaran = request.POST.get('jenis_pembayaran')
        jenis_tiket = request.POST.get('jenis_tiket')
        id_pertandingan = str(id)
        id_penonton = "e2d58d08-5036-46b9-8815-71566405ddfc"
        query(f"""INSERT INTO PEMBELIAN_TIKET (Nomor_Receipt, ID_Penonton, Jenis_Tiket, Jenis_Pembayaran, ID_Pertandingan) VALUES 
        (%s, %s, %s, %s, %s) """ %(receipt, id_penonton, jenis_tiket, jenis_pembayaran, id_pertandingan))
        return HttpResponseRedirect(reverse("penonton:dashboard")) 
    return render(request, 'beli_tiket.html', context=context)

### UNTUK R LIST PERTANDINGAN
def list_pertandingan(request):
    context = {}
    list_tanding = query("""
    SELECT string_agg(tp.nama_tim, ' vs ') as tim, s.nama, p.start_datetime, p.end_datetime::time as waktuakhir,  p.id_pertandingan
    FROM Pertandingan p
    JOIN Tim_Pertandingan tp ON p.id_pertandingan = tp.id_pertandingan
    JOIN Stadium s ON s.id_stadium = p.stadium
    GROUP BY s.nama, p.start_datetime, p.id_pertandingan
    ORDER BY p.start_datetime
    """)
    context['pertandingan'] = list_tanding
    return render(request, 'list_pertandingan.html', context=context)