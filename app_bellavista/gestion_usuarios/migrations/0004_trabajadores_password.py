# Generated by Django 5.1.1 on 2024-09-21 14:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion_usuarios', '0003_alter_trabajadores_apellido_m_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='trabajadores',
            name='password',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
