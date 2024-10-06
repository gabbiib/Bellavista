# gestion_usuarios/data.py
import pandas as pd
from datetime import datetime, timedelta

def crear_dataframes():
    # Crear un DataFrame para trabajadores
    data_trabajadores = {
        'id_trabajador': ['21026807', '21026808', '21026809', '21026810', '21026811', '21026812'],
        'nombre': ['Juan Pérez', 'Ana Gómez', 'Carlos Ruiz', 'María López', 'José Martínez', 'Luisa Fernández'],
        'departamento': ['Administración', 'Ventas', 'Recursos Humanos', 'TI', 'Logística', 'Marketing'],
    }

    df_trabajadores = pd.DataFrame(data_trabajadores)

    # Crear un DataFrame para Gestión de Fallas
    data_gestion_fallas = {
        'id_falla': [1, 2, 3, 4, 5, 6],
        'descripcion': ['Falla en el sistema', 'Problema de red', 'Falla en la impresora', 'Error en el software', 'Falla eléctrica', 'Problema con el servidor'],
        'estado': ['Pendiente', 'Resuelto', 'En Progreso', 'Resuelto', 'Pendiente', 'En Progreso'],
        'fecha_reportado': [
            datetime.now().date() - timedelta(days=2),
            datetime.now().date() - timedelta(days=1),
            datetime.now().date(),
            datetime.now().date() - timedelta(days=3),
            datetime.now().date() - timedelta(days=5),
            datetime.now().date() - timedelta(days=4)
        ],
        'id_trabajador': ['21026807', '21026808', '21026809', '21026810', '21026811', '21026812'],
    }

    df_gestion_fallas = pd.DataFrame(data_gestion_fallas)

    # Crear un DataFrame para Reportes de Problemas
    data_reportes_problemas = {
        'id_reporte': [1, 2, 3, 4, 5, 6],
        'tipo_incidente': ['Incidente de software', 'Incidente de hardware', 'Incidente de seguridad', 'Incidente en la red', 'Incidente en la infraestructura', 'Incidente de personal'],
        'fecha_reporte': [
            datetime.now().date() - timedelta(days=2),
            datetime.now().date() - timedelta(days=1),
            datetime.now().date(),
            datetime.now().date() - timedelta(days=3),
            datetime.now().date() - timedelta(days=5),
            datetime.now().date() - timedelta(days=4)
        ],
        'id_trabajador': ['21026807', '21026808', '21026809', '21026810', '21026811', '21026812'],
    }

    df_reportes_problemas = pd.DataFrame(data_reportes_problemas)

    return df_trabajadores, df_gestion_fallas, df_reportes_problemas
