from django.db import migrations

def poblar_catalogos(apps, schema_editor):
    tipoDeGasto = apps.get_model('ubicar', 'tipoDeGasto')
    estadoGasto = apps.get_model('ubicar', 'estadoGasto')

    # Tipos de gasto
    tipos = ['COMBUSTIBLE', 'PEAJE', 'OTROS']
    for t in tipos:
        tipoDeGasto.objects.get_or_create(razon_del_gasto=t)

    # Estados de gasto
    estados = [
        ('PENDIENTE', 'Pendiente de revisión'),
        ('VALIDADO', 'Validado automáticamente por GPS'),
        ('A_REVISAR', 'A revisar por desvío de kilometraje'),
        ('ACEPTADO', 'Aceptado por administrador'),
        ('RECHAZADO', 'Rechazado por administrador'),
        ('AUSENTE', 'Ausente'),
    ]
    for est, desc in estados:
        estadoGasto.objects.get_or_create(estado=est, defaults={'descripcion': desc})

def revertir_catalogos(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('ubicar', '0017_gasto_descripcion_y_nombres_admin'),
    ]

    operations = [
        migrations.RunPython(poblar_catalogos, revertir_catalogos),
    ]
