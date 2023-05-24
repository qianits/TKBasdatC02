from django.db import models

# Create your models here.
class Tim(models.Model):
    nama_tim = models.CharField(max_length=50)
    universitas = models.CharField(max_length=50)

class Pemain(models.Model):
    nama_pemain = models.CharField(max_length=50)
    nomor_hp = models.CharField(max_length=15)
    tanggal_lahir = models.DateField()
    is_captain = models.BooleanField(default=False)
    posisi = models.CharField(max_length=50)
    npm = models.CharField(max_length=20)
    jenjang = models.CharField(max_length=20)
    tim = models.ForeignKey(Tim, on_delete=models.CASCADE, related_name='pemain')

class Pelatih(models.Model):
    nama_pelatih = models.CharField(max_length=50)
    nomor_hp = models.CharField(max_length=15)
    email = models.EmailField()
    alamat = models.CharField(max_length=255)
    spesialisasi = models.CharField(max_length=50)
    tim = models.ForeignKey(Tim, on_delete=models.CASCADE, related_name='pelatih')

class NotulensiTemp(models.Model):
    notulensi = models.TextField()

