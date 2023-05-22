from django.shortcuts import redirect, render
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

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