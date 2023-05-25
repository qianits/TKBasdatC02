from django.shortcuts import render
import psycopg2

from utils.query import query



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