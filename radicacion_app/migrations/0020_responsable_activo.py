from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('radicacion_app', '0019_alerta_radicado'),
    ]

    operations = [
        migrations.AddField(
            model_name='responsable',
            name='activo',
            field=models.BooleanField(default=True),
        ),
    ]