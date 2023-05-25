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