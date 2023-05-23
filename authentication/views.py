import uuid
from django.shortcuts import redirect, render, reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
import psycopg2


def authentication(request):
    return render(request, 'login_or_register.html')


def register_manajer_penonton(request):
    form = UserCreationForm()

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Akun telah berhasil dibuat!')
            return redirect('authentication:register_manajer_penonton')
    
    context = {'form':form}
    return render(request, 'register_manajer_penonton.html', context)

def register_panitia(request):
    form = UserCreationForm()

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Akun telah berhasil dibuat!')
            return redirect('authentication:register_panitia')
    
    context = {'form':form}
    return render(request, 'register_panitia.html', context)


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
        id_user = str(uuid.uuid4())
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



    # if is_authenticated(request):
    #     username = str(request.session["username"])
    #     password = str(request.session["password"])
    # else:
    #     username = str(request.POST["username"])
    #     password = str(request.POST["password"])

    # role = get_role(username, password)

    # if role == "":
    #     return login_view(request)
    # else:
    #     request.session["username"] = username
    #     request.session["password"] = password
    #     request.session["role"] = role
    #     request.session.set_expiry(0)
    #     request.session.modified = True

    #     if role == "manajer":
    #         return redirect("manajer:dashboard_manajer")
    #     elif role == "panitia":
    #         return redirect("panitia:dashboard_panitia")
    #     elif role == "penonton":
    #         return redirect("penonton:dashboard_penonton")
    #     else:
    #         return render(request, "login_or_register.html")
        

def login_view(request):
    return render(request, "login_or_register.html")


