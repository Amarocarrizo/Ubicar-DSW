from django.db import models

# Create your models here.

class Vehiculo(models.Model):
    tipo=models.CharField(max_length=50)
    patente=models.CharField(max_length=7,unique=True)
    modelo=models.CharField(max_length=50)
    chasis=models.CharField(max_length=50,unique=True)
    kilometraje=models.PositiveIntegerField(default=0)
    estado=models.CharField(max_length=30)

def __str__(self):
    return f"{self.pantente} - {self.modelo}"
