import uuid
from django.shortcuts import redirect, render, reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
import psycopg2
from django.contrib.auth import logout


def authentication(request):
    return render(request, 'login_or_register.html')

@csrf_exempt
def register(request):
    if request.method == 'POST':
        button_value = request.POST.get('button_value')
        if button_value == 'manajer':
            reg_role = 'manajer'
            request.session['reg_role'] = reg_role
            return redirect("authentication:register_manajer_penonton")
        elif button_value == 'penonton':
            reg_role = 'penonton'
            request.session['reg_role'] = reg_role
            return redirect("authentication:register_manajer_penonton")
        elif button_value == 'panitia':
            reg_role = 'panitia'
            request.session['reg_role'] = reg_role
            return redirect("authentication:register_panitia")
    
    return render(request, 'register.html')


def register_manajer_penonton(request):

    if request.method =='POST':
        reg_role = request.session.get('reg_role')
        username = request.POST.get('username')
        password = request.POST.get('password')
        nama_depan = request.POST.get('Nama_Depan')
        nama_belakang = request.POST.get('Nama_Belakang')
        nomor_hp = request.POST.get('Nomor_HP')
        email = request.POST.get('Email')
        alamat = request.POST.get('Alamat')
        status = request.POST.get('drone')
        # Generate UUID
        generated_uuid = uuid.uuid4()
        uuid_string = str(generated_uuid)

        db_connection = psycopg2.connect(
            host="localhost",
            database="postgres",
            user="postgres",
            password="123"
        )

        cursor = db_connection.cursor()
        cursor.execute("set search_path to ULeague")

        if reg_role == 'manajer':
            # Insert manajer:
            # tabel yang terlibat:
            # - User_System
            # - NON_PEMAIN (Generate uuid disini)
            # - STATUS_NON_PEMAIN
            # - Manajer

            try:
                insert_user_system(cursor, username, password)
                insert_non_pemain(cursor, uuid_string, nama_depan, nama_belakang, nomor_hp, email, alamat)
                insert_status_non_pemain(cursor, uuid_string,status)
                insert_manajer(cursor, uuid_string, username)
                
                db_connection.commit()
                db_connection.close()
            except psycopg2.errors.RaiseException as e:
                error_message = str("Username sudah digunakan, mohon ganti username!")
                return render(request, 'register_manajer_penonton.html', {'error': error_message})

            request.session['username'] = username
            return redirect(reverse("manajer:dashboard"), request=request)
        
        elif reg_role == 'penonton':
            # Insert Penonton:
            # tabel yang terlibat:
            # - User_System
            # - NON_PEMAIN (Generate uuid disini)
            # - STATUS_NON_PEMAIN
            # - Penonton

            try:
                insert_user_system(cursor, username, password)
                insert_non_pemain(cursor, uuid_string, nama_depan, nama_belakang, nomor_hp, email, alamat)
                insert_status_non_pemain(cursor, uuid_string,status)
                insert_penonton(cursor, uuid_string, username)
                
                db_connection.commit()
                db_connection.close()
            except psycopg2.errors.RaiseException as e:
                error_message = str("Username sudah digunakan, mohon ganti username!")
                return render(request, 'register_manajer_penonton.html', {'error': error_message})

            request.session['username'] = username
            return redirect(reverse("penonton:dashboard"), request=request)

    return render(request, 'register_manajer_penonton.html')
    

def register_panitia(request):
    if request.method =='POST':
        reg_role = request.session.get('reg_role')
        username = request.POST.get('username')
        password = request.POST.get('password')
        nama_depan = request.POST.get('Nama_Depan')
        nama_belakang = request.POST.get('Nama_Belakang')
        nomor_hp = request.POST.get('Nomor_HP')
        email = request.POST.get('Email')
        alamat = request.POST.get('Alamat')
        status = request.POST.get('drone')
        jabatan = request.POST.get('Jabatan')
        # Generate UUID
        generated_uuid = uuid.uuid4()
        uuid_string = str(generated_uuid)

        db_connection = psycopg2.connect(
            host="localhost",
            database="postgres",
            user="postgres",
            password="123"
        )

        cursor = db_connection.cursor()
        cursor.execute("set search_path to ULeague")

        if reg_role == 'panitia':
            # Insert panitia:
            # tabel yang terlibat:
            # - User_System
            # - NON_PEMAIN (Generate uuid disini)
            # - STATUS_NON_PEMAIN
            # - Panitia

            try:
                insert_user_system(cursor, username, password)
                insert_non_pemain(cursor, uuid_string, nama_depan, nama_belakang, nomor_hp, email, alamat)
                insert_status_non_pemain(cursor, uuid_string,status)
                insert_panitia(cursor, uuid_string,jabatan, username)
                
                db_connection.commit()
                db_connection.close()
            except psycopg2.errors.RaiseException as e:
                error_message = str("Username sudah digunakan, mohon ganti username!")
                return render(request, 'register_panitia.html', {'error': error_message})

            request.session['username'] = username
            return redirect(reverse("panitia:dashboard"), request=request)
        
    return render(request, 'register_panitia.html')

def insert_user_system(cursor, username:str, password:str):
    # Insert username & password to USER_SYSTEM
    query_insert_user_system = """INSERT INTO USER_SYSTEM (Username, Password) 
    VALUES (%s,%s)
    """
    cursor.execute(query_insert_user_system,(username, password))

def insert_non_pemain(cursor,uuid_str:str, nama_depan:str, nama_belakang:str, nomor_hp:str, email:str, alamat:str):
    
    # Insert attribute ke tabel non_pemain
    query_insert_non_pemain = """INSERT INTO NON_PEMAIN (ID, Nama_Depan, Nama_Belakang,
    Nomor_HP, Email, Alamat) 
    VALUES (%s,%s,%s,%s,%s,%s)
    """
    cursor.execute(query_insert_non_pemain,(uuid_str,nama_depan,nama_belakang,nomor_hp,email,alamat))
    
def insert_status_non_pemain(cursor,uuid_str:str,status:str):
    # Insert ID dan Role to tabel STATUS_NON_PEMAIN
    query_insert_status = """INSERT INTO STATUS_NON_PEMAIN (ID_Non_Pemain, Status) 
    VALUES (%s,%s)
    """
    cursor.execute(query_insert_status,(uuid_str, status))

def insert_manajer(cursor,uuid_str:str,username:str):
    # Insert ID dan Username to tabel Manajer
    query_insert_manajer = """INSERT INTO MANAJER (ID_Manajer, Username) 
    VALUES (%s,%s)
    """
    cursor.execute(query_insert_manajer,(uuid_str, username))

def insert_penonton(cursor,uuid_str:str,username:str):
    # Insert ID dan Role to tabel Penonton
    query_insert_penonton = """INSERT INTO PENONTON(ID_Penonton, Username) 
    VALUES (%s,%s)
    """
    cursor.execute(query_insert_penonton,(uuid_str, username))

def insert_panitia(cursor,uuid_str:str,jabatan:str,username:str):
    # Insert ID dan Role to tabel Penonton
    query_insert_penonton = """INSERT INTO PANITIA(ID_Panitia, Jabatan, Username) 
    VALUES (%s,%s,%s)
    """
    cursor.execute(query_insert_penonton,(uuid_str,jabatan,username))






# AUTH USING DB

# Untuk mengetahui user terauntetikasi atau tidak
def is_authenticated(request):
    try:
        request.session["username"]
        return True
    except KeyError:
        return False

# Untuk mencari tahu Usernamenya itu masuk role yang mana
def get_role(cursor, username: str, password: str):


    query_check_username_password = """select * from USER_SYSTEM 
    where username = %s AND password = %s
    """
    cursor.execute(query_check_username_password,(username,password))
    result = cursor.fetchall()
    


    # Cari role
    if type(result) == list and len(result):
        # Search query satu persatu dari tiap role untuk mengetahui rolenya

        # Manajer
        manajer_query = """select * from MANAJER 
        where username = %s 
        """
        cursor.execute(manajer_query,(username,))
        result = cursor.fetchall()

        if type(result) == list and len(result):
            return "manajer"


        # Penonton
        penonton_query = """select * from PENONTON 
        where username = %s 
        """
        cursor.execute(penonton_query,(username,))
        result = cursor.fetchall()

        if type(result) == list and len(result):
            return "penonton"


        # Panitia
        panitia_query = """select * from PANITIA 
        where username = %s 
        """
        cursor.execute(panitia_query,(username,))
        result = cursor.fetchall()

        if type(result) == list and len(result):
            return "panitia"

        return result


# Untuk mengambil session data
def get_session_data(request):
    if not is_authenticated(request):
        return {}

    try:
        return {"username": request.session["username"], "role": request.session["role"]}
    except:
        return {}

# Handle User Login (Backend)
@csrf_exempt
def login(request):
    # # next = request.GET.get("next")

    # if request.method != "POST":
    #     return login_view(request)

    if (request.method == 'POST'):
        db_connection = psycopg2.connect(
            host="localhost",
            database="postgres",
            user="postgres",
            password="123"
        )

        cursor = db_connection.cursor()
        cursor.execute("set search_path to ULeague")
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            
            role = get_role(cursor, username,password)
            request.session['role'] = role
            request.session['username'] = username
            

            db_connection.commit()
            db_connection.close()
            # Redirect ke halaman sesuai role (jika berhasil)
            if role == "manajer":
                return redirect(reverse("manajer:dashboard"), request=request)
            elif role == "panitia":
                return redirect(reverse("panitia:dashboard"), request=request)
            elif role == "penonton":
                return redirect(reverse("penonton:dashboard"), request=request)
            else:
                return redirect("authentication:authentication")
            
        except Exception as e:
            db_connection.rollback()
            messages.error(
                request, 'Gagal mendaftar, mohon perika input anda dan coba lagi')
            db_connection.close()
            return redirect('authentication:authentication')


def logout_page(request):
    logout(request)
    request.session.flush()
    return redirect('authentication:authentication')
        

def login_view(request):
    return render(request, "login_or_register.html")


