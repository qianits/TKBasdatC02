from django.db import models

class Rapat(models.Model):
    id_pertandingan = models.UUIDField()
    datetime = models.DateTimeField()
    perwakilan_panitia = models.CharField(max_length=50)
    manajer_tim_a = models.UUIDField()
    manajer_tim_b = models.UUIDField()
    isi_rapat = models.TextField()

    def __str__(self):
        return f"Rapat Pertandingan {self.id_pertandingan}"
