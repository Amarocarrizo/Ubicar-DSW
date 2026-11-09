from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

#para que acepte float positivos
from django.core.validators import MinValueValidator
from decimal import Decimal
from math import radians, sin, cos, sqrt, atan2
from datetime import timedelta
# Create your models here.

#arrancar con las clases independientes para no hacer una dependiente sin haber declarado de la que depende

class Administrador(models.Model):
    id_admin=models.AutoField(primary_key=True)
    usuario = models.OneToOneField(
    User,
    on_delete=models.CASCADE,
    related_name='administrador',
    null=True,
    blank=True
    )
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
    km_inicial = models.DecimalField(
     max_digits=10,
     decimal_places=2,
     null=True,
     blank=True
    )

    def __str__(self):
        return f"Viaje: {self.id_viaje}"

    def iniciar_viaje(self, latitud_inicial=None, longitud_inicial=None):
         if self.estado == EstadoViaje.EN_CURSO:
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

         #estado_en_curso = EstadoViaje.objects.get(estado="EN CURSO")

         self.estado = EstadoViaje.EN_CURSO
         self.hora_inicio = timezone.now()
         self.km_inicial = self.id_patente.kilometraje
         self.save()
         if latitud_inicial is not None and longitud_inicial is not None:
          self.registrar_posicion(latitud_inicial, longitud_inicial)
    def _calcular_distancia_a_ruta(self, lat_actual, lon_actual):
        """Calcula la distancia mínima en metros entre la posición actual 
           y los puntos de la geometría de la ruta guardada en JSON.
        """
        if not self.id_ruta or not self.id_ruta.geometria_ruta:
            return 0 # Si no hay ruta o geometría guardada, no hay desvío medible

        geometria = self.id_ruta.geometria_ruta
        coordenadas = []

        # Dependiendo de cómo guardes el JSON de OSRM (GeoJSON o array de coords)
        # Si guardas el GeoJSON de OSRM estándar (LineString), las coordenadas vienen como [lon, lat]
        if isinstance(geometria, dict) and 'coordinates' in geometria:
            coordenadas = geometria['coordinates'] # [[lon, lat], [lon, lat], ...]
        elif isinstance(geometria, list):
            coordenadas = geometria

        min_distancia = float('inf')
        lat1 = radians(float(lat_actual))
        lon1 = radians(float(lon_actual))

        # Radio de la Tierra en metros
        R = 6371000 

        for punto in coordenadas:
            # OSRM guarda [longitud, latitud]
            lon2 = radians(float(punto[0]))
            lat2 = radians(float(punto[1]))

            dlat = lat2 - lat1
            dlon = lon2 - lon1

            a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))
            distancia = R * c

            if distancia < min_distancia:
                min_distancia = distancia

        return min_distancia # Retorna la distancia en metros al punto más cercano de la ruta

    def registrar_posicion(self, latitud, longitud):
        # 1- Guardar la posición actual en la base de datos
        posicion= Posicion.objects.create(
            id_viaje=self,
            posicion_x=latitud,
            posicion_y=longitud,
            hora=timezone.now()
        )
        # 2- Si había una alerta de pérdida de conexión pendiente,
         # significa que volvió la conexión
        Alerta.objects.filter(
        viaje=self,
        tipo=AlertaDefinida.PERDIDA_CONEXION,
        estado='PENDIENTE'
        ).update(
         estado='RESUELTA'
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
    def verificar_perdida_conexion(self):

     # Si el viaje ya terminó, no tiene sentido verificar conexión
     if self.hora_llegada is not None:
        return False

     # Buscar la última posición recibida
     ultima_posicion = Posicion.objects.filter(
        id_viaje=self
     ).order_by('-hora').first()

    # Si por alguna razón todavía no hay posiciones
     if ultima_posicion is None:
        return False

    # La app manda posición cada 10 segundos.
    # Damos margen de 30 segundos antes de considerar pérdida.
     limite = timezone.now() - timedelta(seconds=30)

     if ultima_posicion.hora < limite:

        # Evitar crear la misma alerta una y otra vez
        alerta_existente = Alerta.objects.filter(
            viaje=self,
            tipo=AlertaDefinida.PERDIDA_CONEXION,
            estado='PENDIENTE'
        ).exists()

        if not alerta_existente:

            Alerta.objects.create(
                tipo=AlertaDefinida.PERDIDA_CONEXION,
                descripcion=(
                    "No se recibe geolocalización "
                    "del conductor hace más de 30 segundos."
                ),
                estado='PENDIENTE',
                viaje=self
            )

        return True

     return False
    def _distancia_haversine(self, lat1, lon1, lat2, lon2): #repito la formula haversine 
     R = 6371000  # radio de la Tierra en metros

     lat1 = radians(lat1)
     lon1 = radians(lon1)
     lat2 = radians(lat2)
     lon2 = radians(lon2)

     dlat = lat2 - lat1
     dlon = lon2 - lon1

     a = (
        sin(dlat / 2) ** 2
        + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
     )

     c = 2 * atan2(sqrt(a), sqrt(1 - a))

     return R * c
    def calcular_km_recorridos(self): #calculo los kilometros recorridos entre posiciones

     posiciones = list(
        self.posicion_set.order_by('hora')
     )

     if len(posiciones) < 2:
        return 0

     distancia_total = 0

     for i in range(len(posiciones) - 1):

        p1 = posiciones[i]
        p2 = posiciones[i + 1]

        distancia_total += self._distancia_haversine(
            float(p1.posicion_x),
            float(p1.posicion_y),
            float(p2.posicion_x),
            float(p2.posicion_y)
        )

     return distancia_total / 1000
    

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
        ('VALIDADO', 'Validado'),
        ('A_REVISAR', 'A revisar'),
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
    def validar_gasto(self):

     km_gps = self.viaje.calcular_km_recorridos()

     km_declarados = (
     float(self.km_registrado)
     - float(self.viaje.km_inicial)
     )

     diferencia = abs(
     km_declarados - km_gps
     )
     TOLERANCIA_KM = 5

     if diferencia <= TOLERANCIA_KM:

        estado_validado = estadoGasto.objects.get(
            estado='VALIDADO'
        )

        self.estado = estado_validado
        self.save()

        return True

     else:

        estado_revisar = estadoGasto.objects.get(
            estado='A_REVISAR'
        )

        self.estado = estado_revisar
        self.save()

        Alerta.objects.create(
            tipo=AlertaDefinida.GASTO_INCONSISTENTE,
            descripcion=(
                f"Gasto inconsistente. "
                f"Km declarados: {self.km_registrado}. "
                f"Km GPS: {round(km_gps, 2)}."
            ),
            estado=EstadoAlerta.PENDIENTE,
            viaje=self.viaje
        )

        return False

class AlertaDefinida(models.TextChoices):
        DESVIO="DESVIO","Desvio"
        TARDANZA= "TARDANZA","Tardanza"
        PERDIDA_CONEXION = "PERDIDA_CONEXION", "Perdida de conexion"
        GASTO_INCONSISTENTE = "GASTO_INCONSISTENTE","Gasto inconsistente"

class EstadoAlerta(models.TextChoices):
    PENDIENTE = "PENDIENTE", "Pendiente"
    IRREGULARIDAD_CONFIRMADA = "IRREGULARIDAD_CONFIRMADA", "Irregularidad confirmada"
    REVISADA_SIN_NOVEDAD = "REVISADA_SIN_NOVEDAD", "Revisada sin novedad"
    RESUELTA = "RESUELTA", "Resuelta"

    
class Alerta(models.Model):
    id_alerta = models.AutoField(primary_key=True)
    tipo = models.CharField(max_length=20 ,choices=AlertaDefinida.choices)
    descripcion = models.CharField(max_length=250)
    fecha_hora = models.DateTimeField(default=timezone.now)
    estado = models.CharField(
    max_length=30,
    choices=EstadoAlerta.choices,
    default=EstadoAlerta.PENDIENTE
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

    fecha_revision = models.DateTimeField( #se cuando se auditó
    null=True,
    blank=True
     )

    def confirmar_irregularidad(self, administrador):
     self.estado = EstadoAlerta.IRREGULARIDAD_CONFIRMADA
     self.administrador = administrador
     self.fecha_revision = timezone.now()
     self.save()
 

    def revisar_sin_novedad(self, administrador):
     self.estado = EstadoAlerta.REVISADA_SIN_NOVEDAD
     self.administrador = administrador
     self.fecha_revision = timezone.now()
     self.save()

    def __str__(self):
        return f"Alerta {self.id_alerta} - {self.tipo}"

