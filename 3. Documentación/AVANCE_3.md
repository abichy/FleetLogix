# FleetLogix M2 — Avance 3
## Modelo dimensional y pipeline ETL

### 1. Objetivo
Construir un Data Warehouse en Snowflake para analizar
las operaciones logísticas de FleetLogix a partir de
datos operacionales almacenados en PostgreSQL.

### 2. Arquitectura de datos
Origen: PostgreSQL (base fleetlogix).
Procesamiento: Python.
Destino: Snowflake (FLEETLOGIX_DW.ANALYTICS).
Modelo analítico: esquema estrella.

### 3. Modelo dimensional

Tabla central:
- FACT_DELIVERIES: 400.000 entregas.

Dimensiones:
- DIM_CUSTOMER: 400.000 clientes.
- DIM_DATE: 365 fechas de 2026.
- DIM_DRIVER: 400 conductores.
- DIM_ROUTE: 50 rutas.
- DIM_TIME: 1.440 minutos del día.
- DIM_VEHICLE: 200 vehículos.

La granularidad de FACT_DELIVERIES es una fila
por entrega.

Las métricas de distancia y combustible proceden
del viaje y pueden repetirse en varias entregas.
No deben sumarse directamente por entrega.

### 4. Pipeline ETL

1. etl_extract_deliveries.py
   Extrae datos desde PostgreSQL.

2. etl_refresh_staging.py
   Carga los datos a una tabla temporal y actualiza
   STG_DELIVERIES mediante MERGE.

3. etl_merge_deliveries.py
   Actualiza e inserta entregas en FACT_DELIVERIES.

4. etl_quality_checks.py
   Ejecuta controles de integridad y consistencia.

Orquestador: etl_pipeline.py

Ejecución:
python etl_pipeline.py --execute

### 5. Prueba de integración

Fecha: 18 de noviembre de 2026.

Resultado:
- 400.000 entregas extraídas.
- 400.000 registros validados en staging.
- MERGE ejecutado correctamente.
- 10 controles de calidad aprobados.
- Duración total: 34,92 segundos.

### 6. Calidad y limitaciones

Los controles verifican duplicados, claves nulas,
correspondencia dimensional y consistencia temporal.

La ejecución completa fue validada con los datos
actuales.

Para incorporar nuevas entidades de negocio,
se requiere actualizar las dimensiones correspondientes
o implementar su mantenimiento incremental.

La ejecución entre PostgreSQL y Snowflake no constituye
una transacción distribuida atómica. Ante fallos,
se debe revisar el registro y reejecutar el pipeline.

### 7. Resultado

Se implementó y probó un proceso ETL de extremo a
extremo entre PostgreSQL y Snowflake, con modelo
dimensional, carga incremental y controles automáticos.
