from django.shortcuts import render
import psycopg2

from utils.query import query

def dashboard_penonton(request):
    username = request.session.get('username')

    context = {}
    # Untuk Informasi
    informasi = get_informasi(username) # [{'id': 'e2d58d08-5036-46b9-8815-71566405ddfc', 'nama_depan': 'Enrico', 'nama_belakang': 'Dumigan', 'nomor_hp': '083835531812', 'email': 'edumigank@newsvine.com', 'alamat': '7 Stoughton Hill'}]
    status = get_status(informasi[0]['id'])  # [{'id_pertandingan': '01b0dec5-48b3-44d9-b1dd-b9903c33b1ff', 'start_datetime': datetime.datetime(2023, 4, 1, 18, 30), 'end_datetime': datetime.datetime(2023, 4, 1, 21, 30), 'stadium': '74d109b4-94d9-4632-b48b-a7cc96382ddf'}]
    info_pertandingan = get_pertandingan([informasi[0]['id']])

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
    context['data'] = tuple_data

    if info_pertandingan != None:
        print("Masuk if")
        # get nama tim bertanding
        tim_bertanding = []
        for item in info_pertandingan:
            nama_tim_bertanding = get_tim_bertanding(info_pertandingan[0]['id_pertandingan'])
            tim_bertanding += nama_tim_bertanding
        
        #get nama stadium
        stadium = []
        for item in info_pertandingan:
            nama_stadion = get_nama_stadion(info_pertandingan[0]['stadium'])
            stadium += nama_stadion

        info_pertandingan_new = []
        for item in info_pertandingan:
            tuple_values = tuple(item.values())
            info_pertandingan_new.append(tuple_values)
        

        # Info pertandingan fix banget
        info_fix = [tuple(sum(items, ())) for items in zip(tim_bertanding, stadium, info_pertandingan_new)]


        
        context['data_pertandingan'] = info_fix
        print(info_pertandingan_new)
        print(tuple_data) #[('e2d58d08-5036-46b9-8815-71566405ddfc', 'Enrico Dumigan', '083835531812', 'edumigank@newsvine.com', '7 Stoughton Hill', 'Penonton, Dosen')]
        print(info_fix)
        return render(request, 'dashboard_penonton.html',context=context)

    else:
        return render(request, 'dashboard_penonton.html',context=context)

# Untuk mencari seluruh informasi user
def get_informasi(username: str):

    # Mencari ID
    get_id = query(f"""select ID_Penonton from PENONTON 
    where username = '%s'
    """ %(username))
    id_dict = get_id[0]
    
    # Mencari data berdasarkan ID
    get_data = query(f"""select * from NON_PEMAIN 
    where ID = '%s'
    """%(id_dict["id_penonton"]))
    
    return get_data

def get_status(id: str):
    get_status = query(f"""select status from STATUS_NON_PEMAIN 
    where ID_Non_Pemain = '%s'
    """ %(id))
    return get_status

def get_pertandingan(id: str):
    get_id_pertandingan = query(f"""select ID_Pertandingan from PEMBELIAN_TIKET 
    where ID_Penonton = '%s'
    """ %(id[0]))

    if len(get_id_pertandingan) == 0:
        return None
    
    # Eliminasi data duplikat
    unique_id = set(item['id_pertandingan'] for item in get_id_pertandingan)
    
    result = []
    # loop through unique id
    for item in unique_id:
        get_data_pertandingan = query(f"""select * from PERTANDINGAN 
        where ID_Pertandingan = '%s'
        """ %(item))
        result.extend(get_data_pertandingan)

    return get_data_pertandingan



def get_tim_bertanding(id: str):
    get_tim_bertanding = query(f"""select Nama_Tim from TIM_PERTANDINGAN 
    where ID_Pertandingan = '%s'
    """ %(id))

    result = []
    for item in get_tim_bertanding:
        nama_tim = item['nama_tim']
        result.append(nama_tim)

    final_result = [(', '.join(result[:-1]) + ' vs ' + result[-1]),]

    final_result = [(final_result[0],)]
    print(final_result)
    return final_result
    
def get_nama_stadion(id: str):
    get_stadium = query(f"""select nama from STADIUM 
    where id_stadium = '%s'
    """ %(id))

    result = [(item['nama'],) for item in get_stadium]
    
    print(result)
    return result
