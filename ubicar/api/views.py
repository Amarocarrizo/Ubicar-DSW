#view se encarga del CRUD del modelo ubicar vehiculo
from rest_framework import viewsets, status
from ubicar.models import Vehiculo
from ubicar.models import Administrador
from ubicar.models import Conductor
from ubicar.models import Ruta
from ubicar.models import Posicion
from ubicar.models import Viaje
from ubicar.models import Gasto
from ubicar.models import Alerta
from ubicar.models import AsignacionVehiculo
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import serializers
from ubicar.models import estadoGasto, tipoDeGasto
from ubicar.api.serializer import VehiculoSerializer
from ubicar.api.serializer import AdministradorSerializer
from ubicar.api.serializer import ConductorSerializer
from ubicar.api.serializer import RutaSerializer
from ubicar.api.serializer import ViajeSerializer
from ubicar.api.serializer import PosicionSerializer
from ubicar.api.serializer import GastoSerializer
from ubicar.api.serializer import AlertaSerializer
from ubicar.api.serializer import AsignacionVehiculoSerializer
from ubicar.api.serializer import TipoDeGastoSerializer

class VehiculoViewsSet(viewsets.ModelViewSet):
    queryset= Vehiculo.objects.all()
    serializer_class=VehiculoSerializer

class AdministradorViewsSet(viewsets.ModelViewSet):
    queryset=Administrador.objects.all()
    serializer_class=AdministradorSerializer

class AsignacionVehiculoViewSet(viewsets.ModelViewSet):
    queryset = AsignacionVehiculo.objects.all()
    serializer_class = AsignacionVehiculoSerializer

class ConductorViewsSet(viewsets.ModelViewSet):
    queryset= Conductor.objects.all()
    serializer_class= ConductorSerializer

class RutaViewsSet(viewsets.ModelViewSet):
    queryset= Ruta.objects.all()
    serializer_class= RutaSerializer
class ViajeViewsSet(viewsets.ModelViewSet):
    queryset = Viaje.objects.all()
    serializer_class = ViajeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Un conductor solo ve sus propios viajes (los más nuevos primero); el admin ve todos.
        viajes = Viaje.objects.all().order_by('-id_viaje')
        conductor = Conductor.objects.filter(usuario=self.request.user).first()
        if conductor and not self.request.user.is_staff:
            viajes = viajes.filter(id_conductor=conductor)
        return viajes

    def perform_create(self, serializer):
        conductor = self.request.user.conductor

        asignacion = AsignacionVehiculo.objects.filter(
            conductor=conductor,
            activa=True,
            fecha_desde__lte=timezone.now().date(),
            fecha_hasta__gte=timezone.now().date()
        ).first()

        if not asignacion:
            raise serializers.ValidationError(
                "El conductor no tiene un vehículo asignado actualmente"
            )

        serializer.save(
            id_conductor=conductor,
            id_patente=asignacion.vehiculo
        )

    @action(detail=True, methods=['post'])
    def iniciar(self, request, pk=None):
        viaje = self.get_object()

        latitud = request.data.get('latitud')
        longitud = request.data.get('longitud')

        if latitud is None or longitud is None:
            return Response(
                {'error': 'Debe enviar latitud y longitud'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            viaje.iniciar_viaje(latitud, longitud)

            return Response({
                'mensaje': 'Viaje iniciado correctamente'
            })

        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    @action(detail=True, methods=['post'])
    def posicion(self, request, pk=None):
        viaje = self.get_object()
        latitud = request.data.get('latitud')
        longitud = request.data.get('longitud')

        if latitud is None or longitud is None:
            return Response(
                {'error': 'Debe enviar latitud y longitud'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Llama directamente al método que ya tenías programado en el modelo
            posicion_registrada = viaje.registrar_posicion(float(latitud), float(longitud))
            return Response({
                'mensaje': 'Posición registrada con éxito',
                'lat': posicion_registrada.posicion_x,
                'lon': posicion_registrada.posicion_y
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    @action(detail=True, methods=['post'])
    def finalizar(self, request, pk=None):
        viaje = self.get_object()
        
        try:
            # Llama al método del modelo que valida que esté en curso y setea la hora de llegada
            viaje.finalizar_viaje()
            
            return Response({
                'mensaje': 'Viaje finalizado con éxito',
                'id_viaje': viaje.id_viaje,
                'estado': viaje.estado,
                'hora_llegada': viaje.hora_llegada
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            # Si el viaje no estaba en curso, captura el error del modelo y devuelve un 400
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    @action(detail=False, methods=['post'])
    def verificar_conexiones(self, request):

      viajes_activos = Viaje.objects.filter(
        hora_inicio__isnull=False,
        hora_llegada__isnull=True
     )

      viajes_sin_conexion = []

      for viaje in viajes_activos:

        if viaje.verificar_perdida_conexion():
            viajes_sin_conexion.append(
                viaje.id_viaje
            )

      return Response({
        'mensaje': 'Verificación realizada',
        'viajes_sin_conexion': viajes_sin_conexion
    })
    
class PosicionViewsSet(viewsets.ModelViewSet):
    queryset= Posicion.objects.all()
    serializer_class= PosicionSerializer

class GastoViewsSet(viewsets.ModelViewSet):
    queryset = Gasto.objects.all()
    serializer_class = GastoSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):

        # 1- Obtener conductor autenticado
        try:
            conductor = self.request.user.conductor

        except Conductor.DoesNotExist:
            raise serializers.ValidationError(
                "El usuario autenticado no es un conductor."
            )

        # 2- Buscar el viaje activo MÁS RECIENTE
        viaje = Viaje.objects.filter(
            id_conductor=conductor,
            hora_inicio__isnull=False,
            hora_llegada__isnull=True
        ).order_by('-hora_inicio').first()

        if viaje is None:
            raise serializers.ValidationError(
                "El conductor no tiene un viaje activo."
            )

        # 3- El viaje tiene que haber sido iniciado correctamente
        if viaje.km_inicial is None:
            raise serializers.ValidationError(
                "El viaje activo no tiene kilometraje inicial registrado."
            )

        # 4- Buscar estado inicial PENDIENTE
        estado_pendiente = estadoGasto.objects.filter(
            estado='PENDIENTE'
        ).first()

        if estado_pendiente is None:
            raise serializers.ValidationError(
                "No existe el estado PENDIENTE para los gastos."
            )

        # 5- Crear gasto asociado automáticamente al viaje
        gasto = serializer.save(
            viaje=viaje,
            estado=estado_pendiente
        )

        # 6- Prevalidación automática
        gasto.validar_gasto()
    @action(detail=True, methods=['post'])
    def aprobar(self, request, pk=None):

     gasto = self.get_object()

     administrador_id = request.data.get('administrador')

     administrador = Administrador.objects.get(
        id_admin=administrador_id
     )

     gasto.aprobar(administrador)

     return Response({
        'mensaje': 'Gasto aprobado correctamente'
     })


    @action(detail=True, methods=['post'])
    def rechazar(self, request, pk=None):

     gasto = self.get_object()

     administrador_id = request.data.get('administrador')

     administrador = Administrador.objects.get(
        id_admin=administrador_id
     )

     gasto.rechazar(administrador)

     return Response({
        'mensaje': 'Gasto rechazado correctamente'
     })

class TipoDeGastoViewSet(viewsets.ReadOnlyModelViewSet):
    """Catálogo de tipos de gasto (combustible, peaje, otros) para el formulario de carga."""
    queryset = tipoDeGasto.objects.all()
    serializer_class = TipoDeGastoSerializer

class AlertaViewsSet(viewsets.ModelViewSet):
    queryset= Alerta.objects.all()
    serializer_class= AlertaSerializer
    @action(detail=True, methods=['post'])
    def confirmar(self, request, pk=None):

     alerta = self.get_object()

     administrador_id = request.data.get('administrador')

     administrador = Administrador.objects.get(
        id_admin=administrador_id
     )

     alerta.confirmar_irregularidad(administrador)

     return Response({
        'mensaje': 'Irregularidad confirmada'
     })
    @action(detail=True, methods=['post'])
    def sin_novedad(self, request, pk=None):

     alerta = self.get_object()

     administrador_id = request.data.get('administrador')

     administrador = Administrador.objects.get(
        id_admin=administrador_id
     )

     alerta.revisar_sin_novedad(administrador)

     return Response({
        'mensaje': 'Alerta revisada sin novedad'
     })



class MeView(APIView):
    """GET /api/me/ -> quién está logueado, su rol y sus datos.

    El front lo llama después del login para saber qué pantalla mostrar
    (conductor o administrador) y con qué id de administrador aprobar/rechazar.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        conductor = Conductor.objects.filter(usuario=user).first()
        # Administrador no está ligado a User: se lo reconoce por el mail.
        administrador = Administrador.objects.filter(mail=user.email).first()

        if administrador or user.is_staff:
            rol = 'admin'
        elif conductor:
            rol = 'conductor'
        else:
            rol = 'sin_rol'

        vehiculo = None
        if conductor:
            hoy = timezone.now().date()
            asignacion = AsignacionVehiculo.objects.filter(
                conductor=conductor, activa=True,
                fecha_desde__lte=hoy, fecha_hasta__gte=hoy,
            ).first()
            if asignacion:
                vehiculo = VehiculoSerializer(asignacion.vehiculo).data

        return Response({
            'username': user.username,
            'rol': rol,
            'conductor': ConductorSerializer(conductor).data if conductor else None,
            'administrador': AdministradorSerializer(administrador).data if administrador else None,
            'vehiculo_asignado': vehiculo,
        })
