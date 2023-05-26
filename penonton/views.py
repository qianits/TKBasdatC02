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
    username = request.session.get('username')

    context = {}
    # Untuk Informasi
    informasi = get_informasi(username) # [{'id': 'e2d58d08-5036-46b9-8815-71566405ddfc', 'nama_depan': 'Enrico', 'nama_belakang': 'Dumigan', 'nomor_hp': '083835531812', 'email': 'edumigank@newsvine.com', 'alamat': '7 Stoughton Hill'}]
    status = get_status(informasi[0]['id'])  # [{'id_pertandingan': '01b0dec5-48b3-44d9-b1dd-b9903c33b1ff', 'start_datetime': datetime.datetime(2023, 4, 1, 18, 30), 'end_datetime': datetime.datetime(2023, 4, 1, 21, 30), 'stadium': '74d109b4-94d9-4632-b48b-a7cc96382ddf'}]
    info_pertandingan = get_pertandingan([informasi[0]['id']])

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

    if info_pertandingan != None:
        print("Masuk if")
        # get nama tim bertanding
        tim_bertanding = []
        for item in info_pertandingan:
            nama_tim_bertanding = get_tim_bertanding(info_pertandingan[0]['id_pertandingan'])
            tim_bertanding += nama_tim_bertanding
        
        #get nama stadium
        stadium = []
        for item in info_pertandingan:
            nama_stadion = get_nama_stadion(info_pertandingan[0]['stadium'])
            stadium += nama_stadion

        info_pertandingan_new = []
        for item in info_pertandingan:
            tuple_values = tuple(item.values())
            info_pertandingan_new.append(tuple_values)
        

        # Info pertandingan fix banget
        info_fix = [tuple(sum(items, ())) for items in zip(tim_bertanding, stadium, info_pertandingan_new)]


        
        context['data_pertandingan'] = info_fix
        print(info_pertandingan_new)
        print(tuple_data) #[('e2d58d08-5036-46b9-8815-71566405ddfc', 'Enrico Dumigan', '083835531812', 'edumigank@newsvine.com', '7 Stoughton Hill', 'Penonton, Dosen')]
        print(info_fix)
        return render(request, 'dashboard_penonton.html',context=context)

    else:
        return render(request, 'dashboard_penonton.html',context=context)

# Untuk mencari seluruh informasi user
def get_informasi(username: str):

    # Mencari ID
    get_id = query(f"""select ID_Penonton from PENONTON 
    where username = '%s'
    """ %(username))
    id_dict = get_id[0]
    
    # Mencari data berdasarkan ID
    get_data = query(f"""select * from NON_PEMAIN 
    where ID = '%s'
    """%(id_dict["id_penonton"]))
    
    return get_data

def get_status(id: str):
    get_status = query(f"""select status from STATUS_NON_PEMAIN 
    where ID_Non_Pemain = '%s'
    """ %(id))
    return get_status


def get_pertandingan(id: str):
    get_id_pertandingan = query(f"""select ID_Pertandingan from PEMBELIAN_TIKET 
    where ID_Penonton = '%s'
    """ %(id[0]))

    if len(get_id_pertandingan) == 0:
        return None
    
    # Eliminasi data duplikat
    unique_id = set(item['id_pertandingan'] for item in get_id_pertandingan)
    
    result = []
    # loop through unique id
    for item in unique_id:
        get_data_pertandingan = query(f"""select * from PERTANDINGAN 
        where ID_Pertandingan = '%s'
        """ %(item))
        result.extend(get_data_pertandingan)

    return get_data_pertandingan

def get_tim_bertanding(id: str):
    get_tim_bertanding = query(f"""select Nama_Tim from TIM_PERTANDINGAN 
    where ID_Pertandingan = '%s'
    """ %(id))

    result = []
    for item in get_tim_bertanding:
        nama_tim = item['nama_tim']
        result.append(nama_tim)

    final_result = [(', '.join(result[:-1]) + ' vs ' + result[-1]),]

    final_result = [(final_result[0],)]
    print(final_result)
    return final_result
    
def get_nama_stadion(id: str):
    get_stadium = query(f"""select nama from STADIUM 
    where id_stadium = '%s'
    """ %(id))

    result = [(item['nama'],) for item in get_stadium]
    
    print(result)
    return result

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