"""
Carga datos de prueba para poder usar y demostrar el sistema.

    python manage.py seed_demo

Crea (solo si no existen, se puede correr varias veces):
  - los estados y tipos de gasto que la lógica de Gasto necesita
  - un administrador:  admin / admin1234
  - un conductor:      carlos / carlos1234, con un camión asignado
  - una ruta Campana -> Zárate y un viaje finalizado de ejemplo
"""
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from ubicar.models import (
    Administrador, Conductor, Vehiculo, AsignacionVehiculo, Ruta, Viaje,
    estadoGasto, tipoDeGasto, EstadoViaje,
)


class Command(BaseCommand):
    help = 'Carga datos de prueba (estados de gasto, admin, conductor, vehículo, ruta)'

    def handle(self, *args, **options):
        # 1. Catálogos: Gasto.validar_gasto / aprobar / rechazar buscan estas filas por nombre.
        for estado in ['PENDIENTE', 'VALIDADO', 'A_REVISAR', 'ACEPTADO', 'RECHAZADO']:
            estadoGasto.objects.get_or_create(estado=estado, defaults={'descripcion': estado.title()})
        for razon in ['COMBUSTIBLE', 'PEAJE', 'OTROS']:
            tipoDeGasto.objects.get_or_create(razon_del_gasto=razon)

        # 2. Administrador (usuario de Django con is_staff + fila en Administrador con el mismo mail)
        admin_user = self._usuario('admin', 'admin1234', 'Sofía', 'Ortega', 'admin@ubicar.com', staff=True)
        Administrador.objects.get_or_create(
            mail=admin_user.email,
            defaults={'nombre': 'Sofía', 'apellido': 'Ortega', 'telefono': '1155550000', 'dni': 30111222})

        # 3. Conductor con vehículo asignado (sin asignación vigente no puede crear viajes)
        cond_user = self._usuario('carlos', 'carlos1234', 'Carlos', 'Mendoza', 'carlos@ubicar.com')
        conductor, _ = Conductor.objects.get_or_create(
            usuario=cond_user,
            defaults={'nombre': 'Carlos', 'apellido': 'Mendoza', 'mail': cond_user.email,
                      'telefono': '1155551111', 'dni': 35222333, 'tipo_licencia': 'C1'})
        vehiculo, _ = Vehiculo.objects.get_or_create(
            patente='AE304GN',
            defaults={'modelo': 'Scania G410', 'chasis': 'CH-AE304GN', 'kilometraje': 182000,
                      'estado': 'Activo', 'tipo_de_vehiculo': 'CAMION', 'capacidad_carga': Decimal('18000.00')})
        hoy = timezone.now().date()
        AsignacionVehiculo.objects.get_or_create(
            conductor=conductor, vehiculo=vehiculo,
            defaults={'fecha_desde': hoy - timedelta(days=30), 'fecha_hasta': hoy + timedelta(days=365),
                      'activa': True, 'administrador': Administrador.objects.first()})

        # 4. Una ruta y un viaje ya finalizado, para que el historial no arranque vacío
        ruta, _ = Ruta.objects.get_or_create(
            origen='Campana', destino='Zárate',
            defaults={'distancia_estimada': Decimal('11.20'), 'tiempo_estimado': Decimal('15.00')})
        if not Viaje.objects.exists():
            ahora = timezone.now()
            Viaje.objects.create(
                estado=EstadoViaje.FINALIZADO, id_conductor=conductor, id_ruta=ruta, id_patente=vehiculo,
                hora_inicio=ahora - timedelta(days=1, hours=2), hora_llegada=ahora - timedelta(days=1, hours=1, minutes=40),
                km_inicial=Decimal('181980.00'))

        self.stdout.write(self.style.SUCCESS(
            'Listo. Usuarios: admin / admin1234 (administrador) y carlos / carlos1234 (conductor).'))

    def _usuario(self, username, password, nombre, apellido, mail, staff=False):
        user, creado = User.objects.get_or_create(
            username=username,
            defaults={'email': mail, 'first_name': nombre, 'last_name': apellido,
                      'is_staff': staff, 'is_superuser': staff})
        if creado:
            user.set_password(password)
            user.save()
        return user
