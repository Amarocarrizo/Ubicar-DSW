from django.db import models
from django.utils import timezone

#para que acepte float positivos
from django.core.validators import MinValueValidator
from decimal import Decimal
# Create your models here.

#arrancar con las clases independientes para no hacer una dependiente sin haber declarado de la que depende

class Administrador(models.Model):
    id_admin=models.AutoField(primary_key=True)
    nombre=models.CharField(max_length=30)
    apellido=models.CharField(max_length=30)
    mail=models.CharField(max_length=254)
    telefono=models.CharField(max_length=20)
    dni=models.PositiveIntegerField()

    def __str__(self): #con lo que identificas la clase
        return f"{self.nombre} {self.apellido}"

class Conductor(models.Model):
    id_conductor=models.AutoField(primary_key=True)
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
        return f"{self.patente} - {self.modelo}"


class Ruta(models.Model):
    id_ruta = models.AutoField(primary_key=True)
    origen=models.CharField(max_length=100)
    destino=models.CharField(max_length=100)
    distancia_estimada= models.DecimalField( 
        max_digits=12, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))] # 
    )
    tiempo_estimado= models.DecimalField( 
        max_digits=12, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))] # 
    )

    def __str__(self):
        return f"Ruta {self.id_ruta}: {self.origen} -> {self.destino}"

class Viaje(models.Model):
    id_viaje = models.AutoField(primary_key=True)
    estado = models.CharField(max_length=100)
    hora_inicio = models.DateTimeField(null=True, blank=True)
    hora_llegada = models.DateTimeField(null=True, blank=True)
    id_conductor = models.ForeignKey(
        Conductor, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True 
    )
    id_ruta = models.ForeignKey(
        Ruta, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True 
        )

    id_patente = models.ForeignKey(
        Vehiculo, 
        on_delete=models.SET_NULL, 
        null=True, #bd puede gusardar vacio
        blank=True #podes no asignarle conductor al auto ni bine lo registras
        )

    def __str__(self):
        return f"Viaje: {self.id_viaje}"

    def iniciar_viaje(self, latitud_inicial, longitud_inicial):
        self.estado = 'EN_CURSO'
        self.hora_inicio = timezone.now()
        self.save()
        self.registrar_posicion(latitud_inicial, longitud_inicial)

    def registrar_posicion(self, latitud, longitud):
        return Posicion.objects.create(
            id_viaje=self,
            posicion_x=latitud,
            posicion_y=longitud,
            hora=timezone.now()
        )

    def finalizar_viaje(self):
        self.estado = 'FINALIZADO'
        self.hora_llegada = timezone.now()
        self.save()

class Posicion(models.Model):
    id_posicion = models.AutoField(primary_key=True)
    posicion_x= models.DecimalField( 
            max_digits=12, 
            decimal_places=6
        )
    posicion_y= models.DecimalField( 
                max_digits=12, 
                decimal_places=6
            )
    hora = models.DateTimeField()
    id_viaje = models.ForeignKey(
        Viaje, 
        on_delete=models.SET_NULL, 
        null=True, #bd puede guardar vacio
        blank=True #podes no asignarle conductor al auto ni bien lo registras
        )

    def __str__(self):
        return f"Posicion: {self.posicion_x} {self.posicion_y}"

class Gasto(models.Model):
    id_gasto = models.AutoField(primary_key=True)
    tipo = models.CharField(max_length=20)
    monto = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    comprobante = models.FileField(upload_to='comprobantes/')
    fecha_hora = models.DateTimeField()
    estado = models.CharField(max_length=15)
    km_registrado = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )

    viaje = models.ForeignKey(
        Viaje,
        on_delete=models.CASCADE
    )

    administrador = models.ForeignKey(
        Administrador,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"Gasto {self.id_gasto} - {self.tipo} - ${self.monto}"

    def aprobar(self, administrador):
        self.estado = 'APROBADO'
        self.administrador = administrador #asocia gasto al admin
        self.save()

    def rechazar(self, administrador):
        self.estado = 'RECHAZADO'
        self.administrador = administrador
        self.save()