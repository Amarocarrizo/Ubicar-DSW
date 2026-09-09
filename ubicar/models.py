from django.db import models

#para que acepte float positivos
from django.core.validators import MinValueValidator
from decimal import Decimal
# Create your models here.

#arrancar con las clases independientes para no hacer una dependiente sin haber declarado de la que depende

class Administrador(models.Model):
    id_admin=models.IntegerField(primary_key=True)
    nombre=models.CharField(max_length=30)
    apellido=models.CharField(max_length=30)
    mail=models.CharField(max_length=254)
    telefono=models.CharField(max_length=20)
    dni=models.PositiveIntegerField()

def __str__(self): #con lo que identificas la clase
    return f"{self.nombre} {self.apellido}"

class Conductor(models.Model):
    id_conductor=models.IntegerField(primary_key=True)
    nombre=models.CharField(max_length=30)
    apellido=models.CharField(max_length=30)
    mail=models.CharField(max_length=254)
    telefono=models.CharField(max_length=20)
    dni=models.PositiveIntegerField()
    tipo_licencia = models.CharField(max_length=10)

def __str__(self): 
    return f"{self.nombre} {self.apellido}"

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
    id_admins=models.ManyToManyField(Administrador,blank=True)#al registrar un vehículo, no es obligatorio asignarle un administrador en el formulario se puede dsp por eso blank true
    id_conductor = models.ForeignKey(
    Conductor, 
    on_delete=models.SET_NULL, 
    null=True, #bd puede gusardar vacio
    blank=True #podes no asignarle conductor al auto ni bine lo registras
    )
    #uno a muchos, FK. la clase que escribe es la que apunta a lo que esta dentro de fk

def __str__(self):
    return f"{self.pantente} - {self.modelo}"
