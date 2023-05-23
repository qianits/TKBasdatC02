from django.shortcuts import render

def dashboard_penonton(request):
    return render(request, 'dashboard_penonton.html')

def pembelian_tiket(request):
    return render(request, 'pembelian_tiket.html')


