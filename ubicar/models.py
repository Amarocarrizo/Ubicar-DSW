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

class Licencia(models.Model):
    id_Licencia= models.AutoField(primary_key=True)
    LICENCIA = [
        ('A1', 'A1'),
        ('B1', 'B1'),
        ('C1', 'C1'),
        ('C2', 'C2'),
        ('C3', 'C3'),
    ]
    tipo_De_Licencia= models.CharField(max_length=3,choices=LICENCIA)
    def __str__(self):
      return self.tipo_De_Licencia

class Conductor(models.Model):
    id_conductor=models.AutoField(primary_key=True)
    nombre=models.CharField(max_length=30)
    apellido=models.CharField(max_length=30)
    mail=models.CharField(max_length=254)
    telefono=models.CharField(max_length=20)
    dni=models.PositiveIntegerField()
    tipo_licencia = models.ForeignKey(Licencia, on_delete= models.PROTECT)

    def __str__(self): 
        return f"{self.nombre} {self.apellido}"

class TipoDeVehiculo(models.Model):
    idRodado=models.AutoField(primary_key=True)
    VEHICULOS = [
        ('AUTO', 'Auto'),
        ('CAMIONETA', 'Camioneta'),
        ('CAMION', 'Camion'),
        ('MOTO', 'Moto'),
    ] #agrego posibles choices de un vehiculo

    tipoDeRodado=models.CharField(max_length=15,choices=VEHICULOS)
    def __str__(self):
      return self.tipoDeRodado

class Vehiculo(models.Model): #representará una tabla en la base de datos. Cada atributo de esta clase se convertirá en una columna de esa tabla
    patente=models.CharField(max_length=7,primary_key=True)
    #tipo=models.CharField(max_length=50)
    modelo=models.CharField(max_length=50)
    chasis=models.CharField(max_length=50,unique=True)
    kilometraje=models.PositiveIntegerField()
    estado=models.CharField(max_length=30)
    tipo_de_vehiculo= models.ForeignKey(TipoDeVehiculo,on_delete=models.PROTECT ,null=True,blank=True)
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

    def __str__(self):
        return f"Ruta {self.id_ruta}: {self.origen} -> {self.destino}"

class EstadoViaje(models.Model):
    id_estado = models.AutoField(primary_key=True)

    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('EN_CURSO', 'En curso'),
        ('FINALIZADO', 'Finalizado'),
    ]

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS
    )

    def __str__(self):
        return self.estado
    
class Viaje(models.Model):
    id_viaje = models.AutoField(primary_key=True)
    estado = models.ForeignKey(EstadoViaje,on_delete= models.PROTECT)
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
         if self.estado.estado == 'EN CURSO':
           raise ValueError('El viaje ya está en curso')

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
 
         self.estado.estado = 'EN_CURSO'
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
        if self.estado.estado != 'EN_CURSO':
           raise ValueError(
            'Solo se puede finalizar un viaje que esté en curso'
            )
        self.estado.estado = 'FINALIZADO'
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

class AlertaDefinida(models.Model):
    idAlerta=models.AutoField(primary_key=True)
    TIPOALERTA= [
        ('DESVIO','Desvio'),
        ('TARDANZA','Tardanza'),
    ]
    tipo_de_alerta=models.CharField(max_length=15,choices=TIPOALERTA)


class Alerta(models.Model):
    id_alerta = models.AutoField(primary_key=True)
    tipo = models.ForeignKey(AlertaDefinida, on_delete= models.PROTECT)
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