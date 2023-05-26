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
    username = request.session.get('username')
    context = {}

    # Untuk Informasi
    informasi = get_informasi(username) 
    status = get_status(informasi[0]['id']) 
    nama_tim = get_tim(informasi[0]['id']) 

    tes = {}
    for item in status:
        for key, value in item.items():
            if key in tes:
                tes[key] += f", {value}"
            else:
                tes[key] = value
    status = [tes]

    merged_data = []
    merged_data.extend(status)
    merged_data.extend(nama_tim)

    merge_tup = []
    for item in merged_data:
        for key, value in item.items():
            merge_tup.append((value))
    
    merge_tup = [tuple(merge_tup)]


    tuple_data = []
    for item in informasi:
        nama_lengkap = item['nama_depan'] + ' ' + item['nama_belakang']
        tuple_data.append(tuple([item['id'], nama_lengkap, item['nomor_hp'], item['email'], item['alamat']]))

    
    tuple_data = [tuple_data[0] + merge_tup[0]]
    context['data'] = tuple_data

    return render(request, 'dashboard_manajer.html', context=context)


# Untuk mencari seluruh informasi user
def get_informasi(username: str):
    
    # Mencari ID
    get_id = query(f"""select ID_Manajer from MANAJER 
    where username = '%s'
    """ %(username))
    print(get_id)
    id_dict = get_id[0]


    # Mencari data berdasarkan ID
    get_data = query("""select * from NON_PEMAIN 
    where ID = '%s'
    """%(id_dict["id_manajer"]))
    
    return get_data

def get_status(id: str):
    get_status = query("""select status from STATUS_NON_PEMAIN 
    where ID_Non_Pemain = '%s'
    """ %(id))
    
    return get_status

def get_tim(id: str):
    get_tim = query("""select Nama_Tim from TIM_MANAJER 
    where ID_Manajer = '%s'
    """ %(id))

    return get_tim

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

from django.shortcuts import render
from django.db import connection

def peminjaman_stadium(request):
    if request.method == 'POST':
        stadium_id = request.POST.get('stadium_id')
        tanggal = request.POST.get('tanggal')
        waktu_peminjaman = request.POST.get('waktu_peminjaman')

        # Simpan peminjaman ke database
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO Peminjaman (ID_Manajer, Start_Datetime, End_Datetime, ID_Stadium) VALUES (%s, %s, %s, %s)", [manajer_id, waktu_peminjaman, waktu_peminjaman, stadium_id])

        return render(request, 'peminjaman_stadium.html')

    else:
        # Mendapatkan daftar stadium yang telah dipesan
        with connection.cursor() as cursor:
            cursor.execute("SELECT stadium.nama, peminjaman.start_datetime, peminjaman.end_datetime FROM stadium INNER JOIN peminjaman ON stadium.id_stadium = peminjaman.id_stadium")
            result = cursor.fetchall()

        context = {
            'pemesanan': result
        }

        return render(request, 'peminjaman_stadium.html', context)

def pilih_waktu(request, stadium_id, tanggal):
    # Mendapatkan daftar waktu yang tersedia untuk stadium dan tanggal tertentu
    with connection.cursor() as cursor:
        cursor.execute("SELECT waktu FROM waktu_stadium WHERE stadium_id = %s AND tanggal = %s", [stadium_id, tanggal])
        result = cursor.fetchall()

    context = {
        'waktu': result
    }

    return render(request, 'list_waktu_stadium.html', context)