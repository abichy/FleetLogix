# Scripts de FleetLogix M2

Los scripts ejecutables permanecen temporalmente
en la raíz del proyecto para conservar las rutas
utilizadas por el pipeline ETL.

## Pipeline principal

| Archivo | Función |
|---|---|
| etl_pipeline.py | Orquesta el proceso |
| etl_extract_deliveries.py | Extrae PostgreSQL |
| etl_refresh_staging.py | Actualiza staging |
| etl_merge_deliveries.py | Actualiza hechos |
| etl_quality_checks.py | Valida calidad |

## Dimensiones

- etl_load_customers.py
- etl_load_dates.py
- etl_load_drivers.py
- etl_load_routes.py
- etl_load_time.py
- etl_load_vehicles.py

## Ejecución

Desde la raíz del proyecto:

python etl_pipeline.py --execute

## Resultado verificado

- 400.000 entregas procesadas.
- 10 controles de calidad aprobados.
- Pipeline completo en 34,92 segundos.

## Consideraciones

Se requiere configurar PostgreSQL y Snowflake.

No publicar contraseñas ni credenciales.
