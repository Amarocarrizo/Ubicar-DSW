from django.db import models

#para que acepte float positivos
from django.core.validators import MinValueValidator
from decimal import Decimal
# Create your models here.

#arrancar con las clases independientes para no hacer una dependiente sin haber declarado de la que depende

class Vehiculo(models.Model): #representará una tabla en la base de datos. Cada atributo de esta clase se convertirá en una columna de esa tabla
    patente=models.CharField(max_length=7,primary_key=True)
    tipo=models.CharField(max_length=50)
    modelo=models.CharField(max_length=50)
    chasis=models.CharField(max_length=50,unique=True)
    kilometraje=models.PositiveIntegerField()
    estado=models.CharField(max_length=30)
    capacidad_carga = models.DecimalField( #para que acepte cualq numero positivo, 2 decimales
        max_digits=12, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))] # 
    )

def __str__(self):
    return f"{self.pantente} - {self.modelo}"
