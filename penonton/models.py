from django.db import models

# Create your models here.

class StadiumTemp(models.Model):
    nama_stadium = models.CharField(max_length=100)
    tanggal = models.CharField(max_length=10)