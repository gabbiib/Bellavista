# Generated by Django 5.1.1 on 2024-11-11 02:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion_datos', '0002_alter_marcos_options'),
        ('gestion_reportes', '0003_remove_reportes_problemas_es_predeterminado_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reportes_problemas',
            name='marco',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='gestion_datos.marcos'),
        ),
        migrations.AlterField(
            model_name='reportes_problemas',
            name='tipo_incidente',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gestion_datos.problemas'),
        ),
        migrations.DeleteModel(
            name='Gestion_Fallas',
        ),
    ]
