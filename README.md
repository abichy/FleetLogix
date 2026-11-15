# 🚚 FleetLogix — Análisis y Optimización de Operaciones Logísticas

## 📌 Descripción del proyecto

FleetLogix es un proyecto integrador de Data Science desarrollado en el marco del Módulo 2 de Henry.

Su objetivo es analizar datos de operaciones logísticas para identificar oportunidades de mejora en la gestión de flotas, conductores, rutas, viajes, entregas y mantenimiento.

## 🎯 Objetivos

- Analizar el rendimiento de las operaciones logísticas.
- Evaluar la productividad de los conductores.
- Identificar retrasos y problemas operativos.
- Optimizar consultas SQL mediante índices.
- Generar información útil para la toma de decisiones.

## 🛠️ Tecnologías utilizadas

- Python
- PostgreSQL 17
- SQL
- DBeaver
- Jupyter Notebook
- Git y GitHub

## 🗄️ Base de datos

La base de datos `fleetlogix` contiene seis tablas:

| Tabla | Registros |
|---|---:|
| vehicles | 200 |
| drivers | 400 |
| routes | 50 |
| trips | 100.000 |
| deliveries | 400.000 |
| maintenance | 5.000 |
| **Total** | **505.650** |

## 📊 Avance 1 — Generación y validación de datos

- Generación de datos para las seis tablas.
- Carga de registros en PostgreSQL.
- Validación de cantidades y relaciones.
- Creación del diagrama entidad-relación.
- Elaboración de un reporte de calidad de datos.

## ⚡ Avance 2 — Análisis y optimización SQL

- Ejecución de ocho consultas SQL para analizar operaciones logísticas.
- Análisis de flota, conductores, rutas y entregas.
- Evaluación del rendimiento mediante `EXPLAIN ANALYZE`.
- Creación de un índice para optimizar búsquedas de entregas.
- Comparación del tiempo de ejecución antes y después de la optimización.

**Resultado de la optimización:**

| Medición | Tiempo |
|---|---:|
| Antes del índice | 253,653 ms |
| Después del índice | 36,815 ms |
| Mejora aproximada | 85,5 % |

## 📁 Archivos del repositorio

- `Avance_1_DataGeneration_GitHub.ipynb`
- `Avance_1_FleetLogix_Respaldo_GitHub.ipynb`
- `FleetLogix_Diagrama_ER_Avance1.png`
- `reporte_calidad_avance1.json`
- `Avance_2_Analisis_Optimizacion_SQL.ipynb`
- `Avance_2_Analisis_SQL.sql`

## 🚀 Estado del proyecto

- [x] Avance 1 — Generación y validación de datos
- [x] Avance 2 — Análisis y optimización SQL
- [ ] Próximos avances — En desarrollo

---

**Proyecto académico — Henry | Data Science**
