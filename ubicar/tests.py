from django.test import TestCase

# Create your tests here.
from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile

from datetime import timedelta
import tempfile
import shutil

from ubicar.models import (
    Administrador,
    Conductor,
    Vehiculo,
    AsignacionVehiculo,
    Ruta,
    Viaje,
    Posicion,
    Gasto,
    Alerta,
    estadoGasto,
    tipoDeGasto,
    EstadoViaje,
    AlertaDefinida,
)


TEST_MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class UbicarTests(TestCase):

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):

        self.client = APIClient()

        # =========================
        # USUARIO CONDUCTOR
        # =========================
        self.user_conductor = User.objects.create_user(
            username='juan_test',
            password='123456'
        )

        self.conductor = Conductor.objects.create(
            usuario=self.user_conductor,
            nombre='Juan',
            apellido='Perez',
            mail='juan@test.com',
            telefono='111111',
            dni=12345678,
            tipo_licencia='B1'
        )

        # =========================
        # USUARIO ADMIN
        # =========================
        self.user_admin = User.objects.create_user(
            username='admin_test',
            password='123456'
        )

        self.administrador = Administrador.objects.create(
            usuario=self.user_admin,
            nombre='Admin',
            apellido='Test',
            mail='admin@test.com',
            telefono='222222',
            dni=87654321
        )

        # =========================
        # VEHICULO
        # =========================
        self.vehiculo = Vehiculo.objects.create(
            patente='AA123BB',
            modelo='Toyota',
            chasis='CHASISTEST123',
            kilometraje=20000,
            estado='ACTIVO',
            tipo_de_vehiculo='AUTO',
            capacidad_carga=500
        )

        # =========================
        # ASIGNACION
        # =========================
        hoy = timezone.now().date()

        self.asignacion = AsignacionVehiculo.objects.create(
            conductor=self.conductor,
            vehiculo=self.vehiculo,
            administrador=self.administrador,
            fecha_desde=hoy - timedelta(days=1),
            fecha_hasta=hoy + timedelta(days=30),
            activa=True
        )

        # =========================
        # RUTA
        # =========================
        self.ruta = Ruta.objects.create(
            origen='Origen Test',
            destino='Destino Test',
            distancia_estimada=10,
            tiempo_estimado=20,
            geometria_ruta={
                'type': 'LineString',
                'coordinates': [
                    [-58.980660, -34.161655],
                    [-58.970000, -34.150000]
                ]
            }
        )

        # =========================
        # ESTADOS DE GASTO
        # =========================
        self.estado_pendiente, _ = estadoGasto.objects.get_or_create(
            estado='PENDIENTE',
            defaults={'descripcion': 'Pendiente'}
        )

        self.estado_validado, _ = estadoGasto.objects.get_or_create(
            estado='VALIDADO',
            defaults={'descripcion': 'Validado'}
        )

        self.estado_revisar, _ = estadoGasto.objects.get_or_create(
            estado='A_REVISAR',
            defaults={'descripcion': 'A revisar'}
        )

        self.estado_aceptado, _ = estadoGasto.objects.get_or_create(
            estado='ACEPTADO',
            defaults={'descripcion': 'Aceptado'}
        )

        self.estado_rechazado, _ = estadoGasto.objects.get_or_create(
            estado='RECHAZADO',
            defaults={'descripcion': 'Rechazado'}
        )

        # =========================
        # TIPO DE GASTO
        # =========================
        self.tipo_combustible = tipoDeGasto.objects.create(
            razon_del_gasto='COMBUSTIBLE'
        )

        # =========================
        # VIAJE ACTIVO
        # =========================
        self.viaje = Viaje.objects.create(
            id_conductor=self.conductor,
            id_patente=self.vehiculo,
            id_ruta=self.ruta
        )

        self.viaje.iniciar_viaje(
            latitud_inicial=-34.161655,
            longitud_inicial=-58.980660
        )

    # =====================================================
    # TEST 1 - INICIAR VIAJE
    # =====================================================

    def test_iniciar_viaje_guarda_kilometraje_inicial(self):

        self.viaje.refresh_from_db()

        self.assertEqual(
            self.viaje.estado,
            EstadoViaje.EN_CURSO
        )

        self.assertEqual(
            self.viaje.km_inicial,
            self.vehiculo.kilometraje
        )

        self.assertIsNotNone(
            self.viaje.hora_inicio
        )

    # =====================================================
    # TEST 2 - PERDIDA DE CONEXION
    # =====================================================

    def test_perdida_conexion_genera_alerta(self):

        ultima_posicion = Posicion.objects.filter(
            id_viaje=self.viaje
        ).latest('hora')

        ultima_posicion.hora = (
            timezone.now() - timedelta(seconds=40)
        )

        ultima_posicion.save()

        resultado = self.viaje.verificar_perdida_conexion()

        self.assertTrue(resultado)

        self.assertTrue(
            Alerta.objects.filter(
                viaje=self.viaje,
                tipo=AlertaDefinida.PERDIDA_CONEXION,
                estado='PENDIENTE'
            ).exists()
        )

    # =====================================================
    # TEST 3 - GASTO INCONSISTENTE
    # =====================================================

    def test_gasto_inconsistente_queda_a_revisar_y_genera_alerta(self):

        self.client.force_authenticate(
            user=self.user_conductor
        )

        comprobante = SimpleUploadedFile(
            'comprobante_test.txt',
            b'comprobante falso',
            content_type='text/plain'
        )

        response = self.client.post(
            '/api/gasto/',
            {
                'tipo': self.tipo_combustible.pk,
                'monto': '15000.00',

                # El viaje arranca en 20000.
                # Declaramos 20100 para provocar inconsistencia.
                'km_registrado': '20100.00',

                'comprobante': comprobante
            },
            format='multipart'
        )

        self.assertEqual(
            response.status_code,
            201
        )

        gasto = Gasto.objects.latest(
            'id_gasto'
        )

        self.assertEqual(
            gasto.estado.estado,
            'A_REVISAR'
        )

        self.assertTrue(
            Alerta.objects.filter(
                viaje=self.viaje,
                tipo=AlertaDefinida.GASTO_INCONSISTENTE
            ).exists()
        )

    # =====================================================
    # TEST 4 - CONDUCTOR NO PUEDE APROBAR GASTOS
    # =====================================================

    def test_conductor_no_puede_aprobar_gasto(self):

        gasto = Gasto.objects.create(
            tipo=self.tipo_combustible,
            monto=1000,
            comprobante='comprobantes/test.jpg',
            estado=self.estado_revisar,
            km_registrado=20000,
            viaje=self.viaje
        )

        self.client.force_authenticate(
            user=self.user_conductor
        )

        response = self.client.post(
            f'/api/gasto/{gasto.id_gasto}/aprobar/'
        )

        self.assertEqual(
            response.status_code,
            403
        )

    # =====================================================
    # TEST 5 - ADMIN PUEDE APROBAR GASTOS
    # =====================================================

    def test_admin_puede_aprobar_gasto(self):

        gasto = Gasto.objects.create(
            tipo=self.tipo_combustible,
            monto=1000,
            comprobante='comprobantes/test.jpg',
            estado=self.estado_revisar,
            km_registrado=20000,
            viaje=self.viaje
        )

        self.client.force_authenticate(
            user=self.user_admin
        )

        response = self.client.post(
            f'/api/gasto/{gasto.id_gasto}/aprobar/'
        )

        self.assertEqual(
            response.status_code,
            200
        )

        gasto.refresh_from_db()

        self.assertEqual(
            gasto.estado.estado,
            'ACEPTADO'
        )

        self.assertEqual(
            gasto.administrador,
            self.administrador
        )

    # =====================================================
    # TEST 6 - NO DUPLICAR ALERTAS DE DESVIO
    # =====================================================

    def test_no_duplica_alerta_de_desvio(self):

        # Coordenada intencionalmente muy alejada
        latitud = -34.6037
        longitud = -58.3816

        self.viaje.registrar_posicion(
            latitud,
            longitud
        )

        self.viaje.registrar_posicion(
            latitud,
            longitud
        )

        cantidad = Alerta.objects.filter(
            viaje=self.viaje,
            tipo=AlertaDefinida.DESVIO,
            estado='PENDIENTE'
        ).count()

        self.assertEqual(
            cantidad,
            1
        )