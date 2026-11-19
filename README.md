# 🚚 FleetLogix | Proyecto M2 — Data Science

**Autora:** Abigail Álvarez  
**Institución:** Henry  
**Proyecto:** Ingeniería de datos aplicada a operaciones logísticas

## 📌 Descripción

FleetLogix es un proyecto de ingeniería de datos orientado al análisis de operaciones logísticas, utilizando PostgreSQL, Python, SQL y Snowflake, junto con una propuesta de arquitectura cloud en AWS.

## 📂 Organización del repositorio

| Carpeta | Contenido |
|---|---|
| [1. Notebooks](1.%20Notebooks/) | Notebooks correspondientes a los cuatro avances |
| [2. Scripts](2.%20Scripts/) | Scripts Python del proceso ETL y consultas SQL |
| [3. Documentación](3.%20Documentaci%C3%B3n/) | Documentación técnica, diagramas y evidencias |

## 📚 Avances del proyecto

### Avance 1 — PostgreSQL y generación de datos

Diseño de seis tablas relacionales y generación de datos sintéticos para operaciones logísticas.

**505.650 registros operacionales** distribuidos entre entregas, viajes, mantenimiento, conductores, vehículos y rutas.

[📓 Ver notebook del Avance 1](1.%20Notebooks/Avance_1_DataGeneration.ipynb)

### Avance 2 — Análisis y optimización SQL

Consultas SQL para analizar operaciones logísticas y evaluación de rendimiento mediante EXPLAIN.

[📓 Ver notebook del Avance 2](1.%20Notebooks/Avance_2_Analisis_Optimizacion_SQL.ipynb)

[💻 Ver consultas SQL](2.%20Scripts/Avance_2_Analisis_SQL.sql)

### Avance 3 — Data Warehouse y ETL

Implementación de un modelo estrella en Snowflake, con una tabla de hechos de 400.000 entregas y seis dimensiones.

Pipeline de extracción, transformación, carga incremental y controles de calidad.

[📓 Ver notebook del Avance 3](1.%20Notebooks/Avance_3_ETL_Fleetlogix.ipynb)

[📄 Ver documentación ETL](3.%20Documentaci%C3%B3n/AVANCE_3.md)

[📊 Ver modelo estrella](3.%20Documentaci%C3%B3n/MODELO_ESTRELLA.md)

### Avance 4 — Arquitectura Cloud AWS

Propuesta de arquitectura utilizando API Gateway, Lambda, RDS PostgreSQL, DynamoDB, S3, CloudWatch y Snowflake.

**Estado:** arquitectura diseñada y documentada, no desplegada en AWS.

[📓 Ver notebook del Avance 4](1.%20Notebooks/Avance_4_CloudArchitecture.ipynb)

[📄 Ver documentación AWS](3.%20Documentaci%C3%B3n/AVANCE_4_AWS.md)

[📑 Ver análisis de arquitectura en PDF](3.%20Documentaci%C3%B3n/AWS_Analisis_Arquitectura.pdf)

## 🛠️ Tecnologías

- Python
- PostgreSQL
- SQL
- Snowflake
- Jupyter Notebook
- AWS (arquitectura propuesta)
- Git y GitHub

## 🖼️ Evidencias

Las capturas de los avances 1, 2 y 3, junto con los diagramas de base de datos y modelo estrella, se encuentran en [3. Documentación](3.%20Documentaci%C3%B3n/).

## ▶️ Ejecución del pipeline

Desde la raíz del repositorio:

```bash
python etl_pipeline.py --execute
