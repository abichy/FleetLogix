# Proyecto M2 ABIGAIL ÁLVAREZ
## Data Science — Henry | FleetLogix

Sistema de ingeniería de datos para analizar operaciones logísticas mediante PostgreSQL, Python, Snowflake y una arquitectura cloud propuesta en AWS.


## Organización del repositorio

| Carpeta | Contenido |
|---|---|
| [notebooks](notebooks/) | Desarrollo de los avances en Jupyter |
| [scripts](scripts/) | Guía del pipeline y scripts Python |
| [sql](sql/) | Consultas y optimización SQL |
| [docs](docs/) | Modelo estrella y arquitectura AWS |
| [evidencias](evidencias/) | Capturas y resultados de validación |

## Tecnologías

- Python: generación, extracción y transformación de datos.
- PostgreSQL: base de datos operacional.
- Snowflake: Data Warehouse analítico.
- SQL: consultas, optimización y modelo dimensional.
- AWS: diseño de arquitectura cloud.
- GitHub: documentación y control de versiones.

## Datos del proyecto

| Tabla operacional | Registros |
|---|---:|
| deliveries | 400.000 |
| trips | 100.000 |
| maintenance | 5.000 |
| drivers | 400 |
| vehicles | 200 |
| routes | 50 |
| **Total** | **505.650** |

## Avance 1 — Base de datos operacional

Diseño de seis tablas relacionales en PostgreSQL, generación de datos sintéticos y carga de información logística.

## Avance 2 — Consultas y optimización

Desarrollo de consultas SQL para analizar operaciones logísticas y evaluación del rendimiento mediante EXPLAIN.

## Avance 3 — Data Warehouse y ETL

Implementación de un modelo estrella en Snowflake:

- FACT_DELIVERIES: 400.000 entregas.
- DIM_CUSTOMER: 400.000 clientes.
- DIM_DATE: 365 fechas.
- DIM_DRIVER: 400 conductores.
- DIM_ROUTE: 50 rutas.
- DIM_TIME: 1.440 minutos.
- DIM_VEHICLE: 200 vehículos.

Pipeline ETL:

1. Extracción desde PostgreSQL.
2. Actualización incremental de staging.
3. MERGE de la tabla de hechos.
4. Controles automáticos de calidad.

**Resultado de la prueba:** 400.000 entregas procesadas, 10 controles aprobados y ejecución completa en 34,92 segundos.

[Documentación del Avance 3](docs/AVANCE_3.md)

[Diagrama del modelo estrella](docs/MODELO_ESTRELLA.md)

## Avance 4 — Arquitectura AWS

Diseño propuesto con:

- Amazon API Gateway.
- AWS Lambda.
- Amazon RDS PostgreSQL.
- Amazon DynamoDB.
- Amazon S3.
- Amazon CloudWatch.
- Snowflake como plataforma analítica.

Esta arquitectura está documentada, pero no desplegada en AWS.

[Documentación y arquitectura AWS](docs/AVANCE_4_AWS.md)

## Ejecución del pipeline

Desde la raíz del proyecto:

```bash
python etl_pipeline.py --execute
```

Requiere PostgreSQL y Snowflake configurados, las dimensiones cargadas y las variables de entorno correspondientes.

La autenticación de Snowflake utiliza OAuth. No deben publicarse credenciales ni archivos de configuración sensibles.

## Limitaciones

- La carga incremental de hechos requiere dimensiones actualizadas.
- Las métricas de viaje no son directamente aditivas por entrega.
- No existe una transacción distribuida única entre PostgreSQL y Snowflake.
- La arquitectura AWS es una propuesta técnica.

## Estado

Pipeline PostgreSQL → Snowflake implementado y probado con los datos actuales.

Proyecto académico FleetLogix M2.
