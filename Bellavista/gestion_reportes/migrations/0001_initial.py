# Generated by Django 5.1.1 on 2024-10-27 22:04

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Reportes_Problemas',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo_incidente', models.CharField(max_length=100)),
                ('descripcion', models.TextField()),
                ('marco', models.CharField(blank=True, max_length=255, null=True)),
                ('medida_marco', models.TextField(default='Sin medir')),
                ('foto_url', models.ImageField(blank=True, null=True, upload_to='reportes_fotos/')),
                ('fecha_reporte', models.DateTimeField(auto_now_add=True)),
                ('latitud', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('longitud', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('rut_usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Gestion_Fallas',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.TextField()),
                ('ubicacion_geografica', models.CharField(max_length=255)),
                ('estado', models.CharField(max_length=50)),
                ('fecha_reporte', models.DateTimeField()),
                ('rut_usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('id_reporte', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gestion_reportes.reportes_problemas')),
            ],
        ),
        migrations.CreateModel(
            name='Tareas',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('descripcion', models.TextField()),
                ('prioridad', models.CharField(choices=[('Alta', 'Alta'), ('Media', 'Media'), ('Baja', 'Baja')], max_length=20)),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
                ('id_reporte', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='gestion_reportes.reportes_problemas')),
            ],
        ),
        migrations.CreateModel(
            name='Asignacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estado', models.CharField(choices=[('En espera', 'En espera'), ('En progreso', 'En progreso'), ('Completada', 'Completada')], default='En espera', max_length=20)),
                ('asignado_en', models.DateTimeField(auto_now_add=True)),
                ('actualizado_en', models.DateTimeField(auto_now=True)),
                ('fecha_fin', models.DateTimeField(blank=True, null=True)),
                ('trabajador', models.ForeignKey(limit_choices_to={'rol__nombre': 'Trabajador'}, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('tarea', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gestion_reportes.tareas')),
            ],
        ),
    ]