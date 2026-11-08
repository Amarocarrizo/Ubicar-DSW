from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

#para que acepte float positivos
from django.core.validators import MinValueValidator
from decimal import Decimal
from math import radians, sin, cos, sqrt, atan2
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

class Licencia(models.TextChoices):
     A1="A1", "A1"
     B1="B1","B1"
     C1= "C1", "C1"
     C2="C2", "C2"
     C3="C3", "C3"
      
class Conductor(models.Model):
    id_conductor=models.AutoField(primary_key=True)
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='conductor',
        null=True,
        blank=True
    )
    nombre=models.CharField(max_length=30)
    apellido=models.CharField(max_length=30)
    mail=models.CharField(max_length=254)
    telefono=models.CharField(max_length=20)
    dni=models.PositiveIntegerField()
    tipo_licencia = models.CharField(max_length=3,choices= Licencia.choices)

    def __str__(self): 
        return f"{self.nombre} {self.apellido}"

class TipoDeVehiculo(models.TextChoices):
        AUTO="AUTO", "Auto"
        CAMIONETA="CAMIONETA", "Camioneta"
        CAMION="CAMION", "Camion"
        MOTO="MOTO", "Moto"
    #agrego posibles choices de un vehiculo

class Vehiculo(models.Model): #representará una tabla en la base de datos. Cada atributo de esta clase se convertirá en una columna de esa tabla
    patente=models.CharField(max_length=7,primary_key=True)
    #tipo=models.CharField(max_length=50)
    modelo=models.CharField(max_length=50)
    chasis=models.CharField(max_length=50,unique=True)
    kilometraje=models.PositiveIntegerField()
    estado=models.CharField(max_length=30)
    tipo_de_vehiculo= models.CharField(max_length=20,choices=TipoDeVehiculo.choices)
    capacidad_carga = models.DecimalField( #para que acepte cualq numero positivo, 2 decimales
        max_digits=12, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))] # 
    )
    
    def __str__(self):
        return f"{self.patente} - {self.modelo}"

class AsignacionVehiculo(models.Model):
    conductor = models.ForeignKey(
        Conductor,
        on_delete=models.CASCADE
    )

    vehiculo = models.ForeignKey(
        Vehiculo,
        on_delete=models.CASCADE
    )

    administrador = models.ForeignKey(
        Administrador,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    fecha_desde = models.DateField()
    fecha_hasta = models.DateField()

    activa = models.BooleanField(default=True)
    def __str__(self):
      return f"{self.conductor} - {self.vehiculo}"



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

    # Atributo nuevo para guardar el vector/geometría de OSRM
    geometria_ruta = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"Ruta {self.id_ruta}: {self.origen} -> {self.destino}"

class EstadoViaje(models.TextChoices):
       PENDIENTE= "PENDIENTE", "Pendiente"
       EN_CURSO= "EN CURSO" , "En Curso"
       CANCELADO= "CANCELADO" , "Cancelado"
       FINALIZADO= "FINALIZADO" , "Finalizado" 
  
class Viaje(models.Model):
    id_viaje = models.AutoField(primary_key=True)
    estado = models.CharField(
      max_length=20,
      choices=EstadoViaje.choices,
      default=EstadoViaje.PENDIENTE,
  )
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
        on_delete=models.PROTECT #todo viaje debe tener una ruta, obligatoriamente 
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
         if self.estado != 'ASIGNADO':
          raise ValueError('Solo se puede iniciar un viaje que esté ASIGNADO')

         if self.id_conductor is None:
          raise ValueError('El viaje no tiene conductor asignado')

         if self.id_patente is None:
          raise ValueError('El viaje no tiene vehículo asignado')

         if self.id_ruta is None:
          raise ValueError('El viaje no tiene ruta asignada')

         asignacion = AsignacionVehiculo.objects.filter(
         conductor=self.id_conductor,
         vehiculo=self.id_patente,
         activa=True,
         fecha_desde__lte=timezone.now().date(),
         fecha_hasta__gte=timezone.now().date()
         ).exists()

         if not asignacion:
            raise ValueError(
        'El vehículo no está habilitado para este conductor'
         )

         #estado_en_curso = EstadoViaje.objects.get(estado="EN CURSO")

         self.estado = EstadoViaje.EN_CURSO
         self.hora_inicio = timezone.now()
         self.save()
         self.registrar_posicion(latitud_inicial, longitud_inicial)

    def rechazar_viaje(self):
        """El chofer rechaza el viaje asignado."""
        if self.estado != 'ASIGNADO':
            raise ValueError('Solo se puede rechazar un viaje que esté ASIGNADO')
        
        self.estado = 'RECHAZADO'
        self.save()

    def registrar_posicion(self, latitud, longitud):
        # 1- Guardar la posición actual en la base de datos
        posicion= Posicion.objects.create(
            id_viaje=self,
            posicion_x=latitud,
            posicion_y=longitud,
            hora=timezone.now()
        )
        # 2- Verificar el desvío comparando con la ruta
        UMBRAL_DESVIO_METROS = 200.0  # Margen permitido de desvío (ej: 200 metros)
        distancia_al_camino = self._calcular_distancia_a_ruta(latitud, longitud)

        if distancia_al_camino > UMBRAL_DESVIO_METROS:
            # Buscar el tipo de alerta 'DESVIO'
            Alerta.objects.create(
            tipo=AlertaDefinida.DESVIO,
            descripcion=f"El vehículo se desvió {round(distancia_al_camino, 2)} metros de la ruta planificada.",
            estado='PENDIENTE',
            viaje=self
           )
            self.estado = EstadoViaje.PENDIENTE
            self.save()
        else:
           self.estado = EstadoViaje.EN_CURSO
           self.save()
        return posicion

    def finalizar_viaje(self):
        if self.estado!= EstadoViaje.EN_CURSO:
           raise ValueError(
            'Solo se puede finalizar un viaje que esté en curso'
            )
        self.estado= EstadoViaje.FINALIZADO
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
        on_delete=models.CASCADE  #si elimino el viaje, se eliminan sus posiciones
        )

    def __str__(self):
        return f"Posicion: {self.posicion_x} {self.posicion_y}"

class estadoGasto(models.Model):
    idEstado= models.AutoField(primary_key=True)
    ESTADOGASTO=[
        ('RECHAZADO','Rechazado'),
        ('PENDIENTE','Pendiente'),
        ('ACEPTADO','Aceptado'),
        ('AUSENTE','Ausente'),
    ]
    estado=models.CharField(max_length=20,choices=ESTADOGASTO,default='PENDIENTE')
    descripcion=models.CharField(max_length=50)

class tipoDeGasto(models.Model):
    idTipoDeGasto= models.AutoField(primary_key=True)
    GASTOS = [
        ('COMBUSTIBLE', 'Combustible'),
        ('PEAJE', 'Peaje'),
        ('OTROS', 'Otro'),
    ] #agrego posibles choices de un gasto
    razon_del_gasto= models.CharField(max_length=20,choices=GASTOS)

class Gasto(models.Model):
    id_gasto = models.AutoField(primary_key=True)
    tipo = models.ForeignKey(tipoDeGasto,on_delete=models.PROTECT)
    monto = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    comprobante = models.FileField(upload_to='comprobantes/')
    fecha_hora = models.DateTimeField(default= timezone.now)
    estado = models.ForeignKey(estadoGasto,on_delete=models.PROTECT)
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
     estado_aprobado = estadoGasto.objects.get(
        estado='ACEPTADO'
    )

     self.estado = estado_aprobado
     self.administrador = administrador #asigna el gasto al administrador
     self.save()

    def rechazar(self, administrador):
     estado_rechazado = estadoGasto.objects.get(
        estado='RECHAZADO'
    )

     self.estado = estado_rechazado
     self.administrador = administrador
     self.save()

class AlertaDefinida(models.TextChoices):
        DESVIO="DESVIO","Desvio"
        TARDANZA= "TARDANZA","Tardanza"
    
class Alerta(models.Model):
    id_alerta = models.AutoField(primary_key=True)
    tipo = models.CharField(max_length=20 ,choices=AlertaDefinida.choices)
    descripcion = models.CharField(max_length=250)
    fecha_hora = models.DateTimeField(default=timezone.now)
    estado = models.CharField(max_length=20, default='PENDIENTE')

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
        return f"Alerta {self.id_alerta} - {self.tipo}"