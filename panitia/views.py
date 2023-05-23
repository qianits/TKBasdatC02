from django.shortcuts import render


def dashboard_panitia(request):
    return render(request, 'dashboard_panitia.html')

def panitia_memulai_pertandingan(request):
    return render(request, "mulai_pertandingan.html")
