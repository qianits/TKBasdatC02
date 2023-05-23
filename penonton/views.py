from django.shortcuts import render
import psycopg2

def dashboard_penonton(request):
    username = request.session.get('username')
    
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
        tim_bertanding = get_tim_bertanding(cursor, info_pertandingan[0][0]) 
        tim_1 = tim_bertanding[0][0]
        tim_2 = tim_bertanding[1][0]
        tim_bertanding = tim_1 + " vs " + tim_2

        nama_stadion = get_nama_stadion(cursor, info_pertandingan[0][3])
        nama_stadion = nama_stadion[0][0]

        start_time = info_pertandingan[0][1]
        end_time = info_pertandingan[0][2]

        db_connection.commit()
        db_connection.close()
        

        return render(request, 'dashboard_penonton.html',{'nama':nama, 'email':email, 'no_hp':no_hp, 'alamat':alamat, 'status':status, 'tim_bertanding':tim_bertanding,
                                                        'stadium':nama_stadion, 'start':start_time, 'end':end_time})

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

    print(data)

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
