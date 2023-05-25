from django.shortcuts import render
import psycopg2

from utils.query import query

def dashboard_manajer(request):
    username = request.session.get('username')
    context = {}

    # Untuk Informasi
    informasi = get_informasi(username) 
    status = get_status(informasi[0]['id']) 
    nama_tim = get_tim(informasi[0]['id']) 

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
    merged_data.extend(nama_tim)

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

    return render(request, 'dashboard_manajer.html', context=context)


# Untuk mencari seluruh informasi user
def get_informasi(username: str):
    
    # Mencari ID
    get_id = query(f"""select ID_Manajer from MANAJER 
    where username = '%s'
    """ %(username))
    print(get_id)
    id_dict = get_id[0]


    # Mencari data berdasarkan ID
    get_data = query("""select * from NON_PEMAIN 
    where ID = '%s'
    """%(id_dict["id_manajer"]))
    
    return get_data

def get_status(id: str):
    get_status = query("""select status from STATUS_NON_PEMAIN 
    where ID_Non_Pemain = '%s'
    """ %(id))
    
    return get_status

def get_tim(id: str):
    get_tim = query("""select Nama_Tim from TIM_MANAJER 
    where ID_Manajer = '%s'
    """ %(id))

    return get_tim