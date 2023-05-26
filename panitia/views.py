from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
import psycopg2
from django.db import connection
from utils.query import *

def dashboard_panitia(request):
    username = request.session.get('username')

    context = {}

    # Untuk Informasi
    informasi = get_informasi(username) 
    status = get_status(informasi[0]['id'])   
    info_rapat = get_rapat(informasi[0]['id'])
    jabatan = get_jabatan(informasi[0]['id'])
    print("jabatan")
    jabatan_tup  = tuple(d['jabatan'] for d in jabatan)
    print(jabatan_tup)


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
    resultsss = [jabatan_tup + tuple_item for tuple_item in tuple_data]

    context['data'] = resultsss
    # [('74359555-b3d7-4c97-b70f-5843e3ca1f4b', 'Bastien Cansfield', '088984639510', 'bcansfield14@patch.com', '45 Florence Hill', 'Panitia, Tendik')]
    

    if info_rapat != None:
        print("MASUK IF")
        print(resultsss)

        list_of_id_pertandingan = [item['id_pertandingan'] for item in info_rapat]
        list_of_datetime = [item['datetime'] for item in info_rapat]
        list_of_isi_rapat = [item['isi_rapat'] for item in info_rapat]
    
        # Manajer tim A
        temps_tim_1 = [item['manajer_tim_a'] for item in info_rapat]
        list_of_tim_manajer_1 = []
        for id in temps_tim_1:
            temp = get_list_of_tim_manajer(id)
            list_of_tim_manajer_1.append(temp)
        list_of_tim_manajer_1 = list_of_tim_manajer_1[0]

        # Manajer tim B
        temps_tim_2 = [item['manajer_tim_b'] for item in info_rapat]
        list_of_tim_manajer_2 = []
        for id in temps_tim_2:
            temp = get_list_of_tim_manajer(id)
            list_of_tim_manajer_2.append(temp)
        list_of_tim_manajer_2 = list_of_tim_manajer_2[0]

        print("==============")
        print(list_of_id_pertandingan)
        print(list_of_datetime)
        print(list_of_isi_rapat)
        print(list_of_tim_manajer_1)
        print(list_of_tim_manajer_2)

        results = list(zip(list_of_id_pertandingan, list_of_datetime, list_of_isi_rapat, list_of_tim_manajer_1, list_of_tim_manajer_2))
        context['data_rapat'] = results
        print(results)
        print(tuple_data)

        return render(request, 'dashboard_panitia.html',context=context)

    else:
        return render(request, 'dashboard_panitia.html',context=context)


# Untuk mencari seluruh informasi user
def get_informasi(username: str):
    # Mencari ID
    get_id = query(f"""select ID_panitia from PANITIA 
    where username = '%s'
    """ %(username))
    id_dict = get_id[0]
    
    # Mencari data berdasarkan ID
    get_data = query(f"""select * from NON_PEMAIN 
    where ID = '%s'
    """%(id_dict["id_panitia"]))
    return get_data

def get_status(id: str):
    get_status = query(f"""select status from STATUS_NON_PEMAIN 
    where ID_Non_Pemain = '%s'
    """ %(id))
    return get_status

def get_jabatan(id: str):
    get_jabatan = query(f"""select jabatan from PANITIA 
    where ID_Panitia = '%s'
    """ %(id))
    return get_jabatan

def get_rapat(id: str):
    get_data_rapat = query(f"""select * from RAPAT 
    where PERWAKILAN_PANITIA = '%s'
    """ %(id))

    if len(get_data_rapat) == 0:
        return None
    
    return get_data_rapat

def get_list_of_tim_manajer(id: str):
    get_tim = query(f"""select Nama_Tim from TIM_MANAJER 
    where ID_Manajer = '%s'
    """ %(id))

    get_manajer = query(f"""select Nama_Depan || ' ' || Nama_Belakang AS Nama_Lengkap from NON_PEMAIN 
    where ID = '%s'
    """ %(id))

    result = [(list(d1.values())[0], list(d2.values())[0]) for d1, d2 in zip(get_tim, get_manajer)]
    return result

def query(query_str: str):
    hasil = []
    with connection.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SET SEARCH_PATH TO ULEAGUE")
        try:
            cursor.execute(query_str)

            if query_str.strip().lower().startswith("select"):
                # Kalau ga error, return hasil SELECT
                hasil = map_cursor(cursor)
            else:
                # Kalau ga error, return jumlah row yang termodifikasi oleh INSERT, UPDATE, DELETE
                hasil = cursor.rowcount
        except Exception as e:
            # Ga tau error apa
            hasil = e
    return hasil


def panitia_memulai_pertandingan(request, id):
    # print(id)
    id='01b0dec5-48b3-44d9-b1dd-b9903c33b1ff'
    context = {}
    # db_connection = psycopg2.connect(
    #     host="localhost",
    #     database="postgres",
    #     user="postgres",
    #     password="123"
    # )
    # cursor = db_connection.cursor()
    # cursor.execute("set search_path to uleague")
    tim_pertandingan = get_pertandingan(id)
    # print(tim_pertandingan[1]['nama_tim'])
    peristiwa = get_peristiwa(id)
    pemain1 = get_pemain(tim_pertandingan[0]['nama_tim'])
    pemain2 = get_pemain(tim_pertandingan[1]['nama_tim'])
    context['tim_pertandingan'] = tim_pertandingan
    context['peristiwa'] = peristiwa
    context['tim1'] = pemain1
    context['tim2'] = pemain2
    # db_connection.close()
    # print(pemain2)
    
    if (request.method == 'POST'):
        pelaku1 = request.POST.get('pelaku1')
        peristiwa1 = request.POST.get('peristiwa1')
        id_pemain = query(f"""SELECT ID_Pemain
        FROM Pemain
        WHERE CONCAT(Nama_Depan, ' ', Nama_Belakang) = '%s'""" %(pelaku1))
        query(f"""INSERT INTO peristiwa (id_pertandingan, datetime, jenis, id_pemain) VALUES 
        (%s, CURRENT_TIMESTAMP, %s,  %s) """ %(id, pelaku1, peristiwa1, id_pemain))
        
    return render(request, 'mulai_pertandingan.html', context=context)


def get_peristiwa( id: str):
    results = query(f"""SELECT *
    FROM Peristiwa
    WHERE id_pertandingan = '%s'
    """ %(id))
    # cursor.execute(query_get_jabatan,(id,))
    # results = cursor.fetchall()
    return results

def get_pertandingan( id: str):
    results = query(f"""SELECT tp.ID_Pertandingan, tb.Nama_Tim 
    FROM TIM_PERTANDINGAN tp
    JOIN TIM tb ON tp.Nama_Tim = tb.Nama_Tim
    WHERE tp.ID_pertandingan = '%s'
    """ %(id))
    # cursor.execute(query_get_jabatan,(id,))
    # results = cursor.fetchall()
    # print(results)
    return results

def get_pemain( tim1: str):
    results = query(f"""SELECT ID_pemain, nama_depan, nama_belakang 
    FROM Pemain p
    WHERE p.nama_tim = '%s'
    """ %(tim1))
    # cursor.execute(query_get_jabatan,(tim1,))
    # results = cursor.fetchall()
    # print(results)
    return results


def panitia_manage_pertandingan(request):
    context = {}
    db_connection = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password="123"
    )
    cursor = db_connection.cursor()
    cursor.execute("set search_path to uleague")
    list_skor = get_list_skor(cursor)
    list_pertandingan = get_list_pertandingan(cursor)
    context['pertandingan'] = list_pertandingan
    context['hasil_akhir'] = list_skor
    context['grup'] = [['Grup A',[]], ['Grup B',[]], ['Grup C',[]], ['Grup D',[]]]
    pointer = 0
    # print(len(context['pertandingan']))
    # print((context['pertandingan']))

    for pertandingan in context['pertandingan']:
        if len(context['grup'][pointer][1]) == 4:
            pointer += 1
        context['grup'][pointer][1] += [pertandingan]

    print(context['grup'])
    db_connection.close()
    return render(request, 'manage_pertandingan.html', context=context)

def get_list_skor(cursor):
    query_get_list = """
    SELECT
    p.id_pertandingan,
    tp.nama_tim AS tim,
    tp.skor
    FROM
    Pertandingan p
    JOIN Tim_Pertandingan tp ON p.id_pertandingan = tp.id_pertandingan
    WHERE
    tp.skor = (
        SELECT MAX(skor)
        FROM Tim_Pertandingan
        WHERE id_pertandingan = p.id_pertandingan
    );

    """
    list_skor = cursor.execute(query_get_list,)
    list_skor = cursor.fetchall()
    # print(list_skor)
    return list_skor

def get_list_pertandingan(cursor):
    query_get_list = """
    SELECT string_agg(tp.nama_tim, ' vs ') as tim, s.nama, p.start_datetime, p.end_datetime::time as waktuakhir, p.id_pertandingan
    FROM Pertandingan p
    JOIN Tim_Pertandingan tp ON p.id_pertandingan = tp.id_pertandingan
    JOIN Stadium s ON s.id_stadium = p.stadium
    GROUP BY s.nama, p.start_datetime, p.id_pertandingan
    ORDER BY p.start_datetime
    """
    list_pertandingan = cursor.execute(query_get_list,)
    list_pertandingan = cursor.fetchall()
    # print(list_pertandingan)
    return list_pertandingan

def crt_mulai_rapat():
    return

def read_mulai_rapat():
    return
def daftar_pertandingan(request):
    pertandingan = Rapat.objects.all()
    context = {'pertandingan': pertandingan}
    return render(request, 'rapat_pertandingan.html', context)
def pertandingan_list(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT p.id_pertandingan, t1.nama_tim, t2.nama_tim, s.nama, p.start_datetime, p.end_datetime FROM pertandingan p JOIN tim t1 ON t1.nama_tim = p.nama_tim_a JOIN tim t2 ON t2.nama_tim = p.nama_tim_b JOIN stadium s ON s.id_stadium = p.stadium")
        pertandingan_list = cursor.fetchall()

    return render(request, 'rapat_pertandingan.html', {'pertandingan_list': pertandingan_list})

def rapat_form(request, id_pertandingan):
    if request.method == 'POST':
        isi_rapat = request.POST.get('isi_rapat')

        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO rapat (id_pertandingan, isi_rapat) VALUES (%s, %s)", [id_pertandingan, isi_rapat])

        return redirect('dashboard_panitia')

    return render(request, 'mulai_rapat.html', {'id_pertandingan': id_pertandingan})
