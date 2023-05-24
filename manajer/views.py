from django.shortcuts import render
import psycopg2

def dashboard_manajer(request):
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