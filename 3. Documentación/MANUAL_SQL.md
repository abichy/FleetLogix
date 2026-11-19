# FleetLogix — Manual de consultas SQL

## Base de datos
PostgreSQL, con seis tablas operacionales:
drivers, vehicles, routes, trips, deliveries y maintenance.

## Consultas de análisis

| N.º | Consulta | Objetivo de negocio |
|---|---|---|
| 1 | Vehículos por tipo | Conocer la composición de la flota |
| 2 | Licencias próximas a vencer | Prevenir incumplimientos |
| 3 | Viajes por estado | Monitorear operaciones |
| 4 | Entregas por ciudad | Planificar recursos |
| 5 | Viajes completados por conductor | Evaluar productividad |
| 6 | Promedio de entregas por conductor | Medir eficiencia |
| 7 | Consumo de combustible por ruta | Identificar ineficiencias |
| 8 | Retrasos por día de la semana | Mejorar la planificación |

## Código SQL

Las ocho consultas completas están disponibles en:
`2. Scripts/Avance_2_Analisis_SQL.sql`

## Optimización

Se utiliza EXPLAIN (ANALYZE, BUFFERS) para analizar
el rendimiento antes y después de crear el índice:

`idx_deliveries_status_scheduled`

El índice combina delivery_status y scheduled_datetime
para favorecer búsquedas filtradas por estado y fecha.

## Validación

La mejora de rendimiento debe calcularse comparando
los tiempos reales de ejecución antes y después.

No se afirma un porcentaje de mejora sin mediciones
verificadas.

## Evidencias

Consultar la carpeta:
`3. Documentación/capturas_avance2/`
