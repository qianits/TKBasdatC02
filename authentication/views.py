import uuid
from django.shortcuts import redirect, render, reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
import psycopg2
from django.contrib.auth import logout

from utils.query import query


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


        if reg_role == 'manajer':
            # Insert manajer:
            # tabel yang terlibat:
            # - User_System
            # - NON_PEMAIN (Generate uuid disini)
            # - STATUS_NON_PEMAIN
            # - Manajer

            try:
                insert_user_system(username, password)
                insert_non_pemain(uuid_string, nama_depan, nama_belakang, nomor_hp, email, alamat)
                insert_status_non_pemain(uuid_string,status)
                insert_manajer(uuid_string, username)
                
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
                insert_user_system(username, password)
                insert_non_pemain(uuid_string, nama_depan, nama_belakang, nomor_hp, email, alamat)
                insert_status_non_pemain(uuid_string,status)
                insert_penonton(uuid_string, username)
                
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

        if reg_role == 'panitia':
            # Insert panitia:
            # tabel yang terlibat:
            # - User_System
            # - NON_PEMAIN (Generate uuid disini)
            # - STATUS_NON_PEMAIN
            # - Panitia

            try:
                insert_user_system(username, password)
                insert_non_pemain(uuid_string, nama_depan, nama_belakang, nomor_hp, email, alamat)
                insert_status_non_pemain(uuid_string,status)
                insert_panitia(uuid_string,jabatan, username)
                
            except psycopg2.errors.RaiseException as e:
                error_message = str("Username sudah digunakan, mohon ganti username!")
                return render(request, 'register_panitia.html', {'error': error_message})

            request.session['username'] = username
            return redirect(reverse("panitia:dashboard"), request=request)
        
    return render(request, 'register_panitia.html')

def insert_user_system(username:str, password:str):
    # Insert username & password to USER_SYSTEM
    # query(f"""INSERT INTO USER_SYSTEM (Username, Password) 
    # VALUES (%s,%s)
    # """ %(username,password))
    # print("Berhasil insert user_system")
    query(f"""INSERT INTO USER_SYSTEM (Username, Password) 
    VALUES ('{username}', '{password}')
    """)
    print("Berhasil insert user_system")
    

def insert_non_pemain(uuid_str:str, nama_depan:str, nama_belakang:str, nomor_hp:str, email:str, alamat:str):
    
    # Insert attribute ke tabel non_pemain
    query(f"""INSERT INTO NON_PEMAIN (ID, Nama_Depan, Nama_Belakang,
    Nomor_HP, Email, Alamat) 
    VALUES ('{uuid_str}', '{nama_depan}', '{nama_belakang}', '{nomor_hp}', '{email}', '{alamat}')
    """)
    print("Berhasil insert non_pemain")

    
def insert_status_non_pemain(uuid_str:str,status:str):
    # Insert ID dan Role to tabel STATUS_NON_PEMAIN
    query(f"""INSERT INTO STATUS_NON_PEMAIN (ID_Non_Pemain, Status) 
    VALUES ('{uuid_str}', '{status}')
    """)
    print("Berhasil insert status_non_pemain")

def insert_manajer(uuid_str:str,username:str):
    # Insert ID dan Username to tabel Manajer
    query(f"""INSERT INTO MANAJER (ID_Manajer, Username) 
    VALUES ('{uuid_str}', '{username}')
    """ )
    print("Berhasil insert manajer")

def insert_penonton(uuid_str:str,username:str):
    # Insert ID dan Role to tabel Penonton
    query(f"""INSERT INTO PENONTON(ID_Penonton, Username) 
    VALUES ('{uuid_str}', '{username}')
    """)
    print("Berhasil insert penonton")

def insert_panitia(uuid_str:str,jabatan:str,username:str):
    # Insert ID dan Role to tabel Penonton
    query(f"""INSERT INTO PANITIA(ID_Panitia, Jabatan, Username) 
    VALUES ('{uuid_str}', '{jabatan}', '{username}')
    """)


# AUTH USING DB

# Untuk mengetahui user terauntetikasi atau tidak
def is_authenticated(request):
    try:
        request.session["username"]
        return True
    except KeyError:
        return False

# Untuk mencari tahu Usernamenya itu masuk role yang mana
def get_role(username: str, password: str):


    query_check_username_password = query(f"""select * from USER_SYSTEM 
    where username = '%s' AND password = '%s'
    """ %(username,password))
    # Cari role
    if len(query_check_username_password):
        # Search query satu persatu dari tiap role untuk mengetahui rolenya
        
        # Manajer
        manajer_query = query(f"""select * from MANAJER 
        where username = '%s'
        """%(username))

        if len(manajer_query):
            print(type(manajer_query))
            print("Manajer")
            return "manajer"


        # Penonton
        penonton_query = query(f"""select * from PENONTON 
        where username = '%s' 
        """%(username))

        if len(penonton_query):
            print("penonton")
            return "penonton"


        # Panitia
        panitia_query = query(f"""select * from PANITIA 
        where username = '%s' 
        """%(username))

        if len(panitia_query):
            print("panitia")
            return "panitia"

        return query_check_username_password


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

        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            
            role = get_role(username,password)
            request.session['role'] = role
            request.session['username'] = username
            
            print(role)

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
            messages.error(
                request, 'Gagal mendaftar, mohon perika input anda dan coba lagi')
            return redirect('authentication:authentication')


def logout_page(request):
    logout(request)
    request.session.flush()
    return redirect('authentication:authentication')
        

def login_view(request):
    return render(request, "login_or_register.html")