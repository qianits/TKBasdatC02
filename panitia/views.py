from django.shortcuts import render
import psycopg2



def dashboard_panitia(request):
    username = request.session.get('username')

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
    info_rapat = get_rapat(cursor,[informasi[0][0]])
    jabatan = get_jabatan(cursor, informasi[0][0])

    nama = informasi[0][1] + " " + informasi[0][2]
    email = informasi[0][4]
    no_hp = informasi[0][3]
    alamat = informasi[0][5]
    

    if info_rapat != None:

        print(info_rapat)
        list_of_id_pertandingan = [x[0] for x in info_rapat]
        list_of_datetime = [x[1] for x in info_rapat]
        list_of_isi_rapat = [x[5] for x in info_rapat]

        print(list_of_id_pertandingan)
        
    

        temps_tim_1 = [x[3] for x in info_rapat]
        list_of_tim_manajer_1 = []
        for id in temps_tim_1:
            temp = get_list_of_tim_manajer(cursor,id)
            list_of_tim_manajer_1.append(temp)

        temps_tim_2 = [x[4] for x in info_rapat]
        list_of_tim_manajer_2 = []
        for id in temps_tim_2:
            temp = get_list_of_tim_manajer(cursor,id)
            list_of_tim_manajer_2.append(temp)
    
        db_connection.commit()
        db_connection.close()

        tup1 = [(item,) for item in list_of_id_pertandingan]
        tup2 = [(item,) for item in list_of_datetime]
        tup3 = [(item,) for item in list_of_isi_rapat]

        print(tup1)

        data = list(zip(tup1, tup2, list_of_tim_manajer_1, list_of_tim_manajer_2, tup3))

        return render(request, 'dashboard_panitia.html',{'nama':nama, 'email':email, 'no_hp':no_hp, 'alamat':alamat, 'status':status, 'jabatan':jabatan
                                                         , 'list_of_id_pertandingan':list_of_id_pertandingan, 'data':data})

    else:
        db_connection.commit()
        db_connection.close()
        return render(request, 'dashboard_panitia.html',{'nama':nama, 'email':email, 'no_hp':no_hp, 'alamat':alamat, 'status':status, 'jabatan':jabatan})


# Untuk mencari seluruh informasi user
def get_informasi(cursor, username: str):

    # Mencari ID
    query_get_ID = """select ID_panitia from PANITIA 
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

def get_jabatan(cursor, id: str):
    query_get_jabatan = """select jabatan from PANITIA 
    where ID_Panitia = %s
    """
    cursor.execute(query_get_jabatan,(id,))
    results = cursor.fetchall()
    return results[0][0]

def get_rapat(cursor, id: str):
    query_get_data_rapat = """select * from RAPAT 
    where PERWAKILAN_PANITIA = %s
    """
    cursor.execute(query_get_data_rapat,(id[0],))
    data_rapat = cursor.fetchall()

    if len(data_rapat) == 0:
        return None
    
    return data_rapat

def get_list_of_tim_manajer(cursor, id: str):
    query_get_tim = """select Nama_Tim from TIM_MANAJER 
    where ID_Manajer = %s
    """
    cursor.execute(query_get_tim,(id,))
    tim = cursor.fetchall()

    query_get_manajer = """select Nama_Depan || ' ' || Nama_Belakang AS Nama_Lengkap from NON_PEMAIN 
    where ID = %s
    """
    cursor.execute(query_get_manajer,(id,))
    nama_manajer = cursor.fetchall()

    tim_manajer = (tim[0][0], nama_manajer[0][0])
    
    return tim_manajer

def panitia_memulai_pertandingan(request):
    context = {}
    db_connection = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password="123"
    )
    cursor = db_connection.cursor()
    cursor.execute("set search_path to uleague")
    list_pertandingan = get_list_pertandingan(cursor)
    context['pertandingan'] = list_pertandingan
    db_connection.close()
    return render(request, 'mulai_pertandingan.html', context=context)



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
    list_pertandingan = get_list_skor(cursor)
    list_pertandingan = get_list_pertandingan(cursor)
    context['pertandingan'] = list_pertandingan
    context['hasil_akhir'] = list_pertandingan
    context['grup'] = [('Grup A'), ('Grup B'), ('Grup C'), ('Grup D')]

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
    print(list_skor)
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
    print(list_pertandingan)
    return list_pertandingan

def crt_mulai_rapat():
    return

def read_mulai_rapat():
    return
