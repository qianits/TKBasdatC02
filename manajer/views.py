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

def dashboard_manajer(request):
    username = request.session.get('username')
    print("masuk")
    print(username)

    db_connection = psycopg2.connect(
            host="localhost",
            database="postgres",
            user="postgres",
            password="123"
        )
    
    cursor = db_connection.cursor()
    cursor.execute("set search_path to ULeague")

    # Untuk Informasi
    print(username)
    informasi = get_informasi(cursor, username)
    status = get_status(cursor,informasi[0][0]) 
    nama_tim = get_tim(cursor,informasi[0][0]) 

    db_connection.commit()
    db_connection.close()  

    nama = informasi[0][1] + " " + informasi[0][2]
    email = informasi[0][4]
    no_hp = informasi[0][3]
    alamat = informasi[0][5]

    return render(request, 'dashboard_manajer.html',{'nama':nama, 'email':email, 'no_hp':no_hp, 'alamat':alamat, 'status':status, 'nama_tim':nama_tim})


# Untuk mencari seluruh informasi user
def get_informasi(cursor, username: str):

    # Mencari ID
    query_get_ID = """select ID_Manajer from MANAJER 
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

def get_tim(cursor, id: str):
    query_get_status = """select Nama_Tim from TIM_MANAJER 
    where ID_Manajer = %s
    """
    cursor.execute(query_get_status,(id,))
    results = cursor.fetchall()
    if len(results) == 0:
        return "Belum membuat tim"
    else:
        return results[0][0]

def read_peminjaman_stadium():
    return

def crt_peminjaman_stadium():
    return

def del_peminjaman_stadium():
    return

#Bagian Mengelola Tim
def registrasi_tim(request):
    if request.method == 'POST':
        nama_tim = request.POST['nama_tim']
        universitas = request.POST['universitas']
        Tim.objects.create(nama_tim=nama_tim, universitas=universitas)
        return redirect('daftar_tim')

    return render(request, 'registrasi_tim.html')

# def daftar_tim(request):
#     tim_list = Tim.objects.all()
#     return render(request, 'daftar_tim.html', {'tim_list': tim_list})

def daftar_pemain(request, tim_id):
    tim = Tim.objects.get(id=tim_id)
    pemain_list = tim.pemain.all()
    return render(request, {'tim': tim, 'pemain_list': pemain_list})

def daftar_pelatih(request, tim_id):
    tim = Tim.objects.get(id=tim_id)
    pelatih_list = tim.pelatih.all()
    return render(request, {'tim': tim, 'pelatih_list': pelatih_list})

def tambah_pemain(request, tim_id):
    if request.method == 'POST':
        pemain_id = request.POST['pemain_id']
        pemain = Pemain.objects.get(id=pemain_id)
        pemain.tim_id = tim_id
        pemain.save()
        return redirect('daftar_pemain', tim_id=tim_id)

    pemain_tersedia = Pemain.objects.filter(tim__isnull=True)
    return render(request,{'pemain_tersedia': pemain_tersedia})

def tambah_pelatih(request, tim_id):
    if request.method == 'POST':
        pelatih_id = request.POST['pelatih_id']
        pelatih = Pelatih.objects.get(id=pelatih_id)
        pelatih.tim_id = tim_id
        pelatih.save()
        return redirect('daftar_pelatih', tim_id=tim_id)

    pelatih_tersedia = Pelatih.objects.filter(tim__isnull=True)
    return render(request, {'pelatih_tersedia': pelatih_tersedia})

def hapus_pemain(request, tim_id, pemain_id):
    tim = get_object_or_404(Tim, id=tim_id)
    pemain = get_object_or_404(Pemain, id=pemain_id, tim=tim)
    pemain.tim = None
    pemain.save()
    return redirect('daftar_pemain', tim_id=tim_id)

def hapus_pelatih(request, tim_id, pelatih_id):
    tim = get_object_or_404(Tim, id=tim_id)
    pelatih = get_object_or_404(Pelatih, id=pelatih_id, tim=tim)
    pelatih.tim = None
    pelatih.save()
    return redirect('daftar_pelatih', tim_id=tim_id)

def make_captain(request, tim_id, pemain_id):
    tim = get_object_or_404(Tim, id=tim_id)
    pemain = get_object_or_404(Pemain, id=pemain_id, tim=tim)
    tim.pemain_set.update(is_captain=False)
    pemain.is_captain = True
    pemain.save()
    
    return redirect('daftar_pemain', tim_id=tim_id)

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
    id_manajer = "6984f2a7-85e5-4d0d-9d40-79d7469276dd"
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

def notulensi(request, id):
    context = {}
    db_connection = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="qistina",
        password="Qistina04"
    )
    cursor = db_connection.cursor()
    cursor.execute("set search_path to uleague")
    notul = get_notul(cursor, id)
    context['notul'] = notul
    db_connection.close()
    return render(request, 'notulensi_rapat.html', context)

def get_notul(cursor, id):
    query_get_list = """
    SELECT isi_rapat
    FROM Rapat
    WHERE id_pertandingan = %s
    """
    selected_notul = cursor.execute(query_get_list,(id,))
    selected_notul = cursor.fetchall()
    return selected_notul
