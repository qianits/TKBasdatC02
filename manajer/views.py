from django.shortcuts import render, redirect, get_object_or_404
import psycopg2
from .models import Tim, Pemain, Pelatih

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
    return results[0][0]
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